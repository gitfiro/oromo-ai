"""Document-reset, BOS-conditioned exact summed-NLL evaluator for full checkpoints.

Run --help for the CLI. No dataset normalization, truncation, EOS scoring or
cross-document context. Window policy is versioned in each result.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform


def windows(ids, context, stride):
    """Yield input IDs and first target index; each non-BOS token scored once."""
    if context < 2 or not 1 <= stride < context:
        raise ValueError('Require context >= 2 and 1 <= stride < context')
    end_scored = 1
    while end_scored < len(ids):
        end = min(len(ids), end_scored + stride)
        start = max(0, end - context)
        yield ids[start:end], end_scored - start
        end_scored = end


def summarize(nll, tokens, byte_count, characters, records):
    if not byte_count or not tokens or not math.isfinite(nll):
        raise ValueError('Empty or nonfinite evaluation')
    return dict(nll_sum=nll, scored_tokens=tokens, utf8_bytes=byte_count,
                characters=characters, records=records,
                nll_per_byte=nll / byte_count,
                bits_per_byte=nll / (byte_count * math.log(2)))


def read_records(path):
    rows = []
    with path.open(encoding='utf-8') as stream:
        for line_no, line in enumerate(stream, 1):
            row = json.loads(line)
            text = row.get('text')
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f'Invalid/empty text at line {line_no}')
            rows.append((text, str(row.get('source', 'unspecified'))))
    if not rows:
        raise ValueError('No validation records')
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True, help='Full saved model directory or Hub ID; not a PEFT adapter')
    p.add_argument('--tokenizer', help='Defaults to model; must match checkpoint vocabulary')
    p.add_argument('--revision', help='Hub model revision; use immutable commit when possible')
    p.add_argument('--tokenizer-revision')
    p.add_argument('--data', type=Path, required=True, help='Original text JSONL, never packed token IDs')
    p.add_argument('--expected-sha256', required=True, help='Frozen input-file SHA256')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--context', type=int, default=1024)
    p.add_argument('--stride', type=int, default=512)
    p.add_argument('--device', default='cuda')
    p.add_argument('--dtype', choices=['float32','bfloat16'], default='float32')
    args = p.parse_args()
    if args.output.exists():
        p.error('Output exists; choose a new file to preserve prior results')
    if args.context < 2 or not 1 <= args.stride < args.context:
        p.error('Require 1 <= stride < context')
    digest = hashlib.sha256(args.data.read_bytes()).hexdigest()
    if digest != args.expected_sha256:
        p.error('Input SHA256 does not match the frozen validation file')
    rows = read_records(args.data)
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer or args.model,
        revision=args.tokenizer_revision or args.revision, trust_remote_code=False)
    if tokenizer.bos_token_id is None:
        p.error('This protocol requires a BOS token; do not silently omit the first text token')
    model = AutoModelForCausalLM.from_pretrained(args.model, revision=args.revision,
        torch_dtype=getattr(torch, args.dtype), attn_implementation='eager',
        trust_remote_code=False).to(args.device).eval()
    totals = defaultdict(lambda: [0.0, 0, 0, 0, 0])
    per_record = []
    with torch.inference_mode():
        for index, (text, source) in enumerate(rows):
            encoded = tokenizer.encode(text, add_special_tokens=False)
            if not encoded or tokenizer.unk_token_id in encoded:
                raise ValueError(f'Empty tokenization or unknown token in record {index}')
            if tokenizer.decode(encoded, skip_special_tokens=False,
                                clean_up_tokenization_spaces=False) != text:
                raise ValueError(f'Tokenizer does not round-trip exact text at record {index}; investigate normalization before comparison')
            ids = [tokenizer.bos_token_id] + encoded
            if max(ids) >= model.get_input_embeddings().num_embeddings:
                raise ValueError('Tokenizer IDs exceed model embeddings')
            nll, count = 0.0, 0
            for segment, first_target in windows(ids, args.context, args.stride):
                x = torch.tensor([segment], device=args.device)
                logits = model(input_ids=x, use_cache=False).logits
                # Position t-1 predicts token t. Mask context by slicing targets.
                losses = torch.nn.functional.cross_entropy(
                    logits[0, first_target-1:-1].float(),
                    x[0, first_target:], reduction='none')
                value = losses.double().sum().item()
                if not math.isfinite(value):
                    raise ValueError(f'Nonfinite NLL at record {index}')
                nll += value
                count += len(segment) - first_target
                del logits, losses, x
            if count != len(encoded):
                raise AssertionError('Token scoring coverage mismatch')
            stats = [nll, count, len(text.encode('utf-8')), len(text), 1]
            for key in [('all', ''), ('source', source)]:
                totals[key] = [a+b for a,b in zip(totals[key],stats)]
            per_record.append(dict(index=index, source=source,
                text_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                **summarize(*stats)))
            if (index+1) % 50 == 0:
                print(f'Scored {index+1}/{len(rows)} records', flush=True)
    def local_hashes(location):
        root = Path(location)
        if not root.is_dir():
            return None
        result = {}
        for file in sorted(root.rglob('*')):
            if file.is_file() and file.suffix in {'.json','.safetensors','.bin','.model'}:
                h = hashlib.sha256()
                with file.open('rb') as stream:
                    for chunk in iter(lambda: stream.read(8*1024*1024), b''):
                        h.update(chunk)
                result[str(file.relative_to(root))] = h.hexdigest()
        return result
    report = dict(protocol='document-bos-sliding-v1', model=args.model,
        tokenizer=args.tokenizer or args.model, revision=args.revision,
        resolved_model_revision=getattr(model.config, '_commit_hash', None),
        tokenizer_revision=args.tokenizer_revision or args.revision,
        resolved_tokenizer_revision=tokenizer.init_kwargs.get('_commit_hash'),
        data_sha256=digest, context=args.context, stride=args.stride,
        eos_scored=False, document_context_reset=True, exact_text_roundtrip=True,
        dtype=args.dtype, device=args.device, python=platform.python_version(),
        torch=torch.__version__, transformers=transformers.__version__,
        hardware=torch.cuda.get_device_name() if args.device.startswith('cuda') else 'cpu',
        evaluator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        model_files=local_hashes(args.model), tokenizer_files=local_hashes(args.tokenizer or args.model),
        overall=summarize(*totals[('all','')]),
        per_source={k[1]:summarize(*v) for k,v in totals.items() if k[0]=='source'},
        per_record=per_record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report['overall'], indent=2))


if __name__ == '__main__':
    main()
