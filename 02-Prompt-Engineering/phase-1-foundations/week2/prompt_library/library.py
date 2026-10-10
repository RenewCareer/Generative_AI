"""Prompt templates as versioned, testable files.

Why files and not strings in code?
- Prompts change more often than code; reviewing a .toml diff is easy.
- Every template carries its own tests, so a change can be checked before it ships.
- `version` + git history = you can always answer "which prompt produced this?"

Template variables use `${name}` (string.Template), so JSON braces in prompts
never need escaping — a classic `str.format` footgun.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

TEMPLATES_DIR = Path(__file__).parent / "templates"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass
class TemplateTest:
    name: str
    vars: dict[str, str]
    checks: list[dict]


@dataclass
class PromptTemplate:
    name: str
    version: str
    category: str
    description: str
    variables: list[str]
    instructions: str
    template: str
    tests: list[TemplateTest] = field(default_factory=list)
    changelog: list[str] = field(default_factory=list)
    source: Path | None = None

    @property
    def id(self) -> str:
        return f"{self.name}@{self.version}"

    def render(self, **vars: str) -> str:
        missing = set(self.variables) - set(vars)
        extra = set(vars) - set(self.variables)
        if missing or extra:
            raise ValueError(f"{self.id}: missing vars {sorted(missing)}, unexpected {sorted(extra)}")
        return Template(self.template).substitute(vars)

    def placeholders(self) -> set[str]:
        found = set()
        for m in Template.pattern.finditer(self.template):
            name = m.group("named") or m.group("braced")
            if name:
                found.add(name)
        return found

    def validate(self) -> list[str]:
        """Static problems that need no API call. Returns a list of issues."""
        issues = []
        if not SEMVER.match(self.version):
            issues.append(f"version {self.version!r} is not semver (x.y.z)")
        if self.placeholders() != set(self.variables):
            issues.append(f"placeholders {sorted(self.placeholders())} != "
                          f"declared variables {sorted(self.variables)}")
        if not self.tests:
            issues.append("has no tests")
        for t in self.tests:
            if set(t.vars) != set(self.variables):
                issues.append(f"test {t.name!r} vars {sorted(t.vars)} != {sorted(self.variables)}")
            if not t.checks:
                issues.append(f"test {t.name!r} has no checks")
        return issues


def load_template(path: Path) -> PromptTemplate:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    tests = [TemplateTest(t["name"], t.get("vars", {}), t.get("checks", []))
             for t in data.pop("tests", [])]
    return PromptTemplate(**data, tests=tests, source=path)


def load_library(directory: Path = TEMPLATES_DIR) -> dict[str, PromptTemplate]:
    lib: dict[str, PromptTemplate] = {}
    for path in sorted(directory.glob("*.toml")):
        t = load_template(path)
        if t.name in lib:
            raise ValueError(f"Duplicate template name {t.name!r} in {path.name}")
        lib[t.name] = t
    return lib
