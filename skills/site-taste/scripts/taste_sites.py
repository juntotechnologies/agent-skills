"""Compare the site-taste registry with the site checkouts on this machine."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

from taste_model import Site, Taste

POINTER = "site-taste"
DEFAULT_ROOTS = (Path.home() / "GitHub" / "projects", Path.home() / "GitHub" / "sites")


@dataclass(frozen=True)
class SiteReport:
    site: Site
    checkout: Path | None
    problems: tuple[str, ...]


def checkout_for(site: Site, roots: tuple[Path, ...]) -> Path | None:
    candidates = [root / site.repo.split("/")[-1] for root in roots]
    return next((path for path in candidates if (path / ".git").exists()), None)


def expected_files(taste: Taste, site: Site) -> list[str]:
    checks = [ref.file for item in taste.principles for ref in item.checks if ref.site == site.id]
    return sorted({*site.taste_docs, *checks})


def missing_files(root: Path, files: list[str]) -> list[str]:
    return [f"missing file: {name}" for name in files if not (root / name).exists()]


def npm_script_exists(root: Path, name: str) -> bool:
    package = root / "package.json"
    return package.exists() and name in json.loads(package.read_text()).get("scripts", {})


def make_target_exists(root: Path, name: str) -> bool:
    makefile = root / "Makefile"
    return makefile.exists() and re.search(rf"^{re.escape(name)}:", makefile.read_text(), re.MULTILINE) is not None


RUNNERS = {"npm": npm_script_exists, "make": make_target_exists}


def command_exists(root: Path, run: str) -> bool:
    runner, *words = run.split()
    return RUNNERS[runner](root, words[-1])


def missing_commands(root: Path, site: Site) -> list[str]:
    return [f"missing command: {c.run}" for c in site.commands if not command_exists(root, c.run)]


def missing_pointer(root: Path) -> list[str]:
    agents = root / "AGENTS.md"
    found = agents.exists() and POINTER in agents.read_text()
    return [] if found else [f"AGENTS.md does not name the {POINTER} skill"]


def report_site(taste: Taste, site: Site, roots: tuple[Path, ...]) -> SiteReport:
    root = checkout_for(site, roots)
    if root is None:
        return SiteReport(site, None, ())
    found = (*missing_files(root, expected_files(taste, site)), *missing_commands(root, site), *missing_pointer(root))
    return SiteReport(site, root, found)


def is_stale_pending(report: SiteReport) -> bool:
    return bool(report.site.pending_pr and report.checkout and not report.problems)


def state_of(report: SiteReport) -> str:
    if report.checkout is None:
        return "no checkout here"
    if is_stale_pending(report):
        return "ok, but pending_pr is stale: remove it from sites.json"
    return "drift" if report.problems else "ok"


def pending_note(report: SiteReport) -> str:
    return f" (pending {report.site.pending_pr})" if report.site.pending_pr and report.problems else ""


def report_lines(report: SiteReport) -> list[str]:
    head = f"{report.site.id}: {state_of(report)}{pending_note(report)}"
    return [head, *(f"  {line}" for line in report.problems)]


def is_failing(report: SiteReport) -> bool:
    drifted = bool(report.problems) and not report.site.pending_pr
    return drifted or is_stale_pending(report)


def failing(reports: list[SiteReport]) -> list[SiteReport]:
    return [item for item in reports if is_failing(item)]
