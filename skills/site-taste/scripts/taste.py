"""Build, check, query and compare the site-taste data. Run: taste.py build | check | rules [--area A] [--id I] | sites [--root DIR]."""
import argparse
import sys
from pathlib import Path

from taste_model import Principle, Taste, load_taste
from taste_render import render_checklist, render_principles, render_sites
from taste_rules import problems
from taste_sites import DEFAULT_ROOTS, failing, report_lines, report_site

REFERENCES = Path(__file__).resolve().parents[1] / "references"
OUTPUTS = {"principles.md": render_principles, "sites.md": render_sites, "checklist.md": render_checklist}


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


def rule_line(item: Principle) -> str:
    return f"{item.id} [{item.enforcement.value}]: {item.rule}"


def rule_detail(item: Principle) -> str:
    return f"{rule_line(item)}\nwhy: {item.why}\nfix: {item.fix}"


def run_rules(args: argparse.Namespace) -> int:
    """1 line per rule, so an agent loads only what it asks for. --id gives the why + fix."""
    items = [item for item in load_taste().principles if args.area in (None, item.area) and args.id in (None, item.id)]
    print("\n".join((rule_detail if args.id else rule_line)(item) for item in items))
    return 0 if items else 1


HANDLERS = {"build": run_build, "check": run_check, "rules": run_rules, "sites": run_sites}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(HANDLERS))
    parser.add_argument("--root", action="append", type=Path, help="Folder that holds site checkouts")
    parser.add_argument("--area", help="rules: only this area, such as layout")
    parser.add_argument("--id", help="rules: one rule, with its why and fix")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return HANDLERS[args.command](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
