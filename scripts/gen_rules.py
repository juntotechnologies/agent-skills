"""Write global/AGENTS.md from rules/rules.json. Run: gen_rules.py build | check."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'rules/rules.json'
TARGET = ROOT / 'global/AGENTS.md'


def load_registry(path=REGISTRY):
    return json.loads(path.read_text())


def is_prose(rule):
    return rule['enforcer'] is None


def section_lines(registry, section):
    texts = [rule['text'] for rule in registry['rules'] if rule['section'] == section and is_prose(rule)]
    return [f'## {section}', *texts, ''] if texts else []


def render(registry):
    body = [line for section in registry['sections'] for line in section_lines(registry, section)]
    return '\n'.join([f'# {registry["title"]}', '', *body, registry['footer'], ''])


def main(argv):
    text = render(load_registry())
    if argv[1:] == ['build']:
        TARGET.write_text(text)
        return 0
    if TARGET.read_text() == text:
        return 0
    print('stale: global/AGENTS.md; run scripts/gen_rules.py build')
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
