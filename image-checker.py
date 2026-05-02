"""
image-checker.py
================
Background task: validates image paths in Hugo content .md files
and auto-fixes broken links by searching static/images/.

Runs every 15 minutes via Windows Task Scheduler.

What it does:
  1. Reads every .md in content/posts/
  2. Finds all image links  ![alt](/images/path/file.ext)
  3. Checks if static/images/path/file.ext exists
  4. If NOT found, searches all of static/images/ for a file with
     the same name and fixes the path
  5. Logs every fix to image-checker.log
"""

import os, re, sys, shutil
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────
HUGO_SITE       = r"C:\Users\DELL\karimabdelazizblog"
CONTENT_POSTS   = os.path.join(HUGO_SITE, "content", "posts")
STATIC_IMAGES   = os.path.join(HUGO_SITE, "static", "images")
LOG_FILE        = os.path.join(HUGO_SITE, "image-checker.log")
# ───────────────────────────────────────────────────────────────

IMAGE_LINK = re.compile(
    r'(!\[[^\]]*\])\((/images/[^)]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp))\)',
    re.IGNORECASE
)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def build_index(root):
    """Build filename -> [full_paths] index of all files under root."""
    idx = {}
    for dirpath, _, files in os.walk(root):
        for fname in files:
            key = fname.lower()
            idx.setdefault(key, []).append(os.path.join(dirpath, fname))
    return idx

def url_to_static(url_path):
    """Convert /images/a/b/c.png -> static/images/a/b/c.png abs path."""
    relative = url_path.lstrip('/')          # images/a/b/c.png
    return os.path.join(HUGO_SITE, "static", relative)

def static_to_url(abs_path):
    """Convert abs static path -> /images/... URL."""
    rel = os.path.relpath(abs_path, os.path.join(HUGO_SITE, "static"))
    return '/' + rel.replace('\\', '/')

def fix_md(md_path, idx):
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log("WARN Cannot read %s: %s" % (md_path, e))
        return 0

    original = content
    fixes = 0

    def replacer(m):
        nonlocal fixes
        alt_part = m.group(1)   # ![alt]
        url      = m.group(2)   # /images/.../file.ext

        static_path = url_to_static(url)
        if os.path.isfile(static_path):
            return m.group(0)   # OK — nothing to fix

        # File missing — search by filename
        filename = os.path.basename(url).lower()
        candidates = idx.get(filename, [])

        if not candidates:
            log("MISSING (no match found): %s  in  %s" % (url, os.path.basename(md_path)))
            return m.group(0)

        # Pick the best candidate (prefer one with matching parent folder name)
        best = candidates[0]
        if len(candidates) > 1:
            post_slug = os.path.basename(os.path.dirname(md_path)).lower()
            for c in candidates:
                if post_slug in c.lower():
                    best = c
                    break

        new_url = static_to_url(best)
        log("FIXED  %s -> %s  in  %s" % (url, new_url, os.path.basename(md_path)))
        fixes += 1
        return "%s(%s)" % (alt_part, new_url)

    content = IMAGE_LINK.sub(replacer, content)

    if fixes:
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            log("WARN Cannot write %s: %s" % (md_path, e))
            return 0

    return fixes

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.isdir(CONTENT_POSTS):
        log("ERROR content/posts not found: " + CONTENT_POSTS)
        sys.exit(1)

    log("--- image-checker run started ---")
    idx   = build_index(STATIC_IMAGES)
    total = 0

    for root, dirs, files in os.walk(CONTENT_POSTS):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
        for fname in sorted(files):
            if fname.lower().endswith('.md'):
                fixed = fix_md(os.path.join(root, fname), idx)
                total += fixed

    if total:
        log("Fixed %d broken image link(s). Run Hugo to rebuild." % total)
    else:
        log("All image links OK.")
    log("--- image-checker run done ---")
