#!/usr/bin/env python3
"""Variant twins in usecases/ (run by .github/workflows/checks.yml; runs locally too).

A use case may ship two variants of one program: git-only/ (every device read from its Git file) and git-live/ (the same
plus reads of the running devices). They must say the same thing except where they read from. This check removes, from
both requirements.md files, every fenced ``## Device sources`` block and the ``## Connection surfaces`` section, and from
both topology.json files the ``name`` and ``readOnlyServices`` keys; what remains must be identical.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOCK = re.compile(r'```\n## Device sources\n.*?```\n', re.S)
CONN = re.compile(r'^## Connection surfaces\n.*?(?=^## |\Z)', re.S | re.M)


def spec(p):
    with open(p, encoding='utf-8') as f:
        return CONN.sub('', BLOCK.sub('```\n## Device sources\n```\n', f.read()))


def topo(p):
    with open(p, encoding='utf-8') as f:
        t = json.load(f)
    t.pop('name', None); t.pop('readOnlyServices', None)
    return t


def main():
    base = os.path.join(ROOT, 'usecases')
    errs, pairs = [], 0
    for d in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        a, b = os.path.join(base, d, 'git-only'), os.path.join(base, d, 'git-live')
        if not (os.path.isdir(a) and os.path.isdir(b)):
            continue
        pairs += 1
        if spec(os.path.join(a, 'requirements.md')) != spec(os.path.join(b, 'requirements.md')):
            errs.append(f'{d}: requirements.md differs outside Device sources / Connection surfaces')
        if topo(os.path.join(a, 'topology.json')) != topo(os.path.join(b, 'topology.json')):
            errs.append(f'{d}: topology.json differs outside name / readOnlyServices')
    for e in errs:
        print('TWIN', e)
    print(f'{pairs} twin pair(s); ' + ('ok' if not errs else f'{len(errs)} difference(s)'))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
