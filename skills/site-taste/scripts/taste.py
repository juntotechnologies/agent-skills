"""Build, check and compare the site-taste data. Run: taste.py build | check | sites [--root DIR]."""
import argparse
import sys
from pathlib import Path

from taste_model import Taste, load_taste
from taste_render import render_principles, render_sites
from taste_rules import problems
from taste_sites import DEFAULT_ROOTS, failing, report_lines, report_site

REFERENCES = Path(__file__).resolve().parents[1] / "references"
OUTPUTS = {"principles.md": render_principles, "sites.md": render_sites}


def run_build(args: argparse.Namespace) -> int:
    taste = load_taste()
    REFERENCES.mkdir(exist_ok=True)
    for name, render in OUTPUTS.items():
        (REFERENCES / name).write_text(render(taste))
        print(f"wrote references/{name}")
    return 0


def same_text(path: Path, text: str) -> bool:
    return path.exists() and path.read_text() == text


def stale_outputs(taste: Taste) -> list[str]:
    return [f"stale: references/{name}" for name, render in OUTPUTS.items() if not same_text(REFERENCES / name, render(taste))]


def run_check(args: argparse.Namespace) -> int:
    taste = load_taste()
    found = [*problems(taste), *stale_outputs(taste)]
    print("\n".join(found) if found else "ok: data valid, references up to date")
    return 1 if found else 0


def run_sites(args: argparse.Namespace) -> int:
    taste = load_taste()
    roots = tuple(args.root) if args.root else DEFAULT_ROOTS
    reports = [report_site(taste, site, roots) for site in taste.sites]
    print("\n".join(line for report in reports for line in report_lines(report)))
    return 1 if failing(reports) else 0


HANDLERS = {"build": run_build, "check": run_check, "sites": run_sites}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(HANDLERS))
    parser.add_argument("--root", action="append", type=Path, help="Folder that holds site checkouts")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return HANDLERS[args.command](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
