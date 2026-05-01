"""
images.py  -  Obsidian → Hugo image processor (v3)
====================================================

Handles Karim's note structure where:
  - Posts live in nested subfolders  (ejpt/Day 0/Note.md)
  - Images live next to the .md in a sibling folder named like "Note images/"
    or "Note-images/"

Obsidian structure:
    posts/
      ejpt/
        Day 0/
          Introduction to information gathering.md
          Introduction to information gathering images/
            scope.png
            recon mapping flow.png

Hugo output structure (ALWAYS uses hyphens – no spaces):
    static/
      images/
        ejpt/
          day-0/
            introduction-to-information-gathering/
              scope.png
              recon-mapping-flow.png

Image link written into the .md file:
    ![scope](/images/ejpt/day-0/introduction-to-information-gathering/scope.png)

Usage (called automatically by BlogWatcher.ps1):
    python images.py <obsidian_posts_dir> <hugo_static_images_dir>
"""

import os
import re
import shutil
import sys
import tempfile

# ─── Argument validation ───────────────────────────────────────────────────────
if len(sys.argv) != 3:
    print("ERROR: Expected 2 arguments: <obsidian_posts_dir> <hugo_static_images_base>")
    sys.exit(1)

obsidian_posts_dir  = sys.argv[1]   # Obsidian vault posts folder
static_images_base  = sys.argv[2]   # Hugo static/images/

# ─── Patterns ─────────────────────────────────────────────────────────────────
# Matches both ![[image.png]] and [[image.png]] (Obsidian embeds)
OBSIDIAN_EMBED = re.compile(
    r'!?\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\]\]',
    re.IGNORECASE
)

# Matches already-converted Hugo links: ![alt](/images/...)
HUGO_LINK = re.compile(
    r'!\[[^\]]*\]\(/images/[^)]+\)',
    re.IGNORECASE
)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def slugify(text):
    """Convert any string to a lowercase hyphen-slug (URL-safe, no spaces)."""
    text = text.strip()
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove any character that is not alphanumeric or hyphen
    text = re.sub(r'[^a-z0-9\-]', '', text)
    # Collapse multiple consecutive hyphens
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def find_image_file(image_basename, md_dir):
    """
    Search for an image file near the .md file.
    Priority:
      1. Same directory as the .md
      2. Any sibling folder whose name contains 'images' (case-insensitive)
      3. Any sibling subfolder (broad fallback)
    """
    # 1. Same dir
    candidate = os.path.join(md_dir, image_basename)
    if os.path.isfile(candidate):
        return candidate

    try:
        entries = list(os.scandir(md_dir))
    except PermissionError:
        return None

    # 2. Sibling folders with 'images' in name
    for entry in entries:
        if entry.is_dir() and 'images' in entry.name.lower():
            candidate = os.path.join(entry.path, image_basename)
            if os.path.isfile(candidate):
                return candidate

    # 3. Any sibling subfolder
    for entry in entries:
        if entry.is_dir():
            candidate = os.path.join(entry.path, image_basename)
            if os.path.isfile(candidate):
                return candidate

    return None


def safe_write(filepath, content):
    """
    Write content to filepath using a temp file then atomic move.
    Avoids 'Bad file descriptor' when Obsidian still holds the file open.
    """
    try:
        fd, tmp_path = tempfile.mkstemp(suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            shutil.move(tmp_path, filepath)
            return True
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise
    except Exception as e:
        print(f"  WARN  Could not write back to {filepath}: {e}")
        return False


def build_url_slug(obsidian_posts_root, md_filepath, post_name):
    """
    Build the URL-path segment used for this post's images.
    Uses the relative subfolder path so that posts in different subfolders
    never collide even if they share the same filename.

    Example:
      posts_root  = C:/Vault/posts
      md_filepath = C:/Vault/posts/ejpt/Day 0/My Note.md
      post_name   = My Note
      → url_slug  = ejpt/day-0/my-note
    """
    rel_dir = os.path.relpath(os.path.dirname(md_filepath), obsidian_posts_root)
    parts = rel_dir.replace('\\', '/').split('/')
    slug_parts = [slugify(p) for p in parts if p and p != '.']
    slug_parts.append(slugify(post_name))
    return '/'.join(slug_parts)


# ─── Main walk ────────────────────────────────────────────────────────────────
processed = 0
warnings  = 0

for root, dirs, files in os.walk(obsidian_posts_dir):
    # Skip hidden directories
    dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

    for filename in sorted(files):
        if not filename.lower().endswith('.md'):
            continue

        post_name = os.path.splitext(filename)[0]
        filepath  = os.path.join(root, filename)

        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  WARN  Could not read {filepath}: {e}")
            warnings += 1
            continue

        # Only process files that have Obsidian embeds
        matches = OBSIDIAN_EMBED.findall(content)
        if not matches:
            continue

        # Build the URL slug for this post (subfolder-aware)
        url_slug = build_url_slug(obsidian_posts_dir, filepath, post_name)

        # Destination folder in Hugo static/images/<url_slug>/
        dest_img_dir = os.path.join(static_images_base, *url_slug.split('/'))
        os.makedirs(dest_img_dir, exist_ok=True)

        rel_path = os.path.relpath(filepath, obsidian_posts_dir)
        print(f"\n[{rel_path}]  →  images/{url_slug}/")

        changed = False
        for image_ref, _ext in matches:
            # image_ref may contain a full path (e.g. posts/ejpt/Day 0/folder/img.png)
            # We only care about the filename part
            image_basename = os.path.basename(image_ref)

            # Slugify the image filename to remove spaces
            name_no_ext, ext = os.path.splitext(image_basename)
            slug_img_name    = slugify(name_no_ext) + ext.lower()

            # The Hugo URL path (always hyphens, no spaces)
            url_path = f"/images/{url_slug}/{slug_img_name}"
            md_link  = f"![{name_no_ext}]({url_path})"

            # Replace ![[...]] and [[...]] forms
            for pattern in [f"![[{image_ref}]]", f"[[{image_ref}]]"]:
                if pattern in content:
                    content = content.replace(pattern, md_link)
                    changed = True

            # Copy the image file to Hugo static folder
            src = find_image_file(image_basename, root)
            dst = os.path.join(dest_img_dir, slug_img_name)

            if src:
                try:
                    shutil.copy2(src, dst)
                    rel_src = os.path.relpath(src, obsidian_posts_dir)
                    print(f"  OK   {slug_img_name}  (from {rel_src})")
                except Exception as e:
                    print(f"  WARN  Could not copy {slug_img_name}: {e}")
                    warnings += 1
            else:
                print(f"  WARN  Image not found near {rel_path}: {image_basename}")
                warnings += 1

        # Also fix any already-written Hugo links that still have spaces
        # Pattern: ![alt](/images/path with spaces/file.png)
        def fix_spaces_in_link(m):
            link = m.group(0)
            # Extract the URL part and slugify each segment
            inner = re.search(r'\(/images/([^)]+)\)', link)
            if inner:
                parts = inner.group(1).split('/')
                fixed_parts = []
                for p in parts:
                    name_part, sep, ext_part = p.rpartition('.')
                    if sep:
                        fixed_parts.append(slugify(name_part) + '.' + ext_part.lower())
                    else:
                        fixed_parts.append(slugify(p))
                fixed_url = '/images/' + '/'.join(fixed_parts)
                link = link.replace(inner.group(0), f'({fixed_url})')
            return link

        new_content = HUGO_LINK.sub(fix_spaces_in_link, content)
        if new_content != content:
            content = new_content
            changed = True

        # Write back if anything changed
        if changed:
            if safe_write(filepath, content):
                processed += 1
                print(f"  SAVED  {filename}")
            else:
                warnings += 1

# ─── Summary ──────────────────────────────────────────────────────────────────
print(f"\n----------------------------------------------")
print(f"images.py done.  Processed: {processed}  |  Warnings: {warnings}")
if warnings > 0:
    sys.exit(1)
