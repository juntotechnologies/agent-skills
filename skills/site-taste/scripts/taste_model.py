"""Typed models for the site-taste data files. Each file loads once and fails on a bad shape."""
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class Scope(Enum):
    ALL = "all"
    PUBLIC_SITE = "public-site"
    CLIENT_SITE = "client-site"
    APP = "app"


class Enforcement(Enum):
    CHECK = "check"
    MANUAL = "manual"


class FromJson:
    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)

    @classmethod
    def many(cls, items: list) -> tuple:
        return tuple(map(cls.from_json, items))


@dataclass(frozen=True)
class Area(FromJson):
    id: str
    title: str
    summary: str


@dataclass(frozen=True)
class FileRef(FromJson):
    site: str
    file: str


@dataclass(frozen=True)
class Evidence(FromJson):
    site: str
    pr: int


@dataclass(frozen=True)
class Command(FromJson):
    run: str
    does: str


@dataclass(frozen=True)
class Principle(FromJson):
    id: str
    area: str
    scope: Scope
    rule: str
    why: str
    fix: str
    enforcement: Enforcement
    checks: tuple[FileRef, ...]
    evidence: tuple[Evidence, ...]

    @classmethod
    def from_json(cls, data: dict):
        fields = dict(data)
        fields["scope"] = Scope(fields["scope"])
        fields["enforcement"] = Enforcement(fields["enforcement"])
        fields["checks"] = FileRef.many(fields["checks"])
        fields["evidence"] = Evidence.many(fields["evidence"])
        return cls(**fields)


@dataclass(frozen=True)
class Site(FromJson):
    id: str
    name: str
    repo: str
    url: str
    kind: Scope
    taste_docs: tuple[str, ...]
    commands: tuple[Command, ...]
    pending_pr: str | None = None

    @classmethod
    def from_json(cls, data: dict):
        fields = dict(data)
        fields["kind"] = Scope(fields["kind"])
        fields["taste_docs"] = tuple(fields["taste_docs"])
        fields["commands"] = Command.many(fields["commands"])
        return cls(**fields)


@dataclass(frozen=True)
class Taste:
    areas: tuple[Area, ...]
    principles: tuple[Principle, ...]
    sites: tuple[Site, ...]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def load_taste(data_dir: Path = DATA_DIR) -> Taste:
    principles = read_json(data_dir / "principles.json")
    sites = read_json(data_dir / "sites.json")
    return Taste(
        areas=Area.many(principles["areas"]),
        principles=Principle.many(principles["principles"]),
        sites=Site.many(sites["sites"]),
    )
