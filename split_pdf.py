#!/usr/bin/env python3
"""Split a large PDF into smaller PDFs with a fixed number of pages each.

Usage:
    python split_pdf.py input.pdf --pages 10
    python split_pdf.py input.pdf -p 25 -o output_dir

Requires: pip install pypdf
"""

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def split_pdf(input_path: Path, pages_per_file: int, output_dir: Path) -> list[Path]:
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Zero-pad part numbers so files sort correctly (part_01, part_02, ...)
    num_parts = (total + pages_per_file - 1) // pages_per_file
    width = max(2, len(str(num_parts)))

    outputs = []
    for part, start in enumerate(range(0, total, pages_per_file), start=1):
        end = min(start + pages_per_file, total)
        writer = PdfWriter()
        for i in range(start, end):
            writer.add_page(reader.pages[i])

        out_path = output_dir / f"{input_path.stem}_part{part:0{width}d}_p{start + 1}-{end}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        outputs.append(out_path)
        print(f"Wrote {out_path} (pages {start + 1}-{end})")

    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Split a PDF into chunks of N pages.")
    parser.add_argument("input", type=Path, help="Path to the PDF to split")
    parser.add_argument("-p", "--pages", type=int, required=True,
                        help="Number of pages per output file")
    parser.add_argument("-o", "--output-dir", type=Path, default=None,
                        help="Output directory (default: <input>_split next to the input)")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1
    if args.pages < 1:
        print("Error: --pages must be at least 1", file=sys.stderr)
        return 1

    output_dir = args.output_dir or args.input.with_name(f"{args.input.stem}_split")
    outputs = split_pdf(args.input, args.pages, output_dir)
    print(f"Done: {len(outputs)} file(s) written to {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
