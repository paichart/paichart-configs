#!/usr/bin/env python3
"""Repository rules for paichart-configs (run by .github/workflows/checks.yml; runs locally too: python3 .github/scripts/check-tree.py).

1. STRUCTURE  — only the known top-level entries exist.
2. FORBIDDEN  — no Terraform state/plans/variables, no credential or key files.
3. SIZE       — no file over 256 KB (configs of record are small; a big file is usually a mistake).
4. ADDRESSES  — every IPv4 literal is private (RFC 1918), loopback, link-local, documentation (RFC 5737), a mask/wildcard,
                or listed in .github/address-allowlist.txt (synthetic lab addresses such as router IDs). A real public address
                here would publish someone's infrastructure.
"""
import ipaddress, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOP = {'.github', '.gitignore', '.gitleaks.toml', 'CODEOWNERS', 'LICENSE', 'README.md', 'k8s', 'terraform', 'network', 'usecases'}
FORBIDDEN = [r'\.tfstate', r'\.tfplan$', r'\.tfvars', r'(^|/)\.env$', r'\.env$', r'kubeconfig', r'\.pem$', r'\.key$',
             r'(^|/)hosts\.yaml$', r'(^|/)id_(rsa|ed25519|ecdsa)']
MAX = 256 * 1024
IPV4 = re.compile(r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])')
DOC_NETS = [ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]


def tracked():
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout.decode()
    return [p for p in out.split('\0') if p]


def allowed_ip(s, allow):
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        return True  # not an address (e.g. a version-like string)
    if s in allow or ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified:
        return True
    if any(ip in n for n in DOC_NETS):
        return True
    first = int(s.split('.')[0])
    return first == 255 or s.startswith('0.')   # masks and wildcards


def main():
    allow_path = os.path.join(ROOT, '.github', 'address-allowlist.txt')
    allow = set()
    if os.path.exists(allow_path):
        allow = {l.split('#')[0].strip() for l in open(allow_path) if l.split('#')[0].strip()}
    errs = []
    for p in tracked():
        top = p.split('/')[0]
        if top not in TOP:
            errs.append(f'STRUCTURE {p}: top-level entry not allowed ({sorted(TOP)})')
        if any(re.search(f, p) for f in FORBIDDEN):
            errs.append(f'FORBIDDEN {p}: state, variables, credential or key file')
        full = os.path.join(ROOT, p)
        if os.path.getsize(full) > MAX:
            errs.append(f'SIZE {p}: over {MAX // 1024} KB')
            continue
        if p.startswith('.github/'):
            continue
        try:
            text = open(full, encoding='utf-8').read()
        except UnicodeDecodeError:
            errs.append(f'BINARY {p}: configs of record are text')
            continue
        for n, line in enumerate(text.split('\n'), 1):
            for m in IPV4.finditer(line):
                if not allowed_ip(m.group(1), allow):
                    errs.append(f'ADDRESS {p}:{n}: {m.group(1)} is a public address (allow a synthetic one in .github/address-allowlist.txt)')
    for e in errs:
        print(e)
    print('ok' if not errs else f'{len(errs)} problem(s)')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
