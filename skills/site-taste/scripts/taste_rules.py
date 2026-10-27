"""Pure checks on the site-taste data. Each check returns a list of problem lines."""
import re
from collections import Counter

from taste_model import Enforcement, Principle, Scope, Site, Taste

RULE_WORDS = 20
TEXT_WORDS = 25
SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
COMMAND_PREFIXES = ("npm run ", "make ")


def sentences(text: str) -> list[str]:
    return [part for part in SENTENCE_END.split(text.strip()) if part]


def long_sentences(label: str, text: str, limit: int) -> list[str]:
    return [f"{label}: {len(part.split())} words, limit {limit}: {part}" for part in sentences(text) if len(part.split()) > limit]


def principle_sentence_problems(item: Principle) -> list[str]:
    return [
        *long_sentences(f"{item.id} rule", item.rule, RULE_WORDS),
        *long_sentences(f"{item.id} why", item.why, TEXT_WORDS),
        *long_sentences(f"{item.id} fix", item.fix, TEXT_WORDS),
    ]


def sentence_problems(taste: Taste) -> list[str]:
    return [line for item in taste.principles for line in principle_sentence_problems(item)]


def duplicates(kind: str, ids: list[str]) -> list[str]:
    return [f"duplicate {kind} id: {name}" for name, count in Counter(ids).items() if count > 1]


def slug_problems(kind: str, items: tuple) -> list[str]:
    return [f"bad {kind} id: {item.id}" for item in items if not SLUG.match(item.id)]


def id_problems(taste: Taste) -> list[str]:
    groups = {"area": taste.areas, "principle": taste.principles, "site": taste.sites}
    return [
        line
        for kind, items in groups.items()
        for line in (*duplicates(kind, [item.id for item in items]), *slug_problems(kind, items))
    ]


def unknown_area(item: Principle, areas: set[str]) -> list[str]:
    return [] if item.area in areas else [f"{item.id}: unknown area {item.area}"]


def unknown_sites(item: Principle, sites: set[str]) -> list[str]:
    refs = (*item.checks, *item.evidence)
    return [f"{item.id}: unknown site {ref.site}" for ref in refs if ref.site not in sites]


def reference_problems(taste: Taste) -> list[str]:
    areas = {item.id for item in taste.areas}
    sites = {item.id for item in taste.sites}
    return [
        line
        for item in taste.principles
        for line in (*unknown_area(item, areas), *unknown_sites(item, sites))
    ]


def enforcement_problem(item: Principle) -> list[str]:
    if (item.enforcement is Enforcement.CHECK) == bool(item.checks):
        return []
    return [f"{item.id}: {item.enforcement.value} enforcement with {len(item.checks)} check files"]


def enforcement_problems(taste: Taste) -> list[str]:
    return [line for item in taste.principles for line in enforcement_problem(item)]


def kind_problems(site: Site) -> list[str]:
    return [f"{site.id}: kind must not be all"] if site.kind is Scope.ALL else []


def command_problems(site: Site) -> list[str]:
    bad = [command.run for command in site.commands if not command.run.startswith(COMMAND_PREFIXES)]
    return [f"{site.id}: command must start with npm run or make: {run}" for run in bad]


def site_problems(taste: Taste) -> list[str]:
    return [line for site in taste.sites for line in (*kind_problems(site), *command_problems(site))]


def problems(taste: Taste) -> list[str]:
    checks = (id_problems, reference_problems, enforcement_problems, site_problems, sentence_problems)
    return [line for check in checks for line in check(taste)]
