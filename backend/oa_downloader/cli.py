import argparse
import sys
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="oa_downloader")
    p.add_argument("--input-file", type=str, default=None)
    p.add_argument("--pasted-text", type=str, default=None)
    p.add_argument("--output-root", type=str, default=r"D:\\Papers")

    p.add_argument("--delay-seconds", type=float, default=1.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout-seconds", type=int, default=30)
    p.add_argument("--proxy", type=str, default=None)

    p.add_argument("--resume", action="store_true")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if not args.input_file and not (args.pasted_text and args.pasted_text.strip()):
        print("ERROR: Provide --input-file or --pasted-text", file=sys.stderr)
        return 2

    run_pipeline(
        input_file=args.input_file,
        pasted_text=args.pasted_text,
        output_root=args.output_root,
        delay_seconds=args.delay_seconds,
        retries=args.retries,
        timeout_seconds=args.timeout_seconds,
        proxy=args.proxy,
        resume=args.resume,
    )

    return 0
