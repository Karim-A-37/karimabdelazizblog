"""
images.py  -  Obsidian -> Hugo image processor (v6)
====================================================

Jobs:
  1. Obsidian vault scan:
       a. Copy ALL images from sibling *-images/ folders -> static/images/<slug>/
       b. Auto-inject slug/title/date into frontmatter if missing
       c. Fix ![[image.png]] Obsidian embeds
       d. Fix /images/wrong-path/img.png absolute links
       e. Fix relative links  ![alt](img.png)  or  ![alt](images/img.png)

  2. Hugo content rescue:
       a. Copy any image files stuck in content/ -> static/images/<slug>/
       b. Apply same link fixes to .md files in content/

Slug rules:
    posts/ejpt/Day-0/My Note.md  ->  slug = my-note  (post name only, no subfolder)
    URL becomes: /posts/my-note/   (clean, no subfolder in URL)
"""

import os
import re
import shutil
import sys
import tempfile
from datetime import date as datemod

# ---- args --------------------------------------------------------------------
if len(sys.argv) < 3:
    print("ERROR: usage: images.py <obsidian_posts_dir> <static_images_base> [hugo_content_posts]")
    sys.exit(1)

obsidian_posts_dir = sys.argv[1]
static_images_base = sys.argv[2]
hugo_content_posts = sys.argv[3] if len(sys.argv) > 3 else None

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.tif'}

# Obsidian embed:  ![[img.png]]
RE_OBS = re.compile(
    r'!?\[\[([^\]]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\]\]',
    re.IGNORECASE
)

# Absolute Hugo link already written:  ![alt](/images/...)
RE_ABS = re.compile(
    r'!\[([^\]]*)\]\((/images/[^)]+)\)',
    re.IGNORECASE
)

# Relative link that has NO leading slash and is not http:
#   ![alt](scope.png)  or  ![alt](images/scope.png)  or  ![alt](subfolder/scope.png)
RE_REL = re.compile(
    r'!\[([^\]]*)\]\((?!http|/)([^)]+\.(?:png|jpg|jpeg|gif|webp|svg|bmp|tiff|tif))\)',
    re.IGNORECASE
)

# Frontmatter block
RE_FM = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# ---- helpers -----------------------------------------------------------------

def slugify(text):
    text = text.strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def post_slug(post_name):
    """Slug from post name only — no subfolder. Gives clean URL."""
    return slugify(post_name)


def static_slug(root_dir, md_path, post_name):
    """
    Full slug including subfolder for static/images/ storage path.
    posts/ejpt/Day-0/Note.md  ->  ejpt/day-0/note
    """
    rel_dir = os.path.relpath(os.path.dirname(md_path), root_dir)
    parts   = [p for p in rel_dir.replace('\\', '/').split('/') if p and p != '.']
    return '/'.join(slugify(p) for p in parts) + '/' + slugify(post_name) if parts else slugify(post_name)


def find_image_folders(md_dir):
    folders = []
    try:
        for e in os.scandir(md_dir):
            if e.is_dir() and 'images' in e.name.lower():
                folders.append(e.path)
    except PermissionError:
        pass
    return folders


def find_image_file(basename, md_dir):
    c = os.path.join(md_dir, basename)
    if os.path.isfile(c):
        return c
    for folder in find_image_folders(md_dir):
        c = os.path.join(folder, basename)
        if os.path.isfile(c):
            return c
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


def copy_img(src, dst_dir, slug_name):
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, slug_name)
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print("  WARN  Copy failed %s: %s" % (slug_name, e))
        return False


def ensure_frontmatter(content, post_name, url_slug):
    """
    Inject minimal frontmatter if missing or empty.
    Adds title, date, slug, draft=false.
    slug = just the post name slug (no subfolder) -> clean URL.
    Does NOT overwrite existing values.
    """
    today = datemod.today().isoformat()
    title = post_name.replace('-', ' ').strip()

    fm_match = RE_FM.match(content)
    if fm_match:
        fm_body = fm_match.group(1).strip()
        # If frontmatter exists but is empty, rewrite it
        if not fm_body:
            new_fm = "---\ntitle: \"%s\"\ndate: %s\nslug: \"%s\"\ndraft: false\n---\n" % (title, today, url_slug)
            return new_fm + content[fm_match.end():]
        # Frontmatter has content — only add missing fields
        changed = False
        if 'slug:' not in fm_body:
            fm_body += '\nslug: "%s"' % url_slug
            changed = True
        if 'title:' not in fm_body:
            fm_body = 'title: "%s"\n' % title + fm_body
            changed = True
        if 'date:' not in fm_body:
            fm_body = fm_body + '\ndate: %s' % today
            changed = True
        if 'draft:' not in fm_body:
            fm_body = fm_body + '\ndraft: false'
            changed = True
        if changed:
            new_fm = "---\n%s\n---\n" % fm_body.strip()
            return new_fm + content[fm_match.end():]
        return content
    else:
        # No frontmatter at all — prepend it
        new_fm = "---\ntitle: \"%s\"\ndate: %s\nslug: \"%s\"\ndraft: false\n---\n\n" % (title, today, url_slug)
        return new_fm + content


def fix_image_links(content, img_url_prefix, md_dir):
    """
    Fix all image link variants to use /images/<img_url_prefix>/<slug>.ext
    img_url_prefix = ejpt/day-0/introduction-to-information-gathering
    """
    changed = False

    # 1. Obsidian embeds:  ![[img.png]]
    def fix_obs(m):
        nonlocal changed
        ref     = m.group(1)
        base    = os.path.basename(ref)
        nm, ext = os.path.splitext(base)
        slug    = slugify(nm) + ext.lower()
        changed = True
        return "![%s](/images/%s/%s)" % (nm, img_url_prefix, slug)
    content = RE_OBS.sub(fix_obs, content)

    # 2. Absolute /images/... links with wrong path
    def fix_abs(m):
        nonlocal changed
        alt     = m.group(1)
        url     = m.group(2)          # /images/something/file.png
        file    = url.split('/')[-1]  # file.png (may have %20)
        nm, ext = os.path.splitext(file.replace('%20', ' '))
        slug    = slugify(nm) + ext.lower()
        new_url = "/images/%s/%s" % (img_url_prefix, slug)
        if url != new_url:
            changed = True
            return "![%s](%s)" % (alt, new_url)
        return m.group(0)
    content = RE_ABS.sub(fix_abs, content)

    # 3. Relative links:  ![alt](scope.png)  or  ![alt](images/scope.png)
    def fix_rel(m):
        nonlocal changed
        alt      = m.group(1)
        rel_path = m.group(2)                    # e.g. "scope.png" or "images/scope.png"
        basename = os.path.basename(rel_path)    # "scope.png"
        nm, ext  = os.path.splitext(basename)
        # Try to find the actual file
        src = find_image_file(basename, md_dir)
        slug = slugify(nm) + ext.lower()
        changed = True
        return "![%s](/images/%s/%s)" % (alt if alt else nm, img_url_prefix, slug)
    content = RE_REL.sub(fix_rel, content)

    return content, changed


# ---- counters ----------------------------------------------------------------
copied    = 0
fixed_mds = 0
warnings  = 0


# ==============================================================================
# JOB 1 - Obsidian vault
# ==============================================================================
if os.path.isdir(obsidian_posts_dir):
    print("\n[JOB 1] Obsidian posts: %s" % obsidian_posts_dir)

    for root, dirs, files in os.walk(obsidian_posts_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        md_files = [f for f in sorted(files) if f.lower().endswith('.md')]
        if not md_files:
            continue

        for filename in md_files:
            post_name    = os.path.splitext(filename)[0]
            md_path      = os.path.join(root, filename)
            url_slug     = post_slug(post_name)          # clean URL slug (no subfolder)
            img_url_slug = static_slug(obsidian_posts_dir, md_path, post_name)  # storage path
            dst_dir      = os.path.join(static_images_base, *img_url_slug.split('/'))

            # A. Copy all images from sibling image folders
            for img_folder in find_image_folders(root):
                for img_file in sorted(os.listdir(img_folder)):
                    ext = os.path.splitext(img_file)[1].lower()
                    if ext not in IMAGE_EXTS:
                        continue
                    nm, ext_o = os.path.splitext(img_file)
                    slug_name = slugify(nm) + ext_o.lower()
                    src       = os.path.join(img_folder, img_file)
                    if copy_img(src, dst_dir, slug_name):
                        print("  COPY  %s -> /images/%s/%s" % (img_file, img_url_slug, slug_name))
                        copied += 1
                    else:
                        warnings += 1

            # B. Fix .md content
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print("  WARN  Cannot read %s: %s" % (md_path, e))
                warnings += 1
                continue

            original = content

            # Inject/fix frontmatter (slug, title, date, draft)
            content = ensure_frontmatter(content, post_name, url_slug)

            # Fix all image link types
            content, _ = fix_image_links(content, img_url_slug, root)

            if content != original:
                if safe_write(md_path, content):
                    print("  FIXED  %s" % filename)
                    fixed_mds += 1
                else:
                    warnings += 1

else:
    print("\n[JOB 1] SKIP - not found: %s" % obsidian_posts_dir)


# ==============================================================================
# JOB 2 - Hugo content rescue
# ==============================================================================
if hugo_content_posts and os.path.isdir(hugo_content_posts):
    print("\n[JOB 2] Rescue from Hugo content: %s" % hugo_content_posts)

    for root, dirs, files in os.walk(hugo_content_posts):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.'))

        md_files  = [f for f in sorted(files) if f.lower().endswith('.md')]
        img_files = [f for f in sorted(files) if os.path.splitext(f)[1].lower() in IMAGE_EXTS]

        if not md_files:
            continue

        post_name    = os.path.splitext(md_files[0])[0]
        url_slug     = post_slug(post_name)
        img_url_slug = static_slug(hugo_content_posts, os.path.join(root, md_files[0]), post_name)
        dst_dir      = os.path.join(static_images_base, *img_url_slug.split('/'))

        # Rescue image files directly in the folder
        for img_file in img_files:
            nm, ext_o = os.path.splitext(img_file)
            slug_name = slugify(nm) + ext_o.lower()
            src       = os.path.join(root, img_file)
            if copy_img(src, dst_dir, slug_name):
                print("  RESCUED  %s -> /images/%s/%s" % (img_file, img_url_slug, slug_name))
                copied += 1
            else:
                warnings += 1

        # Rescue from sibling image subfolders
        try:
            for e in os.scandir(root):
                if not (e.is_dir() and 'images' in e.name.lower()):
                    continue
                for img_file in sorted(os.listdir(e.path)):
                    ext = os.path.splitext(img_file)[1].lower()
                    if ext not in IMAGE_EXTS:
                        continue
                    nm, ext_o = os.path.splitext(img_file)
                    slug_name = slugify(nm) + ext_o.lower()
                    src       = os.path.join(e.path, img_file)
                    if copy_img(src, dst_dir, slug_name):
                        print("  RESCUED  %s/%s -> /images/%s/%s" % (e.name, img_file, img_url_slug, slug_name))
                        copied += 1
                    else:
                        warnings += 1
        except PermissionError:
            pass

        # Fix .md links in Hugo content
        for filename in md_files:
            md_path = os.path.join(root, filename)
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print("  WARN  Cannot read %s: %s" % (md_path, e))
                warnings += 1
                continue
            original = content
            content  = ensure_frontmatter(content, os.path.splitext(filename)[0], url_slug)
            content, _ = fix_image_links(content, img_url_slug, root)
            if content != original:
                if safe_write(md_path, content):
                    print("  FIXED  %s" % filename)
                    fixed_mds += 1
                else:
                    warnings += 1

# ---- summary -----------------------------------------------------------------
print("\n----------------------------------------------")
print("images.py done.  Copied: %d  |  Fixed MDs: %d  |  Warnings: %d" % (copied, fixed_mds, warnings))
if warnings > 0:
    sys.exit(1)
