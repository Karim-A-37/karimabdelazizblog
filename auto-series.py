"""
auto-series.py  —  Automatic Series & Weight Injector
=====================================================
Scans content/posts and content/projects for markdown files.
For every .md inside a subfolder, it:
  1. Sets  series: ["<Parent Folder Name>"]   (folder name, title-cased)
  2. Sets  weight: N   (based on alphabetical/natural sort order within that folder)
  3. Sets  ShowToc: true   (for readability)

Rules:
  - Only touches posts inside a SUBFOLDER (not root-level files)
  - Skips _index.md files
  - Series name = the immediate parent folder name (e.g. "ejpt" → "eJPT", "wazuh" → "Wazuh Labs")
  - Weight = position in sorted file list (1, 2, 3...)
  - Never overwrites existing series/weight if they already match
"""

import os, re, glob

SITE_ROOT = r"C:\Users\DELL\karimabdelazizblog"
CONTENT_DIRS = [
    os.path.join(SITE_ROOT, "content", "posts"),
    os.path.join(SITE_ROOT, "content", "projects"),
]

# Map folder names to friendly series names.
# Add entries here for custom naming; otherwise folder name is title-cased.
SERIES_NAME_MAP = {
    "ejpt": "eJPT",
    "wazuh": "Wazuh Labs",
    "ctf-writeups": "CTF Writeups",
}


def get_series_name(folder_name):
    """Convert a folder name to a series display name."""
    key = folder_name.lower().strip()
    if key in SERIES_NAME_MAP:
        return SERIES_NAME_MAP[key]
    # Default: replace hyphens/underscores with spaces and title-case
    return folder_name.replace("-", " ").replace("_", " ").title()


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def parse_frontmatter(content):
    """Return (fm_text, body) or (None, content) if no frontmatter."""
    m = re.match(r"\A---[ \t]*\r?\n(.*?\r?\n)---[ \t]*\r?\n(.*)", content, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return None, content


def has_field(fm_text, field):
    """Check if a YAML field exists in frontmatter text."""
    return bool(re.search(r"^" + re.escape(field) + r"\s*:", fm_text, re.MULTILINE))


def get_field_value(fm_text, field):
    """Get a simple scalar field value."""
    m = re.search(r"^" + re.escape(field) + r"\s*:\s*(.*)", fm_text, re.MULTILINE)
    if m:
        return m.group(1).strip().strip("\"'")
    return None


def get_series_value(fm_text):
    """Extract the first series name from frontmatter (handles both list and scalar)."""
    # List form:  series:\n  - "Name"
    m = re.search(r"^series\s*:\s*\n\s*-\s*[\"']?(.*?)[\"']?\s*$", fm_text, re.MULTILINE)
    if m:
        return m.group(1)
    # Inline list: series: ["Name"]
    m = re.search(r'^series\s*:\s*\["?(.*?)"?\]', fm_text, re.MULTILINE)
    if m:
        return m.group(1)
    # Scalar: series: Name
    m = re.search(r"^series\s*:\s*[\"']?(.*?)[\"']?\s*$", fm_text, re.MULTILINE)
    if m and m.group(1):
        return m.group(1)
    return None


def set_or_update_field(fm_text, field, value):
    """Set a scalar field in frontmatter. Adds it if missing, updates if present."""
    pattern = r"^" + re.escape(field) + r"\s*:.*$"
    new_line = f"{field}: {value}"
    if re.search(pattern, fm_text, re.MULTILINE):
        fm_text = re.sub(pattern, new_line, fm_text, count=1, flags=re.MULTILINE)
    else:
        # Add before the last line
        fm_text = fm_text.rstrip("\n") + "\n" + new_line + "\n"
    return fm_text


def set_series_field(fm_text, series_name):
    """Set series as a proper YAML list."""
    new_block = f'series:\n  - "{series_name}"'

    # Remove existing series field (could be scalar or list)
    # First remove list items that follow
    fm_text = re.sub(
        r"^series\s*:.*(?:\n\s+-\s+.*)*",
        "{{SERIES_PLACEHOLDER}}",
        fm_text,
        count=1,
        flags=re.MULTILINE,
    )
    if "{{SERIES_PLACEHOLDER}}" in fm_text:
        fm_text = fm_text.replace("{{SERIES_PLACEHOLDER}}", new_block)
    else:
        # Field didn't exist, add it
        fm_text = fm_text.rstrip("\n") + "\n" + new_block + "\n"
    return fm_text


def collect_posts_by_series_folder(content_dir):
    """
    Walk content_dir and group markdown files by their series folder.
    Returns dict: { series_folder_name: [(weight, file_path), ...] }
    """
    groups = {}

    for root, dirs, files in os.walk(content_dir):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        md_files = sorted(f for f in files if f.endswith(".md") and f != "_index.md")
        if not md_files:
            continue

        # Determine the series folder — the first subfolder under content_dir
        rel = os.path.relpath(root, content_dir)
        if rel == ".":
            continue  # skip root-level files

        parts = rel.replace("\\", "/").split("/")
        series_folder = parts[0]  # e.g. "ejpt" or "wazuh"

        if series_folder not in groups:
            groups[series_folder] = []

        for fname in md_files:
            groups[series_folder].append(os.path.join(root, fname))

    return groups


def natural_sort_key(path):
    """Sort by Day-0, Day-1, ..., Day-10 correctly; then by filename."""
    basename = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
    return [
        int(c) if c.isdigit() else c.lower()
        for c in re.split(r"(\d+)", basename)
    ]


def process_file(filepath, series_name, weight):
    """Ensure a file has the correct series and weight. Returns True if modified."""
    content = read_file(filepath)
    fm_text, body = parse_frontmatter(content)

    if fm_text is None:
        return False  # no frontmatter, skip

    modified = False

    # --- Series ---
    current_series = get_series_value(fm_text)
    if current_series != series_name:
        fm_text = set_series_field(fm_text, series_name)
        modified = True

    # --- Weight (as integer, never quoted) ---
    current_weight = get_field_value(fm_text, "weight")
    target_weight = str(weight)
    # Check if weight value matches AND is stored as a bare integer (not quoted)
    raw_weight_line = re.search(r"^weight\s*:\s*(.*)", fm_text, re.MULTILINE)
    raw_value = raw_weight_line.group(1).strip() if raw_weight_line else None
    needs_weight_fix = (
        current_weight != target_weight  # wrong value
        or (raw_value and raw_value != target_weight)  # right value but quoted: "1" vs 1
    )
    if needs_weight_fix:
        fm_text = set_or_update_field(fm_text, "weight", weight)
        modified = True

    # --- ShowToc ---
    if not has_field(fm_text, "ShowToc"):
        fm_text = set_or_update_field(fm_text, "ShowToc", "true")
        modified = True

    if modified:
        new_content = "---\n" + fm_text + "---\n" + body
        write_file(filepath, new_content)
        return True

    return False


# ── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    total_fixed = 0

    for content_dir in CONTENT_DIRS:
        if not os.path.isdir(content_dir):
            continue

        groups = collect_posts_by_series_folder(content_dir)

        for folder_name, file_paths in sorted(groups.items()):
            series_name = get_series_name(folder_name)
            # Sort files naturally (Day-0 < Day-1 < ... < Day-10)
            file_paths.sort(key=natural_sort_key)

            for i, fpath in enumerate(file_paths, start=1):
                if process_file(fpath, series_name, i):
                    rel = os.path.relpath(fpath, SITE_ROOT)
                    print(f"FIXED  {rel}  ->  series={series_name!r}  weight={i}")
                    total_fixed += 1

    if total_fixed:
        print(f"\nDone. Updated {total_fixed} file(s).")
    else:
        print("All series/weight OK — no changes needed.")
