"""Extract every ```python block from the labs and run it.

Any lab that doesn't execute is a broken promise to the reader, so this runs in CI.
Blocks containing '...' are skipped: they're deliberate exercises for the student.
"""
import pathlib, re, sys, traceback, io, contextlib

ROOT = pathlib.Path(__file__).parent
BLOCK = re.compile(r"```python\n(.*?)```", re.S)

def main() -> int:
    files = sorted(ROOT.glob("labs/*.md")) + sorted(ROOT.glob("*.md"))
    total = skipped = failed = 0
    for f in files:
        blocks = BLOCK.findall(f.read_text())
        for i, code in enumerate(blocks, 1):
            total += 1
            if "..." in code:
                skipped += 1
                print(f"SKIP {f.name} block {i} (student exercise)")
                continue
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(code, f"{f.name}#{i}", "exec"), {"__name__": "__main__"})
                print(f"ok   {f.name} block {i}")
            except Exception:
                failed += 1
                print(f"FAIL {f.name} block {i}")
                traceback.print_exc()
    print(f"\n{total} blocks | {total-skipped-failed} ran | {skipped} skipped | {failed} failed")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
