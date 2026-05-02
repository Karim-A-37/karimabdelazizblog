"""
fix-frontmatter.py  (v2 - safe)
================================
Only fixes files that have the EXACT broken pattern:
  ---
  FM block 1 (good YAML)
  ---
  ---
  FM block 2 (broken run-on or duplicate YAML)
  ---
  body content...

Never touches files that have a single clean frontmatter block.
"""

import os, re

CONTENT_POSTS = r"C:\Users\DELL\karimabdelazizblog\content\posts"

# Matches ONLY the specific broken pattern: two back-to-back --- blocks
# Group 1 = first FM content (clean YAML)
# Group 2 = second FM content (broken/duplicate)
# Group 3 = actual post body
BROKEN_PATTERN = re.compile(
    r'\A---[ \t]*\r?\n'      # opening ---
    r'(.*?)\r?\n'            # FM1 (non-greedy)
    r'---[ \t]*\r?\n'        # closing ---
    r'[ \t]*\r?\n?'          # optional blank line
    r'---[ \t]*\r?\n'        # SECOND opening ---  <-- the telltale sign
    r'(.*?)\r?\n'            # FM2 content
    r'---[ \t]*\r?\n'        # SECOND closing ---
    r'(.*)',                  # rest of the body
    re.DOTALL
)

def parse_clean_yaml(text):
    """Parse simple key: value YAML, returns dict. Handles list items."""
    result = {}
    current_key = None
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        # List item
        if re.match(r'^\s*-\s+', line):
            item = re.sub(r'^\s*-\s+', '', line).strip().strip('"\'')
            if current_key:
                result.setdefault(current_key, [])
                if isinstance(result[current_key], str):
                    result[current_key] = [result[current_key]]
                result[current_key].append(item)
            continue
        # Key: value
        m = re.match(r'^(\w+):\s*(.*)', line)
        if m:
            current_key = m.group(1)
            val = m.group(2).strip().strip('"\'')
            result[current_key] = val if val else None
    return result

def extract_tags(text):
    """Pull tags from a broken second FM block (may be run-on or multiline)."""
    tags = []
    # Multiline: find tags: key then collect - items
    lines = text.splitlines()
    in_tags = False
    for line in lines:
        line = line.strip()
        if re.match(r'^tags\s*:', line):
            in_tags = True
            # tags: value on same line?
            after = re.sub(r'^tags\s*:\s*', '', line)
            if after:
                tags.append(after.strip().strip('"\''))
            continue
        if in_tags:
            if re.match(r'^-\s+', line):
                tags.append(line[1:].strip().strip('"\''))
            elif re.match(r'^\w+\s*:', line):
                in_tags = False  # another key started
    return tags

def build_frontmatter(fm, tags):
    lines = ['---']
    for key in ['title', 'date', 'slug', 'draft']:
        val = fm.get(key)
        if val is not None:
            # Quote strings with spaces
            if isinstance(val, str) and ' ' in val and not val.startswith('"'):
                val = '"%s"' % val
            lines.append('%s: %s' % (key, val))
    if tags:
        lines.append('tags:')
        for t in tags:
            lines.append('  - %s' % t)
    lines.append('---')
    return '\n'.join(lines)

def fix_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print('ERROR reading %s: %s' % (os.path.basename(path), e))
        return False

    m = BROKEN_PATTERN.match(content)
    if not m:
        return False  # File is clean — do not touch it

    fm1_raw = m.group(1)
    fm2_raw = m.group(2)
    body    = m.group(3).lstrip('\r\n')

    fm   = parse_clean_yaml(fm1_raw)
    tags = fm.pop('tags', None)  # tags from FM1 if any

    # Prefer tags from FM2 (usually where they ended up)
    fm2_tags = extract_tags(fm2_raw)
    if fm2_tags:
        tags = fm2_tags
    elif tags and isinstance(tags, list):
        pass  # keep FM1 tags

    if isinstance(tags, str):
        tags = [tags] if tags else []
    if not tags:
        tags = []

    clean_fm      = build_frontmatter(fm, tags)
    new_content   = clean_fm + '\n\n' + body

    if new_content != content:
        try:
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
        except Exception as e:
            print('ERROR writing %s: %s' % (os.path.basename(path), e))
            return False
        print('FIXED  %s' % os.path.basename(path))
        return True

    return False

# ── Main ────────────────────────────────────────────────────────
if __name__ == '__main__':
    fixed = 0
    for root, dirs, files in os.walk(CONTENT_POSTS):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
        for fname in sorted(files):
            if fname.lower().endswith('.md'):
                if fix_file(os.path.join(root, fname)):
                    fixed += 1

    if fixed:
        print('Done. Fixed %d file(s).' % fixed)
    else:
        print('All frontmatter OK — no changes made.')
