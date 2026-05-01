"""
images.py  —  Obsidian → Hugo image processor
Handles Karim's note structure where images live in sibling folders
next to each .md file, named like "[topic] images/"

Obsidian structure:
    posts/
      Day 1/
        active recon images/      ← sibling image folder
        passive recon images/     ← sibling image folder
        Active Reconnaissance.md
        Passive Reconnaissance.md

Hugo output structure:
    static/
      images/
        Active Reconnaissance/
          screenshot.png
          nmap-output.png
        Passive Reconnaissance/
          whois.png

Usage (called automatically by BlogWatcher.ps1):
    python images.py <hugo_posts_dir> <static_images_base_dir>
"""

import os
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
if len(sys.argv) != 3:
    print("ERROR: Expected 2 arguments: <hugo_posts_dir> <static_images_base_dir>")
    sys.exit(1)

posts_dir          = sys.argv[1]
static_images_base = sys.argv[2]

# Obsidian image embed patterns:
#   ![[image.png]]   → standard Obsidian embed
#   [[image.png]]    → wiki-link style
IMAGE_PATTERN = re.compile(
    r'!?\[\[([^\]]+\.(png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\]\]',
    re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Helper: find an image file by searching sibling folders of the .md file
# ---------------------------------------------------------------------------
def find_image(image_filename, md_file_dir):
    """
    Search for an image in this priority order:
      1. Directly in the same directory as the .md file
      2. In any subfolder whose name contains 'images'
         (e.g. "active recon images", "passive recon images")
      3. In any subfolder (broader fallback)
    Returns the full path if found, None otherwise.
    """
    base_name = os.path.basename(image_filename)

    # 1. Same directory as the .md file
    candidate = os.path.join(md_file_dir, base_name)
    if os.path.exists(candidate):
        return candidate

    # 2. Sibling folders with "images" in the name
    try:
        for entry in os.scandir(md_file_dir):
            if entry.is_dir() and 'images' in entry.name.lower():
                candidate = os.path.join(entry.path, base_name)
                if os.path.exists(candidate):
                    return candidate
    except PermissionError:
        pass

    # 3. Any sibling subfolder (broader fallback)
    try:
        for entry in os.scandir(md_file_dir):
            if entry.is_dir():
                candidate = os.path.join(entry.path, base_name)
                if os.path.exists(candidate):
                    return candidate
    except PermissionError:
        pass

    return None

# ---------------------------------------------------------------------------
# Walk all .md files recursively inside posts_dir
# ---------------------------------------------------------------------------
processed = 0
warnings  = 0

for root, dirs, files in os.walk(posts_dir):
    # Skip hidden directories
    dirs[:] = [d for d in dirs if not d.startswith('.')]

    for filename in sorted(files):
        if not filename.endswith('.md'):
            continue

        post_name = os.path.splitext(filename)[0]   # e.g. "Active Reconnaissance"
        filepath  = os.path.join(root, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = IMAGE_PATTERN.findall(content)
        if not matches:
            continue

        # Create a per-post image subfolder inside Hugo's static/images/
        post_img_dir = os.path.join(static_images_base, post_name)
        os.makedirs(post_img_dir, exist_ok=True)

        rel_path = os.path.relpath(filepath, posts_dir)
        print(f"\n[{rel_path}]  ->  images/{post_name}/")

        for image_name, _ext in matches:
            safe_name = os.path.basename(image_name)
            url_path  = f"/images/{post_name}/{safe_name.replace(' ', '%20')}"
            md_link   = f"![{safe_name}]({url_path})"

            # Replace both ![[x]] and [[x]] forms
            content = content.replace(f"![[{image_name}]]", md_link)
            content = content.replace(f"[[{image_name}]]",  md_link)

            # Locate the image file near the .md file
            src = find_image(image_name, root)
            dst = os.path.join(post_img_dir, safe_name)

            if src:
                shutil.copy2(src, dst)
                rel_src = os.path.relpath(src, posts_dir)
                print(f"  OK  {safe_name}  (from {rel_src})")
            else:
                print(f"  WARN  Not found near {rel_path}: {safe_name}")
                warnings += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        processed += 1

# ---------------------------------------------------------------------------
print(f"\n----------------------------------------------")
print(f"images.py done.  Processed: {processed}  |  Warnings: {warnings}")
