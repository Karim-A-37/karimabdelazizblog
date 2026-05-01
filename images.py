"""
images.py  -  Obsidian -> Hugo image processor (v5)
====================================================

Two jobs in one pass:

  JOB 1 - Obsidian vault (primary):
    For every .md in <obsidian_posts_dir>:
      a. Proactively copies ALL images from sibling "...-images/" folders
         to static/images/<slug>/ regardless of link state.
      b. Rewrites ![[image.png]] Obsidian embeds -> proper Hugo links.
      c. Fixes any existing /images/old-path/img.png links that use wrong
         paths or have spaces, updating them to the correct slug URL.

  JOB 2 - Hugo content rescue (secondary, optional):
    Finds image files stuck inside content/posts/ and copies them to
    static/images/<slug>/. Fixes .md links in content/ to match.

Slug rules:
    posts/ejpt/Day 0/My Note.md  ->  ejpt/day-0/my-note
    scope.png                     ->  scope.png  (no change if already clean)
    recon mapping flow.png        ->  recon-mapping-flow.png

Usage:
    python images.py <obsidian_posts_dir> <static_images_base>
    python images.py <obsidian_posts_dir> <static_images_base> <hugo_content_posts_dir>
"""

import os
import re
import shutil
import sys
import tempfile

# ---- argument check ----------------------------------------------------------
if len(sys.argv) < 3:
    print("ERROR: usage: images.py <obsidian_posts_dir> <static_images_base> [hugo_content_posts]")
    sys.exit(1)

obsidian_posts_dir = sys.argv[1]
static_images_base = sys.argv[2]
hugo_content_posts = sys.argv[3] if len(sys.argv) > 3 else None

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.tif'}

# Obsidian embed:  ![[image.png]]  or  [[image.png]]
RE_OBSIDIAN = re.compile(
    r'!?\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\]\]',
    re.IGNORECASE
)

# Existing Hugo link:  ![alt](/images/...)
RE_HUGO_LINK = re.compile(
    r'!\[([^\]]*)\]\((/images/[^)]+)\)',
    re.IGNORECASE
)

# ---- helpers -----------------------------------------------------------------

def slugify(text):
    """Lowercase ASCII hyphen slug."""
    text = text.strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def build_slug(root_dir, md_path, post_name):
    """
    Build URL slug from subfolder path + post name.
    Example:
      root = posts/
      md   = posts/ejpt/Day 0/My Note.md
      name = My Note
      ->   ejpt/day-0/my-note
    """
    rel_dir = os.path.relpath(os.path.dirname(md_path), root_dir)
    parts   = [p for p in rel_dir.replace('\\', '/').split('/') if p and p != '.']
    return '/'.join(slugify(p) for p in parts) + '/' + slugify(post_name) if parts else slugify(post_name)


def find_image_folders(md_dir):
    """Return list of sibling folders whose name contains 'images'."""
    folders = []
    try:
        for e in os.scandir(md_dir):
            if e.is_dir() and 'images' in e.name.lower():
                folders.append(e.path)
    except PermissionError:
        pass
    return folders


def find_image_file(basename, md_dir):
    """Find an image by filename near the .md file."""
    # same dir
    c = os.path.join(md_dir, basename)
    if os.path.isfile(c):
        return c
    # sibling image folders
    for folder in find_image_folders(md_dir):
        c = os.path.join(folder, basename)
        if os.path.isfile(c):
            return c
    # any sibling dir
    try:
        for e in os.scandir(md_dir):
            if e.is_dir():
                c = os.path.join(e.path, basename)
                if os.path.isfile(c):
                    return c
    except PermissionError:
        pass
    return None


def safe_write(path, content):
    """Atomic write via temp file to avoid Obsidian file-lock issues."""
    try:
        fd, tmp = tempfile.mkstemp(suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            shutil.move(tmp, path)
            return True
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass
            raise
    except Exception as e:
        print("  WARN  Cannot write %s: %s" % (path, e))
        return False


def copy_image(src, dst_dir, slug_name):
    """Copy src image to dst_dir/slug_name. Returns True on success."""
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, slug_name)
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print("  WARN  Copy failed %s: %s" % (slug_name, e))
        return False


# ---- counters ----------------------------------------------------------------
copied    = 0
fixed_mds = 0
warnings  = 0


# ==============================================================================
# JOB 1 - Process Obsidian vault posts
# ==============================================================================
if os.path.isdir(obsidian_posts_dir):
    print("\n[JOB 1] Obsidian posts: %s" % obsidian_posts_dir)

    for root, dirs, files in os.walk(obsidian_posts_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        md_files = [f for f in sorted(files) if f.lower().endswith('.md')]
        if not md_files:
            continue

        for filename in md_files:
            post_name = os.path.splitext(filename)[0]
            md_path   = os.path.join(root, filename)
            url_slug  = build_slug(obsidian_posts_dir, md_path, post_name)
            dst_dir   = os.path.join(static_images_base, *url_slug.split('/'))

            # --- Step A: proactively copy ALL images from sibling folders ----
            img_folders = find_image_folders(root)
            for img_folder in img_folders:
                for img_file in sorted(os.listdir(img_folder)):
                    ext = os.path.splitext(img_file)[1].lower()
                    if ext not in IMAGE_EXTS:
                        continue
                    base_no_ext = os.path.splitext(img_file)[0]
                    slug_name   = slugify(base_no_ext) + ext
                    src         = os.path.join(img_folder, img_file)
                    if copy_image(src, dst_dir, slug_name):
                        rel = os.path.relpath(src, obsidian_posts_dir)
                        print("  COPY  %s  ->  /images/%s/%s" % (rel, url_slug, slug_name))
                        copied += 1
                    else:
                        warnings += 1

            # --- Step B: fix links in the .md file ---------------------------
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print("  WARN  Cannot read %s: %s" % (md_path, e))
                warnings += 1
                continue

            original = content

            # B1: replace ![[image.png]] Obsidian embeds
            def replace_obsidian(m):
                image_ref    = m.group(1)
                basename     = os.path.basename(image_ref)
                name, ext    = os.path.splitext(basename)
                slug_img     = slugify(name) + ext.lower()
                return "![%s](/images/%s/%s)" % (name, url_slug, slug_img)

            content = RE_OBSIDIAN.sub(replace_obsidian, content)

            # B2: fix existing /images/... links that use wrong path or spaces
            def replace_hugo(m):
                alt      = m.group(1)
                old_url  = m.group(2)          # e.g. /images/Old Name/scope.png
                # extract just the filename from whatever old path was used
                old_file = old_url.split('/')[-1]
                name, ext = os.path.splitext(old_file.replace('%20', ' ').replace('-', ' ').strip())
                # re-slug the filename
                slug_img = slugify(name) + ext.lower()
                # build correct URL
                new_url  = "/images/%s/%s" % (url_slug, slug_img)
                return "![%s](%s)" % (alt, new_url)

            content = RE_HUGO_LINK.sub(replace_hugo, content)

            if content != original:
                if safe_write(md_path, content):
                    print("  FIXED  %s" % filename)
                    fixed_mds += 1
                else:
                    warnings += 1

else:
    print("\n[JOB 1] SKIP - Obsidian posts dir not found: %s" % obsidian_posts_dir)


# ==============================================================================
# JOB 2 - Rescue images stuck inside Hugo content/posts/
# ==============================================================================
if hugo_content_posts and os.path.isdir(hugo_content_posts):
    print("\n[JOB 2] Rescue from Hugo content: %s" % hugo_content_posts)

    for root, dirs, files in os.walk(hugo_content_posts):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        md_files = [f for f in sorted(files) if f.lower().endswith('.md')]

        # rescue image files directly inside this dir
        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTS:
                continue
            if md_files:
                post_name = os.path.splitext(md_files[0])[0]
                url_slug  = build_slug(hugo_content_posts, os.path.join(root, md_files[0]), post_name)
            else:
                rel      = os.path.relpath(root, hugo_content_posts)
                url_slug = '/'.join(slugify(p) for p in rel.replace('\\', '/').split('/') if p and p != '.')
            dst_dir   = os.path.join(static_images_base, *url_slug.split('/'))
            name, ext_o = os.path.splitext(filename)
            slug_name   = slugify(name) + ext_o.lower()
            src         = os.path.join(root, filename)
            if copy_image(src, dst_dir, slug_name):
                print("  RESCUED  %s  ->  /images/%s/%s" % (filename, url_slug, slug_name))
                copied += 1
            else:
                warnings += 1

        # rescue images inside sibling "...-images/" subfolders
        try:
            for e in os.scandir(root):
                if not (e.is_dir() and 'images' in e.name.lower()):
                    continue
                if md_files:
                    post_name = os.path.splitext(md_files[0])[0]
                    url_slug  = build_slug(hugo_content_posts, os.path.join(root, md_files[0]), post_name)
                else:
                    rel      = os.path.relpath(root, hugo_content_posts)
                    url_slug = '/'.join(slugify(p) for p in rel.replace('\\', '/').split('/') if p and p != '.')
                dst_dir   = os.path.join(static_images_base, *url_slug.split('/'))
                for img_file in sorted(os.listdir(e.path)):
                    ext = os.path.splitext(img_file)[1].lower()
                    if ext not in IMAGE_EXTS:
                        continue
                    name_part, ext_o = os.path.splitext(img_file)
                    slug_name = slugify(name_part) + ext_o.lower()
                    src       = os.path.join(e.path, img_file)
                    if copy_image(src, dst_dir, slug_name):
                        print("  RESCUED  %s/%s  ->  /images/%s/%s" % (e.name, img_file, url_slug, slug_name))
                        copied += 1
                    else:
                        warnings += 1
        except PermissionError:
            pass

        # fix .md links in Hugo content
        for filename in md_files:
            md_path  = os.path.join(root, filename)
            url_slug = build_slug(hugo_content_posts, md_path, os.path.splitext(filename)[0])
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print("  WARN  Cannot read %s: %s" % (md_path, e))
                warnings += 1
                continue
            original = content
            # fix spaces in /images/... paths
            def fix_link(m):
                alt     = m.group(1)
                old_url = m.group(2)
                old_file = old_url.split('/')[-1]
                name, ext = os.path.splitext(old_file.replace('%20', ' ').replace('-', ' ').strip())
                slug_img  = slugify(name) + ext.lower()
                new_url   = "/images/%s/%s" % (url_slug, slug_img)
                return "![%s](%s)" % (alt, new_url)
            content = RE_HUGO_LINK.sub(fix_link, content)
            # remove leftover Obsidian embeds
            content = RE_OBSIDIAN.sub('', content)
            if content != original:
                if safe_write(md_path, content):
                    print("  FIXED  %s" % filename)
                    fixed_mds += 1
                else:
                    warnings += 1
else:
    if hugo_content_posts:
        print("\n[JOB 2] SKIP - not found: %s" % hugo_content_posts)

# ---- summary -----------------------------------------------------------------
print("\n----------------------------------------------")
print("images.py done.  Copied: %d  |  Fixed MDs: %d  |  Warnings: %d" % (copied, fixed_mds, warnings))
if warnings > 0:
    sys.exit(1)
