"""
fix-frontmatter.py
==================
Fixes duplicated/broken YAML frontmatter in Hugo .md posts.

The problem: some files have two --- blocks like:
  ---
  title: "..."
  date: ...
  slug: "..."
  draft: false
  ---
  ---
  title: "..." date: ... slug: "..." draft: false tags:
  - ejpt
  - recon
  ---

This script merges them into one clean frontmatter block.
"""

import os, re, sys

CONTENT_POSTS = r"C:\Users\DELL\karimabdelazizblog\content\posts"

def parse_inline_yaml_line(line):
    """Parse a run-on YAML line like: title: "foo" date: bar tags:"""
    fields = {}
    # Extract key: value pairs (value ends at next key or end)
    pattern = re.compile(r'(\w+):\s*("(?:[^"\\]|\\.)*"|[^:]+?)(?=\s+\w+:|$)')
    for m in pattern.finditer(line):
        key = m.group(1).strip()
        val = m.group(2).strip().strip('"')
        if val:
            fields[key] = val
    return fields

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on --- markers
    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    # parts[0] = before first ---, parts[1] = first FM, parts[2] = body or second FM, etc.

    if len(parts) < 3:
        return False  # Normal single-block file, skip

    first_fm_raw  = parts[1].strip()
    rest          = parts[2:]  # everything after first closing ---

    # Check if there's a second frontmatter block at the start of rest
    # (i.e., rest starts with a --- block immediately)
    second_fm_raw = None
    body_parts    = rest

    if len(rest) >= 2 and rest[0].strip() == '':
        # Possibly: empty gap then second FM then ---
        # Actually re.split gives us: ['', ' second_fm ', ' body ']
        # if the content is: \n---\n second_fm \n---\n body
        pass

    # Detect duplicate FM: if rest[0] has inline YAML (everything on one line)
    # or if there's another FM-like block
    joined_rest = '---'.join(rest)

    # Pattern: second --- block exists right after body starts
    double_fm = re.match(r'^\s*\n?---\s*\n(.*?)\n---\s*\n(.*)', joined_rest, re.DOTALL)
    if not double_fm:
        # Maybe the rest itself starts with a broken FM (no leading ---)
        # Check if rest[0] looks like run-on yaml
        rest0 = rest[0].strip() if rest else ''
        if not rest0.startswith('\n') and re.search(r'\w+:\s*\S', rest0):
            second_fm_raw = rest0
            body_parts = rest[1:]
        else:
            return False  # No duplicate found
    else:
        second_fm_raw = double_fm.group(1)
        actual_body   = double_fm.group(2)
        body_parts    = [actual_body]

    # Parse first FM as proper YAML
    fm = {}
    for line in first_fm_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('-'):
            # List item for previous key
            if last_key:
                fm.setdefault(last_key, [])
                if isinstance(fm[last_key], str):
                    fm[last_key] = [fm[last_key]]
                fm[last_key].append(line[1:].strip())
            continue
        m = re.match(r'^(\w+):\s*(.*)', line)
        if m:
            last_key = m.group(1)
            val = m.group(2).strip().strip('"')
            fm[last_key] = val if val else None
        else:
            last_key = None

    last_key = None

    # Parse second FM (may be run-on or multi-line)
    if second_fm_raw:
        # Try multi-line first
        current_key = None
        for line in second_fm_raw.splitlines():
            line2 = line.strip()
            if not line2:
                continue
            if line2.startswith('-'):
                if current_key:
                    fm.setdefault(current_key, [])
                    if isinstance(fm[current_key], str):
                        fm[current_key] = [fm[current_key]]
                    fm[current_key].append(line2[1:].strip())
                continue
            m = re.match(r'^(\w+):\s*(.*)', line2)
            if m:
                current_key = m.group(1)
                val = m.group(2).strip().strip('"')
                if val:
                    fm[current_key] = val
                # else keep existing or set None; don't overwrite if already set

    # Build clean frontmatter
    lines = ['---']
    for key in ['title', 'date', 'slug', 'draft']:
        if key in fm and fm[key] is not None:
            val = fm[key]
            if isinstance(val, str) and ' ' in val and not val.startswith('"'):
                val = '"%s"' % val
            lines.append('%s: %s' % (key, val))

    # Tags
    tags = fm.get('tags', fm.get('tag', []))
    if isinstance(tags, str) and tags:
        tags = [tags]
    if isinstance(tags, list) and tags:
        lines.append('tags:')
        for t in tags:
            lines.append('  - %s' % t)

    lines.append('---')
    clean_fm = '\n'.join(lines)

    # Reconstruct body
    body = ''.join(body_parts).lstrip('\n')

    new_content = clean_fm + '\n\n' + body

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('FIXED  ' + os.path.basename(path))
        return True

    return False

# ── Main ──────────────────────────────────────────────────────
fixed = 0
for root, dirs, files in os.walk(CONTENT_POSTS):
    dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
    for fname in files:
        if fname.lower().endswith('.md'):
            if fix_file(os.path.join(root, fname)):
                fixed += 1

print('Done. Fixed %d file(s).' % fixed)
