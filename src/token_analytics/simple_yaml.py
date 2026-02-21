from __future__ import annotations


def load_simple_yaml(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(0, root)]
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(raw) - len(raw.lstrip(' '))
        key, val = [x.strip() for x in line.strip().split(':', 1)]
        while stack and indent < stack[-1][0]:
            stack.pop()
        cur = stack[-1][1]
        if val == '':
            cur[key] = {}
            stack.append((indent + 2, cur[key]))
        else:
            cur[key] = _parse_scalar(val)
    return root


def _parse_scalar(v: str):
    if v.lower() in {'true', 'false'}:
        return v.lower() == 'true'
    try:
        if '.' in v:
            return float(v)
        return int(v)
    except ValueError:
        return v.strip('"').strip("'")
