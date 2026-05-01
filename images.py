"""
images.py  -  Obsidian → Hugo image processor (v4)
====================================================

Handles two jobs in one pass:

  JOB 1 — Obsidian vault (primary):
    Scans <obsidian_posts_dir> for .md files containing ![[image.png]] embeds.
    Finds the image in a sibling folder, copies it to static/images/<slug>/,
    and rewrites the embed to a proper Hugo Markdown link.

  JOB 2 — Hugo content rescue (secondary, optional):
    Scans <hugo_content_posts_dir> for image files that ended up inside
    content/ (wrong place — Hugo can't serve them). Moves them to
    static/images/<slug>/ and fixes the .md links in content/.

  Both jobs slugify the subfolder path so posts in different subfolders
  never collide and all URLs are clean (no spaces, all hyphens).

Usage:
    python images.py <obsidian_posts_dir> <static_images_base>
    python images.py <obsidian_posts_dir> <static_images_base> <hugo_content_posts_dir>

Called automatically by BlogWatcher.ps1 and Fix-Blog.ps1.
"""

import os
import re
import shutil
import sys
import tempfile

# ─── Argument validation ───────────────────────────────────────────────────────
if len(sys.argv) < 3:
    print("ERROR: Expected: images.py <obsidian_posts_dir> <static_images_base> [hugo_content_posts_dir]")
    sys.exit(1)

obsidian_posts_dir   = sys.argv[1]   # Obsidian vault posts folder
static_images_base   = sys.argv[2]   # Hugo static/images/
hugo_content_posts   = sys.argv[3] if len(sys.argv) > 3 else None  # Hugo content/posts/ (optional)

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.tif'}

# Obsidian embed: ![[image.png]] or [[image.png]]
OBSIDIAN_EMBED = re.compile(
    r'!?\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\]\]',
    re.IGNORECASE
)

# Already-converted Hugo link: ![alt](/images/...)
HUGO_IMG_LINK = re.compile(
    r'!\[[^\]]*\]\(/images/[^)]+\)',
    re.IGNORECASE
)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def slugify(text):
    """Lowercase hyphen slug — URL-safe, no spaces."""
    text = text.strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def slug_path(root_dir, md_filepath, post_name):
    """
    Build the URL slug for this post using its subfolder path.
      root_dir    = C:/Vault/posts
      md_filepath = C:/Vault/posts/ejpt/Day 0/My Note.md
      post_name   = My Note
      → returns   = ejpt/day-0/my-note
    """
    rel_dir = os.path.relpath(os.path.dirname(md_filepath), root_dir)
    parts   = rel_dir.replace('\\', '/').split('/')
    parts   = [slugify(p) for p in parts if p and p != '.']
    parts.append(slugify(post_name))
    return '/'.join(parts)


def find_image_near_md(image_basename, md_dir):
    """Search for image_basename relative to a .md file directory."""
    # 1. Same directory
    c = os.path.join(md_dir, image_basename)
    if os.path.isfile(c):
        return c
    try:
        entries = list(os.scandir(md_dir))
    except PermissionError:
        return None
    # 2. Sibling folders with 'images' in name
    for e in entries:
        if e.is_dir() and 'images' in e.name.lower():
            c = os.path.join(e.path, image_basename)
            if os.path.isfile(c):
                return c
    # 3. Any sibling subfolder (broad fallback)
    for e in entries:
        if e.is_dir():
            c = os.path.join(e.path, image_basename)
            if os.path.isfile(c):
                return c
    return None


def safe_write(filepath, content):
    """Atomic write via temp file — avoids 'Bad file descriptor' from Obsidian lock."""
    try:
        fd, tmp = tempfile.mkstemp(suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            shutil.move(tmp, filepath)
            return True
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass
            raise
    except Exception as e:
        print(f"  WARN  Cannot write {filepath}: {e}")
        return False


def fix_spaces_in_hugo_links(content):
    """Replace spaces in /images/... URLs with hyphens."""
    def _fix(m):
        link = m.group(0)
        inner = re.search(r'\(/images/([^)]+)\)', link)
        if not inner:
            return link
        parts = inner.group(1).split('/')
        fixed = []
        for p in parts:
            base, sep, ext = p.rpartition('.')
            if sep:
                fixed.append(slugify(base) + '.' + ext.lower())
            else:
                fixed.append(slugify(p) if p else p)
        return link.replace(inner.group(0), '(/images/' + '/'.join(fixed) + ')')
    return HUGO_IMG_LINK.sub(_fix, content)


# ─── Counters ─────────────────────────────────────────────────────────────────
processed = 0
warnings  = 0


# ══════════════════════════════════════════════════════════════════════════════
# JOB 1 — Process Obsidian vault posts
# ══════════════════════════════════════════════════════════════════════════════
if os.path.isdir(obsidian_posts_dir):
    print(f"\n[JOB 1] Scanning Obsidian posts: {obsidian_posts_dir}")

    for root, dirs, files in os.walk(obsidian_posts_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        for filename in sorted(files):
            if not filename.lower().endswith('.md'):
                continue

            post_name = os.path.splitext(filename)[0]
            filepath  = os.path.join(root, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  WARN  Cannot read {filepath}: {e}")
                warnings += 1
                continue

            matches = OBSIDIAN_EMBED.findall(content)
            if not matches:
                continue

            url_slug     = slug_path(obsidian_posts_dir, filepath, post_name)
            dest_img_dir = os.path.join(static_images_base, *url_slug.split('/'))
            os.makedirs(dest_img_dir, exist_ok=True)

            rel_path = os.path.relpath(filepath, obsidian_posts_dir)
            print(f"\n  [{rel_path}]  →  /images/{url_slug}/")

            changed = False
            for image_ref, _ext in matches:
                image_basename   = os.path.basename(image_ref)
                name_no_ext, ext = os.path.splitext(image_basename)
                slug_img_name    = slugify(name_no_ext) + ext.lower()
                url_path         = f"/images/{url_slug}/{slug_img_name}"
                md_link          = f"![{name_no_ext}]({url_path})"

                for pat in [f"![[{image_ref}]]", f"[[{image_ref}]]"]:
                    if pat in content:
                        content = content.replace(pat, md_link)
                        changed = True

                src = find_image_near_md(image_basename, root)
                dst = os.path.join(dest_img_dir, slug_img_name)
                if src:
                    try:
                        shutil.copy2(src, dst)
                        print(f"    OK   {slug_img_name}  ← {os.path.relpath(src, obsidian_posts_dir)}")
                    except Exception as e:
                        print(f"    WARN  Copy failed {slug_img_name}: {e}")
                        warnings += 1
                else:
                    print(f"    WARN  Not found: {image_basename}")
                    warnings += 1

            # Fix any already-written links that still have spaces
            fixed = fix_spaces_in_hugo_links(content)
            if fixed != content:
                content = fixed
                changed = True

            if changed:
                if safe_write(filepath, content):
                    processed += 1
                    print(f"    SAVED  {filename}")
                else:
                    warnings += 1
else:
    print(f"\n[JOB 1] SKIP — Obsidian posts dir not found: {obsidian_posts_dir}")


# ══════════════════════════════════════════════════════════════════════════════
# JOB 2 — Rescue images stuck inside Hugo content/posts/
#          (they should be in static/images/ not content/)
# ══════════════════════════════════════════════════════════════════════════════
if hugo_content_posts and os.path.isdir(hugo_content_posts):
    print(f"\n[JOB 2] Rescuing images from Hugo content: {hugo_content_posts}")

    for root, dirs, files in os.walk(hugo_content_posts):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        # --- Move any image files directly in this dir to static/images ---
        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                # Figure out which post this image belongs to by looking for a .md sibling
                md_siblings = [f for f in os.listdir(root) if f.lower().endswith('.md')]
                if md_siblings:
                    post_name    = os.path.splitext(md_siblings[0])[0]
                    url_slug     = slug_path(hugo_content_posts, os.path.join(root, md_siblings[0]), post_name)
                else:
                    # Use the directory name as slug
                    rel          = os.path.relpath(root, hugo_content_posts)
                    url_slug     = '/'.join(slugify(p) for p in rel.replace('\\', '/').split('/') if p and p != '.')

                dest_img_dir = os.path.join(static_images_base, *url_slug.split('/'))
                os.makedirs(dest_img_dir, exist_ok=True)

                name_no_ext, ext_orig = os.path.splitext(filename)
                slug_img_name = slugify(name_no_ext) + ext_orig.lower()
                src = os.path.join(root, filename)
                dst = os.path.join(dest_img_dir, slug_img_name)

                try:
                    shutil.copy2(src, dst)
                    print(f"    RESCUED  {filename}  →  static/images/{url_slug}/{slug_img_name}")
                    processed += 1
                except Exception as e:
                    print(f"    WARN  Could not rescue {filename}: {e}")
                    warnings += 1

        # --- Also check sibling image folders (e.g. "NoteTitle-images/") ---
        for entry in os.scandir(root):
            if not entry.is_dir():
                continue
            if 'images' not in entry.name.lower():
                continue

            # Find the matching .md in this directory
            md_siblings = [f for f in os.listdir(root) if f.lower().endswith('.md')]
            if md_siblings:
                post_name = os.path.splitext(md_siblings[0])[0]
                url_slug  = slug_path(hugo_content_posts, os.path.join(root, md_siblings[0]), post_name)
            else:
                rel       = os.path.relpath(root, hugo_content_posts)
                url_slug  = '/'.join(slugify(p) for p in rel.replace('\\', '/').split('/') if p and p != '.')

            dest_img_dir = os.path.join(static_images_base, *url_slug.split('/'))
            os.makedirs(dest_img_dir, exist_ok=True)

            print(f"\n    [Rescue folder] {entry.name}  →  static/images/{url_slug}/")
            for img_file in sorted(os.listdir(entry.path)):
                img_ext = os.path.splitext(img_file)[1].lower()
                if img_ext not in IMAGE_EXTENSIONS:
                    continue
                name_no_ext, ext_orig = os.path.splitext(img_file)
                slug_img_name = slugify(name_no_ext) + ext_orig.lower()
                src = os.path.join(entry.path, img_file)
                dst = os.path.join(dest_img_dir, slug_img_name)
                try:
                    shutil.copy2(src, dst)
                    print(f"    OK   {slug_img_name}")
                    processed += 1
                except Exception as e:
                    print(f"    WARN  {slug_img_name}: {e}")
                    warnings += 1

        # --- Fix .md links in Hugo content to use slugified paths ---
        for filename in sorted(files):
            if not filename.lower().endswith('.md'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  WARN  Cannot read {filepath}: {e}")
                warnings += 1
                continue

            original = content

            # Fix spaces in /images/... paths → hyphens
            content = fix_spaces_in_hugo_links(content)

            # Remove leftover Obsidian embeds
            content = re.sub(
                r'!?\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp))\]\]',
                '', content, flags=re.IGNORECASE
            )

            if content != original:
                if safe_write(filepath, content):
                    print(f"    FIXED  {filename}")
                    processed += 1
                else:
                    warnings += 1
else:
    if hugo_content_posts:
        print(f"\n[JOB 2] SKIP — Hugo content posts dir not found: {hugo_content_posts}")
    else:
        print(f"\n[JOB 2] SKIP — No Hugo content posts dir provided.")


# ─── Summary ──────────────────────────────────────────────────────────────────
print(f"\n----------------------------------------------")
print(f"images.py done.  Processed: {processed}  |  Warnings: {warnings}")
if warnings > 0:
    sys.exit(1)
