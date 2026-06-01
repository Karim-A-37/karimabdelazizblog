"""
blog_upgrade.py  — Downloads Wazuh labs and sets up blog structure
"""
import os, sys, urllib.request, subprocess, textwrap

SITE    = r"C:\Users\DELL\karimabdelazizblog"
CONTENT = os.path.join(SITE, "content")
RAW     = "https://raw.githubusercontent.com/Karim-A-37/Wazuh/main"

def save(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"  OK  {os.path.basename(path)}")

def download(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        print(f"  ERR download failed: {url}\n      {e}")
        return None

def make_lab(url, dest, fm_dict):
    body = download(url)
    if body is None:
        return
    # Strip existing frontmatter if any
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].lstrip("\n")
    # Build frontmatter
    lines = ["---"]
    for k, v in fm_dict.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f'  - "{item}"')
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    lines.append("")
    full = "\n".join(lines) + "\n" + body.lstrip("\n")
    save(dest, full)

# ── Step 1: Download Wazuh labs ──────────────────────────────────────────
print("\n[1] Downloading Wazuh labs from GitHub")

make_lab(
    url  = RAW + "/Lab%201/lab-1.md",
    dest = os.path.join(CONTENT, "projects", "wazuh", "lab-1.md"),
    fm_dict = {
        "title": "Lab 1 - Wazuh + Suricata IDS Setup",
        "date":  "2025-10-31",
        "slug":  "wazuh-lab-1-ids-setup",
        "description": "Setting up Wazuh SIEM with Suricata NIDS to detect port scans, SQL injection, XSS, and Tor connections using Emerging Threats rules.",
        "tags": ["wazuh", "suricata", "ids", "siem", "network-security"],
        "series": ["Wazuh Labs"],
        "weight": 1,
        "draft":  False,
        "ShowToc": True,
        "TocOpen": False,
    }
)

make_lab(
    url  = RAW + "/Lab%202/Lab-2.md",
    dest = os.path.join(CONTENT, "projects", "wazuh", "lab-2.md"),
    fm_dict = {
        "title": "Lab 2 - Malware Detection with Wazuh",
        "date":  "2025-12-09",
        "slug":  "wazuh-lab-2-malware-detection",
        "description": "Malware detection using Wazuh FIM, CDB hash lists, VirusTotal, Windows Defender log forwarding, and Sysmon for fileless malware detection.",
        "tags": ["wazuh", "malware", "fim", "virustotal", "sysmon"],
        "series": ["Wazuh Labs"],
        "weight": 2,
        "draft":  False,
        "ShowToc": True,
        "TocOpen": False,
    }
)

make_lab(
    url  = RAW + "/Lab%203/N8N_Blockchain_AI.md",
    dest = os.path.join(CONTENT, "projects", "wazuh", "lab-3.md"),
    fm_dict = {
        "title": "Lab 3 - SetChain: AI + Blockchain Threat Detection",
        "date":  "2026-05-25",
        "slug":  "wazuh-lab-3-setchain",
        "description": "Graduation project: automated cybersecurity pipeline — Wazuh, Suricata, n8n, 5-layer AI (Isolation Forest + XGBoost + LLM), STIX 2.1, IPFS, and Hyperledger Fabric blockchain.",
        "tags": ["wazuh", "ai", "blockchain", "hyperledger", "n8n", "ipfs", "graduation-project"],
        "series": ["Wazuh Labs"],
        "weight": 3,
        "draft":  False,
        "ShowToc": True,
        "TocOpen": False,
    }
)

# ── Step 2: Patch eJPT posts with series frontmatter ────────────────────
print("\n[2] Patching eJPT posts with series frontmatter")

ejpt_posts = [
    os.path.join(CONTENT, "posts", "ejpt", "Day-0", "Introduction to information gathering.md"),
    os.path.join(CONTENT, "posts", "ejpt", "Day-1", "Passive Reconnaissance.md"),
]

for p in ejpt_posts:
    if not os.path.exists(p):
        print(f"  ERR not found: {p}")
        continue
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    if "series:" in text:
        print(f"  OK  already patched: {os.path.basename(p)}")
        continue
    text = text.replace(
        "draft: false",
        'draft: false\nseries: ["eJPT"]\nShowToc: true\nTocOpen: false',
        1
    )
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"  OK  patched: {os.path.basename(p)}")

# ── Step 3: Hugo build ───────────────────────────────────────────────────
print("\n[3] Hugo build")
os.chdir(SITE)
result = subprocess.run(["hugo"], capture_output=True, text=True)
for line in (result.stdout + result.stderr).splitlines():
    if line.strip():
        print(f"  {line}")
if result.returncode == 0:
    print("  OK  build successful")
else:
    print(f"  ERR build failed (exit {result.returncode})")
    sys.exit(1)

# ── Step 4: Git push ─────────────────────────────────────────────────────
print("\n[4] Git commit and push")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m",
    "Blog upgrade: Wazuh labs (3), sections, search, eJPT series, Projects nav"], check=True)
result = subprocess.run(["git", "push", "origin", "main"],
    capture_output=True, text=True)
print(result.stdout or result.stderr)

print("\nAll done!")
