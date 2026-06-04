---
title: "Lab 3 - SetChain: AI + Blockchain Threat Detection"
date: "2026-05-25"
slug: "wazuh-lab-3-setchain"
description: "Graduation project: automated cybersecurity pipeline — Wazuh, Suricata, n8n, 5-layer AI (Isolation Forest + XGBoost + LLM), STIX 2.1, IPFS, and Hyperledger Fabric blockchain."
tags:
  - "wazuh"
  - "ai"
  - "blockchain"
  - "hyperledger"
  - "n8n"
  - "ipfs"
  - "graduation-project"
series:
  - "wazuh"
weight: 3
draft: false
ShowToc: true
TocOpen: false
---

# SetChain — AI-Powered Cybersecurity Automation Platform

> **Graduation Project** | Automated Threat Detection · AI Confidence Scoring · STIX 2.1 Threat Intelligence · Hyperledger Fabric Blockchain · IPFS Decentralized Storage · Automated Active Response

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Prerequisites & Lab Environment](#4-prerequisites--lab-environment)
5. [Component 1 — Suricata IDS Installation & Wazuh Link](#5-component-1--suricata-ids-installation--wazuh-link)
6. [Component 2 — Docker & n8n Workflow Engine](#6-component-2--docker--n8n-workflow-engine)
7. [Component 3 — Wazuh → n8n Integration](#7-component-3--wazuh--n8n-integration)
8. [Component 4 — Smart Alert Filter](#8-component-4--smart-alert-filter)
9. [Component 5 — AI Models API (SetChain Pipeline)](#9-component-5--ai-models-api-setchain-pipeline)
10. [Component 6 — n8n Workflow Node-by-Node](#10-component-6--n8n-workflow-node-by-node)
11. [Component 7 — IPFS Decentralized Storage](#11-component-7--ipfs-decentralized-storage)
12. [Component 8 — Hyperledger Fabric Blockchain](#12-component-8--hyperledger-fabric-blockchain)
13. [Component 9 — Blockchain Connector API](#13-component-9--blockchain-connector-api)
14. [Component 10 — AI Chatbot (RAG Integration)](#14-component-10--ai-chatbot-rag-integration)
15. [Wazuh Active Response Configuration](#15-wazuh-active-response-configuration)
16. [Wazuh ossec.conf Reference](#16-wazuh-ossecconf-reference)
17. [End-to-End Testing](#17-end-to-end-testing)
18. [Service Management & Startup Order](#18-service-management--startup-order)
19. [Problems Encountered & Solutions](#19-problems-encountered--solutions)
20. [Quick Reference](#20-quick-reference)

---

## 1. Project Overview

**SetChain** is a fully automated cybersecurity pipeline that:

- Detects network threats via **Suricata IDS** and **Wazuh SIEM**
- Scores every alert with a **5-layer AI pipeline** (anomaly detection → confidence scoring → MITRE mapping → human-review routing → LLM playbook)
- Converts confirmed threats to **STIX 2.1** structured threat intelligence
- Stores every indicator immutably on **IPFS** + **Hyperledger Fabric blockchain**
- Triggers **automated active response** (firewall block, host deny, account disable) via the Wazuh API — the action chosen by the AI, not a static rule
- Feeds all execution data into a **RAG-powered AI chatbot** that can answer questions about live pipeline activity in natural language

### End-to-End Pipeline

```
Network Traffic
      ↓
Suricata IDS  (packet inspection · ET Open Rules)
      ↓
Wazuh SIEM  (log correlation · rule matching · alert generation)
      ↓
Smart Filter Script  (rate limiting · dedup · noise reduction)
      ↓
n8n Webhook  (workflow automation engine)
      ↓
SetChain AI API  (5-layer ML + LLM · /analyze)
      ↓
  ┌──────────────────────────────────────────────┐
  │ decision == ACTION_REQUIRED                  │  decision == IGNORE
  ↓                                              ↓
AbuseIPDB Threat Intel Lookup              No Operation
  ↓                                              ↓
STIX 2.1 Indicator Bundle              File Log (for chatbot memory)
  ↓
IPFS Upload  (content-addressed · decentralized)
  ↓
Hyperledger Fabric  (immutable audit trail · recordAlert txn)
  ↓
Wazuh JWT Auth  (fresh token)
  ↓
Build Active Response  (AI maps decision → command)
  ↓
Wazuh Active Response API  (firewall-drop / host-deny / disable-account)
  ↓
Edit Fields  (format final execution summary)
  ↓
File Log → AI Chatbot Memory  (RAG context for /chat)
```

### Key Contributions

- **5-layer AI pipeline** combining Isolation Forest, XGBoost, MITRE ATT&CK mapping, human-review routing, and LLM-based playbook generation (Groq llama3-70b-8192)
- **Automated response selection** — the AI chooses the response type, timeout, and command based on confidence score, threat level, and MITRE tactic. Not a static rule.
- **Tamper-evident threat intelligence** — every STIX 2.1 bundle is stored on IPFS and the CID is recorded on Hyperledger Fabric, creating an immutable audit trail
- **RAG chatbot** that reads live n8n execution logs and can trace any alert through every stage of the pipeline

---

## 2. System Architecture

### Lab Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Lab Environment (VMware / VirtualBox)                  │
│                                                                             │
│  ┌──────────────────────┐          ┌───────────────────────────────────┐   │
│  │   Wazuh Manager      │          │   Ubuntu Agent  192.168.100.34    │   │
│  │   192.168.100.33     │◄────────►│                                   │   │
│  │                      │          │  ┌──────────┐  ┌───────────────┐  │   │
│  │  wazuh-manager       │          │  │ Suricata │  │ n8n  :5678    │  │   │
│  │  ossec.conf          │          │  │ IDS      │  │ (Docker)      │  │   │
│  │  Smart Filter Script │          │  │ ET Rules │  └───────────────┘  │   │
│  │  Active Response     │          │  └──────────┘  ┌───────────────┐  │   │
│  └──────────────────────┘          │                 │ AI API :8000  │  │   │
│                                    │  ┌──────────┐  │ FastAPI       │  │   │
│                                    │  │  Wazuh   │  │ 5-layer ML    │  │   │
│                                    │  │  Agent   │  └───────────────┘  │   │
│                                    │  └──────────┘  ┌───────────────┐  │   │
│                                    │                 │ Blockchain    │  │   │
│                                    │  ┌──────────┐  │ API  :3005    │  │   │
│                                    │  │   IPFS   │  │ Hyperledger   │  │   │
│                                    │  │  :5001   │  │ Fabric        │  │   │
│                                    │  └──────────┘  └───────────────┘  │   │
│                                    └───────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AI Pipeline (5 Layers)

```
Alert JSON
    ↓
Layer 0 — Anomaly Detection
    Isolation Forest model
    Output: anomaly_score, is_anomaly
    ↓
Layer 1 — Confidence Scoring
    XGBoost classifier
    Multi-feature: rule level · groups · MITRE tactic · anomaly score
    Output: confidence (0.0 – 1.0)
    ↓
Layer 2 — Response Recommendation
    Rule-based + ML hybrid
    Output: BLOCK_IP | ALERT_ADMIN | KILL_PROCESS | DISABLE_ACCOUNT | MONITOR_ONLY
    ↓
Layer 3 — Human Review Routing
    Threshold gating
    Output: threat_level = APPROVED_RESPONSE | NEEDS_HUMAN_REVIEW
    ↓
Layer 4 — LLM Playbook Generator
    Groq llama3-70b-8192
    MITRE ATT&CK framework integration
    Output: structured playbook with mitigation, technique_id, tactic
    ↓
Final: { decision, playbook }
```

---

## 3. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| IDS | Suricata | 7.x | Packet inspection, ET Open rules |
| SIEM | Wazuh | 4.7+ | Log correlation, alerting, active response |
| Workflow | n8n | Latest | Pipeline automation, webhook receiver |
| Container | Docker + Compose | 26.x | n8n containerization |
| AI Runtime | FastAPI + Uvicorn | 0.110+ | HTTP API server for AI pipeline |
| Anomaly Detection | Isolation Forest (scikit-learn) | — | Layer 0 |
| Confidence Scoring | XGBoost | — | Layer 1 |
| LLM | Groq (llama3-70b-8192) | — | Layer 4 playbook generation |
| Threat Intel | AbuseIPDB API v2 | — | IP reputation lookup |
| Threat Standard | STIX 2.1 | — | Structured threat intelligence format |
| Decentralized Storage | IPFS (Kubo) | Latest | Content-addressed storage |
| Blockchain | Hyperledger Fabric | 2.5.15 | Immutable audit trail |
| Blockchain CA | Fabric CA | 1.5.17 | Identity management |
| Smart Contract | Node.js chaincode | — | ThreatIntelContract |
| Language | Python 3.12 | — | AI pipeline, filter scripts |
| Language | JavaScript / Node.js 18 | — | Blockchain connector, chaincode |
| OS | Ubuntu 24.04 LTS (Noble) | — | Agent machine |

---

## 4. Prerequisites & Lab Environment

### Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk | 40 GB free | 80 GB |
| CPU | 4 cores | 8 cores |

> **Disk note:** Hyperledger Fabric Docker images alone consume ~8 GB. IPFS, n8n, and AI model files add another 5–10 GB.

### Network Layout

| Machine | IP | Role |
|---------|----|------|
| Wazuh Manager | `192.168.100.33` | SIEM manager, alert analysis, active response engine |
| Ubuntu Agent | `192.168.100.34` | Wazuh agent, Suricata, n8n, AI API, Blockchain |

### Open Ports (Ubuntu Agent)

| Port | Service |
|------|---------|
| 22 | SSH |
| 5678 | n8n UI & webhook receiver |
| 8000 | SetChain AI API |
| 3005 | Blockchain Connector API |
| 4001 | IPFS swarm |
| 5001 | IPFS API |
| 8080 | IPFS Gateway |

### Required Software (Pre-installed)

- Ubuntu 24.04.4 LTS (ubuntu-24.04.4-live-server-amd64.iso)
- Wazuh Agent (pre-installed and enrolled to manager before this guide)
- Python 3.12 + pip + venv

---

## 5. Component 1 — Suricata IDS Installation & Wazuh Link

**Machine:** Ubuntu Agent (`192.168.100.34`)

### 5.1 Install Suricata

```bash
sudo apt update
sudo add-apt-repository ppa:oisf/suricata-stable -y
sudo apt update
sudo apt install suricata -y
suricata --version
```

### 5.2 Download Emerging Threats Open Rules

```bash
sudo suricata-update
sudo suricata-update update-sources
sudo suricata-update enable-source et/open
sudo suricata-update
```

### 5.3 Configure Suricata

```bash
sudo nano /etc/suricata/suricata.yaml
```

Key settings to verify:
```yaml
# Set your monitored interface
af-packet:
  - interface: ens33   # replace with your actual interface name

# Output — Wazuh reads this file
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      types:
        - alert
        - dns
        - http
        - tls
        - flow
```

Find your interface:
```bash
ip link show
```

### 5.4 Start and enable Suricata

```bash
sudo systemctl enable suricata
sudo systemctl start suricata
sudo systemctl status suricata

# Watch alerts in real time
sudo tail -f /var/log/suricata/eve.json | python3 -m json.tool
```

### 5.5 Link Suricata to Wazuh

Tell the Wazuh agent to forward Suricata's `eve.json` to the manager.

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add inside `<ossec_config>`:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/suricata/eve.json</location>
</localfile>
```

Restart the agent:
```bash
sudo systemctl restart wazuh-agent
```

### 5.6 Suppress noisy Suricata rule at source

Rule `86601` (ET INFO `pwd=` cleartext) fires on every matching HTTP packet and causes alert floods. Add a threshold:

```bash
sudo nano /etc/suricata/threshold.config
```

Add at the bottom:
```
# ET INFO pwd= rule — max 1 per source IP per 12 hours
threshold gen_id 1, sig_id 2013504, type threshold, track by_src, count 1, seconds 43200
```

```bash
sudo systemctl reload suricata
```

Also add a Wazuh-level throttle on the Manager:

```bash
# On the Wazuh MANAGER
sudo nano /var/ossec/etc/rules/local_rules.xml
```

```xml
<group name="suricata,">
  <rule id="100200" level="3" frequency="10" timeframe="43200" ignore="43200">
    <if_sid>86601</if_sid>
    <description>Suricata: ET INFO pwd in cleartext (throttled)</description>
    <group>suricata,</group>
  </rule>
</group>
```

```bash
sudo systemctl restart wazuh-manager
```

---

## 6. Component 2 — Docker & n8n Workflow Engine

**Machine:** Ubuntu Agent (`192.168.100.34`)

### 6.1 Install Docker

```bash
cat > install_docker.sh << 'EOF'
#!/bin/bash
set -euo pipefail

apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

apt-get update -qq
apt-get install -y -qq ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -qq
apt-get install -y -qq docker-ce docker-ce-cli containerd.io \
                        docker-buildx-plugin docker-compose-plugin

systemctl enable docker --quiet
systemctl start docker

docker --version && echo "[OK] Docker installed."
docker compose version && echo "[OK] Compose ready."
EOF

sudo bash install_docker.sh
```

### 6.2 Allow Docker without sudo

```bash
sudo usermod -aG docker $USER
newgrp docker
docker ps   # should work without sudo
```

> **Security note:** Members of the `docker` group have effective root-level access to the host. Only add trusted users.

### 6.3 Useful Docker aliases

Add to `~/.bashrc`:

```bash
alias dstop='cd /opt/n8n && docker compose stop'
alias dstart='cd /opt/n8n && docker compose start'
```

Apply:
```bash
source ~/.bashrc
```

Usage:
```bash
dstop    # stop n8n container
dstart   # start n8n container
```

### 6.4 Deploy n8n

```bash
cat > install_n8n.sh << 'EOF'
#!/bin/bash
set -euo pipefail

N8N_DIR="/opt/n8n"
HOST_IP="192.168.100.34"
N8N_PORT="5678"
N8N_USER="admin"
N8N_PASS="<your-n8n-password>"

[[ $EUID -ne 0 ]] && { echo "Run as root: sudo bash $0"; exit 1; }

mkdir -p "$N8N_DIR"

cat > "${N8N_DIR}/docker-compose.yml" << YAML
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "${N8N_PORT}:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASS}
      - WEBHOOK_URL=http://${HOST_IP}:${N8N_PORT}/
      - GENERIC_TIMEZONE=Africa/Cairo
      - N8N_LOG_LEVEL=info
      - N8N_METRICS=true
      - N8N_DIAGNOSTICS_ENABLED=false
      - N8N_SECURE_COOKIE=false
      - DB_TYPE=sqlite
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - n8n_net

volumes:
  n8n_data:
    driver: local

networks:
  n8n_net:
    driver: bridge
YAML

cd "$N8N_DIR"
docker compose pull
docker compose up -d

sleep 5
if docker ps --filter "name=n8n" --filter "status=running" | grep -q n8n; then
  echo "[OK] n8n running at http://${HOST_IP}:${N8N_PORT}"
else
  docker compose logs --tail=20
  echo "[ERROR] n8n failed to start."
fi
EOF

sudo bash install_n8n.sh
```

> **Why `N8N_SECURE_COOKIE=false`?** n8n v2.21+ defaults to `N8N_SECURE_COOKIE=true`, which requires HTTPS. Without setting it to `false`, the login page loads but cookies silently fail on plain HTTP, making it impossible to authenticate.

### 6.5 Open firewall

```bash
sudo ufw allow 5678/tcp comment "n8n workflow UI"
sudo ufw allow 22/tcp comment "SSH"
sudo ufw status
```

### 6.6 Verify

```bash
docker ps --filter name=n8n
curl -s -o /dev/null -w "%{http_code}" http://192.168.100.34:5678
# Should return 200
```

Access n8n at: **http://192.168.100.34:5678**

---

## 7. Component 3 — Wazuh → n8n Integration

**Machine:** Wazuh Manager (`192.168.100.33`)

### 7.1 Create the integration script

```bash
sudo bash -c 'cat > /var/ossec/integrations/custom-n8n << '"'"'PYEOF'"'"'
#!/usr/bin/env python3
"""
Wazuh → n8n webhook forwarder
Wazuh calls this script as:  custom-n8n <alert_file> <api_key> <hook_url>
"""
import sys, json, urllib.request, urllib.error

N8N_WEBHOOK = "http://192.168.100.34:5678/webhook/wazuh-alerts"
MIN_LEVEL   = 3

def main():
    if len(sys.argv) < 2:
        print("Usage: custom-n8n <alert_file>", file=sys.stderr)
        sys.exit(1)

    try:
        with open(sys.argv[1], "r") as f:
            alert = json.load(f)
    except Exception as e:
        print(f"[n8n] Failed to read alert file: {e}", file=sys.stderr)
        sys.exit(1)

    level = int(alert.get("rule", {}).get("level", 0))
    if level < MIN_LEVEL:
        sys.exit(0)

    payload = {
        "source":    "wazuh",
        "timestamp": alert.get("timestamp", ""),
        "agent":     alert.get("agent", {}),
        "rule": {
            "id":          alert.get("rule", {}).get("id", ""),
            "level":       level,
            "description": alert.get("rule", {}).get("description", ""),
            "groups":      alert.get("rule", {}).get("groups", []),
        },
        "location": alert.get("location", ""),
        "full_log": alert.get("full_log", ""),
        "data":     alert.get("data", {}),
        "syscheck": alert.get("syscheck", {}),
        "decoder":  alert.get("decoder", {}),
    }

    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        N8N_WEBHOOK, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "Wazuh-n8n-Integration/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[n8n] Alert forwarded — level {level} — HTTP {resp.status}")
    except urllib.error.URLError as e:
        print(f"[n8n] Failed to reach n8n: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
PYEOF'

sudo chmod 750 /var/ossec/integrations/custom-n8n
sudo chown root:wazuh /var/ossec/integrations/custom-n8n
```

### 7.2 Add integration block to ossec.conf

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add before `</ossec_config>`:

```xml
<!-- n8n Webhook Integration -->
<integration>
  <name>custom-n8n</name>
  <level>3</level>
  <alert_format>json</alert_format>
</integration>
```

### 7.3 Restart Wazuh Manager

```bash
sudo systemctl restart wazuh-manager
sudo tail -f /var/ossec/logs/ossec.log | grep -i "n8n\|integration"
```

### 7.4 Quick webhook test

```bash
# Test true branch (high severity — should trigger ACTION_REQUIRED)
curl -s -X POST http://192.168.100.34:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "id": "5712",
      "level": 14,
      "description": "sshd: Multiple failed authentication attempts from a single source",
      "firedtimes": 8,
      "mitre": {
        "tactic": ["Credential Access"],
        "id": ["T1110"],
        "technique": ["Brute Force"]
      }
    },
    "agent": {"id": "001", "name": "ubuntu", "ip": "192.168.100.34"},
    "data": {"srcip": "45.33.32.156", "dstip": "192.168.100.34"},
    "timestamp": "2026-05-25T05:33:00Z"
  }' | python3 -m json.tool

# Test false branch (low severity — should IGNORE)
curl -X POST http://192.168.100.34:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "id": "5715",
      "level": 3,
      "description": "SSHD successful login from authorized user"
    },
    "agent": {"id": "001", "name": "ubuntu-agent", "ip": "192.168.100.34"},
    "data": {"srcip": "192.168.100.50", "dstip": "192.168.100.34"},
    "timestamp": "2026-05-25T18:01:00Z"
  }'
```

---

## 8. Component 4 — Smart Alert Filter

**Machine:** Wazuh Manager (`192.168.100.33`)

### Problem

Suricata rule `86601` (ET INFO `pwd=` cleartext) fires on every HTTP packet matching the pattern — flooding n8n with thousands of duplicate low-severity alerts per hour. The basic `custom-n8n` script has no rate limiting.

### Solution

An intelligent middleware that sits between Wazuh and n8n:

- **Global rate limit** — max 20 alerts/minute to n8n across all rules
- **Per-rule rate limiting** — configurable count/window/silence per rule ID
- **`NEVER_FORWARD` list** — known noisy rules are always dropped
- **`ALWAYS_FORWARD` list** — critical rules bypass all rate limits
- **State persistence** — JSON file tracks counts between invocations

### Decision Logic

```
Alert arrives
      ↓
level < 3?               → DROP
      ↓
In NEVER_FORWARD list?   → DROP  (rule 86601 and others)
      ↓
In ALWAYS_FORWARD list?  → SEND immediately (skip all rate limits)
      ↓
Global > 20/min?         → DROP  (protects n8n from any flood)
      ↓
Per-rule rate exceeded?  → DROP + silence that rule for N seconds
      ↓
FORWARD to n8n ✅
```

### Deploy

```bash
sudo tee /var/ossec/integrations/n8n-smart-filter.py > /dev/null << 'EOF'
#!/usr/bin/env python3
"""n8n Smart Alert Filter — rate limiting + dedup + severity routing"""

import sys, json, time, urllib.request, urllib.error
from datetime import datetime

N8N_WEBHOOK  = "http://192.168.100.34:5678/webhook/wazuh-alerts"
STATE_FILE   = "/var/ossec/integrations/.n8n_filter_state.json"
LOG_FILE     = "/var/ossec/logs/n8n-filter.log"

GLOBAL_RATE_LIMIT  = 20    # max alerts forwarded per minute (all rules combined)
GLOBAL_RATE_WINDOW = 60    # seconds

# Per-rule limits: (max_count, window_seconds, silence_seconds)
RULE_LIMITS = {
    "86601":   (1,  43200, 43200),   # ET INFO pwd= → 1 per 12h, silent 12h
    "86600":   (5,  3600,  3600),    # Generic Suricata → 5/hour
    "5501":    (3,  300,   600),     # SSH auth failure → 3 per 5min
    "5503":    (3,  300,   600),     # SSH brute force
    "31151":   (2,  3600,  1800),    # Web attack
    "default": (10, 300,   60),      # Everything else → 10 per 5min
}

# Always forward — bypass all rate limits (critical rules)
ALWAYS_FORWARD_RULE_IDS = {
    "87103",  # Suricata: malware detected
    "87105",  # Suricata: exploit attempt
    "5712",   # SSH brute force (high volume)
    "31166",  # SQL injection
    "554",    # File modified in /etc
    "550",    # Integrity checksum changed
}

# Never forward — always suppress (known noisy, low-value rules)
NEVER_FORWARD_RULE_IDS = {
    "86601",  # ET INFO pwd= cleartext
}

MIN_LEVEL = 3

def log(action, rule_id, level, agent, reason=""):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] {action:8s} | rule={rule_id} lvl={level} agent={agent} | {reason}\n")
    except Exception:
        pass

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"rules": {}, "global": {"count": 0, "window_start": 0}}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

def forward(alert):
    payload = {
        "source":    "wazuh",
        "timestamp": alert.get("timestamp", ""),
        "agent":     alert.get("agent", {}),
        "rule": {
            "id":          alert.get("rule", {}).get("id", ""),
            "level":       alert.get("rule", {}).get("level", 0),
            "description": alert.get("rule", {}).get("description", ""),
            "groups":      alert.get("rule", {}).get("groups", []),
        },
        "location": alert.get("location", ""),
        "full_log": alert.get("full_log", ""),
        "data":     alert.get("data", {}),
    }
    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(N8N_WEBHOOK, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "Wazuh-n8n-SmartFilter/2.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    try:
        with open(sys.argv[1]) as f:
            alert = json.load(f)
    except Exception as e:
        print(f"[filter] Cannot read alert: {e}", file=sys.stderr)
        sys.exit(1)

    rule_id  = str(alert.get("rule", {}).get("id", "0"))
    level    = int(alert.get("rule", {}).get("level", 0))
    agent_id = str(alert.get("agent", {}).get("id", "000"))
    agent_nm = alert.get("agent", {}).get("name", "unknown")

    # Hard filters
    if level < MIN_LEVEL:
        log("DROP", rule_id, level, agent_nm, f"below MIN_LEVEL {MIN_LEVEL}")
        sys.exit(0)
    if rule_id in NEVER_FORWARD_RULE_IDS:
        log("DROP", rule_id, level, agent_nm, "NEVER_FORWARD list")
        sys.exit(0)

    # Always forward critical rules — skip rate limits entirely
    if rule_id in ALWAYS_FORWARD_RULE_IDS:
        try:
            status = forward(alert)
            log("FORCE", rule_id, level, agent_nm, f"critical rule → HTTP {status}")
        except Exception as e:
            log("ERROR", rule_id, level, agent_nm, f"forward failed: {e}")
        sys.exit(0)

    now   = time.time()
    state = load_state()

    # Global rate limit
    g = state["global"]
    if now - g["window_start"] > GLOBAL_RATE_WINDOW:
        g["count"], g["window_start"] = 0, now
    if g["count"] >= GLOBAL_RATE_LIMIT:
        log("DROP", rule_id, level, agent_nm, "global rate limit reached")
        save_state(state)
        sys.exit(0)
    g["count"] += 1

    # Per-rule rate limit
    max_c, window, silence = RULE_LIMITS.get(rule_id, RULE_LIMITS["default"])
    key = f"{rule_id}:{agent_id}"
    r   = state["rules"].get(key, {"count": 0, "window_start": now, "silenced_until": 0})

    if now < r["silenced_until"]:
        log("DROP", rule_id, level, agent_nm,
            f"silenced for {int(r['silenced_until'] - now)}s more")
        save_state(state)
        sys.exit(0)

    if now - r["window_start"] > window:
        r["count"], r["window_start"] = 0, now

    r["count"] += 1
    if r["count"] > max_c:
        r["silenced_until"] = now + silence
        state["rules"][key] = r
        log("DROP", rule_id, level, agent_nm,
            f"rate limit ({r['count']}/{max_c}) → silenced {silence}s")
        save_state(state)
        sys.exit(0)

    state["rules"][key] = r
    save_state(state)

    try:
        status = forward(alert)
        log("FORWARD", rule_id, level, agent_nm,
            f"count={r['count']}/{max_c} → HTTP {status}")
    except Exception as e:
        log("ERROR", rule_id, level, agent_nm, f"forward failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

sudo chmod 750 /var/ossec/integrations/n8n-smart-filter.py
sudo chown root:wazuh /var/ossec/integrations/n8n-smart-filter.py
sudo touch /var/ossec/logs/n8n-filter.log
sudo chown wazuh:wazuh /var/ossec/logs/n8n-filter.log

# Wrapper — Wazuh requires integration scripts to be named custom-*
sudo bash -c 'cat > /var/ossec/integrations/custom-n8n-smart-filter << WRAPPER
#!/bin/bash
/var/ossec/integrations/n8n-smart-filter.py "$1" "$2" "$3"
WRAPPER'
sudo chmod 750 /var/ossec/integrations/custom-n8n-smart-filter
sudo chown root:wazuh /var/ossec/integrations/custom-n8n-smart-filter

# Switch ossec.conf to use the smart filter
sudo sed -i 's/<name>custom-n8n<\/name>/<name>custom-n8n-smart-filter<\/name>/' \
  /var/ossec/etc/ossec.conf

sudo systemctl restart wazuh-manager
```

### Monitor

```bash
sudo tail -f /var/ossec/logs/n8n-filter.log
```

Sample output:
```
[2026-05-25T10:00:01Z] DROP     | rule=86601 lvl=3 agent=ubuntu | NEVER_FORWARD list
[2026-05-25T10:00:03Z] FORWARD  | rule=5503  lvl=7 agent=ubuntu | count=1/3 → HTTP 200
[2026-05-25T10:00:10Z] FORCE    | rule=550   lvl=7 agent=ubuntu | critical rule → HTTP 200
[2026-05-25T10:00:15Z] DROP     | rule=5503  lvl=5 agent=ubuntu | silenced for 587s more
```

---

## 9. Component 5 — AI Models API (SetChain Pipeline)

**Machine:** Ubuntu Agent (`192.168.100.34`)

### 9.1 Setup Python environment

```bash
cd ~/project/ai-models/Project/gradModel

# The venv may have been created on Windows (has Scripts/ instead of bin/)
# Delete and recreate natively on Linux
rm -rf venv
python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn requests numpy scikit-learn \
            xgboost pandas pydantic langchain-groq
```

### 9.2 Configuration file (config.py)

Located at `~/project/ai-models/Project/gradModel/setchain-chatbot/config.py`:

```python
# ============================================
# SetChain AI — Configuration
# ============================================

# --- Groq (LLM for Layer 4 Playbook Generator) ---
# Sign up at https://console.groq.com → API Keys → Create
GROQ_API_KEY = "<your-groq-api-key>"
# Recommended model: llama3-70b-8192 (free tier available)

# --- Telegram Bot (optional — for alert notifications) ---
# Create via @BotFather on Telegram → /newbot
TELEGRAM_BOT_TOKEN = "<your-telegram-bot-token>"

# --- AI Models API (FastAPI running on this machine) ---
AI_API_URL = "http://localhost:8000"

# --- n8n Webhook ---
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/wazuh-alerts"
```

### 9.3 Add /health endpoint

The API file only has `/analyze` and `/chat` by default. Add `/health`:

```bash
sed -i 's/@app.post("\/analyze")/@app.get("\/health")\ndef health_check():\n    return {"status": "ok", "engine": "SetChain AI", "model": "llama3-70b-8192"}\n\n@app.post("\/analyze")/' api.py
```

Verify:
```bash
grep -A3 "@app.get" api.py
```

### 9.4 Create systemd service

```bash
sudo bash -c "cat > /etc/systemd/system/setchain-ai.service << 'EOF'
[Unit]
Description=SetChain AI Engine (FastAPI)
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/home/agent/project/ai-models/Project/gradModel
Environment=\"PATH=/home/agent/project/ai-models/Project/gradModel/venv/bin\"
ExecStart=/home/agent/project/ai-models/Project/gradModel/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable setchain-ai
sudo systemctl start setchain-ai
sudo ufw allow 8000/tcp comment "SetChain AI API"
```

### 9.5 Manual startup (development / debugging)

```bash
cd ~/project/ai-models/Project/gradModel
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
```

### 9.6 Verify

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok","engine":"SetChain AI","model":"llama3-70b-8192"}

# Full analysis test
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "rule": {
        "id": "5710",
        "level": 10,
        "description": "sshd: attempt to login using a denied user",
        "mitre": {"tactic": ["Credential Access"], "id": ["T1110"]}
      },
      "agent": {"ip": "192.168.100.34"}
    }
  }' | python3 -m json.tool
```

**Expected AI Response:**

```json
{
    "decision": "ACTION_REQUIRED",
    "playbook": {
        "source": "Antigravity IDS Pipeline",
        "timestamp": "2026-05-25T...",
        "alert_id": "5710",
        "agent_id": "unknown",
        "host_ip": "192.168.100.34",
        "threat_level": "APPROVED_RESPONSE",
        "confidence": 0.881,
        "recommended_action": "ALERT_ADMIN",
        "details": {
            "rule_description": "sshd: attempt to login using a denied user",
            "tactic": "Credential Access",
            "technique_id": "T1110",
            "mitigation": "User Account Management",
            "milestone_info": "Model-4: MITRE Framework Integration"
        }
    }
}
```

---

## 10. Component 6 — n8n Workflow Node-by-Node

Open n8n at **http://192.168.100.34:5678** → New Workflow.

### Complete Workflow Shape

```
Webhook
   ↓
AI-Models  (HTTP Request → POST /analyze)
   ↓
IF  decision == "ACTION_REQUIRED"
   │
   ├── TRUE ──────────────────────────────────────────────────────────────┐
   │                                                                      │
   ▼                                                                      │
Threat Intel Lookup  (HTTP Request → AbuseIPDB GET /check)         FALSE  │
   ↓                                                                      ▼
STIX  (Code Node — generate STIX 2.1 bundle)               No Operation
   ↓                                                                      ↓
Blockchain  (HTTP Request → POST /api/v1/alerts)           HTTP Request1 (file log)
   ↓
fresh token  (Code Node — Wazuh JWT auth)
   ↓
Build Response  (Code Node — map AI decision → command)
   ↓
Wazuh Active Response  (HTTP Request → PUT /active-response)
   ↓
Edit Fields  (format final summary)
   ↓
file  (HTTP Request → POST /n8n-log → AI chatbot memory)
```

---

### Node 1: Webhook

| Setting | Value |
|---------|-------|
| HTTP Method | `POST` |
| Path | `wazuh-alerts` |
| Authentication | None |
| Response Mode | Immediately |

**Webhook URL:** `http://192.168.100.34:5678/webhook/wazuh-alerts`

After creating the node, click **Listen for Test Event** once to activate it, then send a test curl. Once data appears, click **Stop Listening** and continue building.

---

### Node 2: AI-Models (HTTP Request)

| Setting | Value |
|---------|-------|
| Method | `POST` |
| URL | `http://192.168.100.34:8000/analyze` |
| Send Body | ON |
| Body Content Type | JSON |
| Specify Body | Using JSON |
| JSON field | Click the **Expression toggle (fx)** then paste: `={{ JSON.stringify({ "alert": $json }) }}` |

> **Critical — Expression toggle:** You must click the **fx** button on the JSON field to switch to Expression mode. If you type `{ "alert": {{ $json }} }` in plain mode, n8n serializes `$json` as the string `[object Object]` and the AI API receives malformed input.

---

### Node 3: IF (Decision Branch)

| Setting | Value |
|---------|-------|
| Left Value | `{{ $json.decision }}` |
| Operator | `equals` |
| Right Value | `ACTION_REQUIRED` |

- **True output** → Threat Intel Lookup
- **False output** → No Operation → HTTP Request1 (file log)

---

### Node 4 (True): Threat Intel Lookup (HTTP Request)

Queries AbuseIPDB to get the reputation of the source IP.

| Setting | Value |
|---------|-------|
| Method | `GET` |
| URL | `https://api.abuseipdb.com/api/v2/check` |
| Send Query Parameters | ON |
| Parameter `ipAddress` | `={{ $json.playbook.host_ip }}` |
| Parameter `maxAgeInDays` | `90` |
| Send Headers | ON |
| Header `Key` | `<your-abuseipdb-api-key>` — get free at https://www.abuseipdb.com/api |
| Header `Accept` | `application/json` |

---

### Node 5 (True): STIX (Code Node — JavaScript)

Converts the AI pipeline output into a STIX 2.1 indicator bundle:

```javascript
const data = $('AI-Models').item.json;

const stix = {
  type: "bundle",
  id: `bundle--${Math.random().toString(36).substr(2, 9)}`,
  spec_version: "2.1",
  objects: [
    {
      type: "indicator",
      spec_version: "2.1",
      id: `indicator--${Math.random().toString(36).substr(2, 9)}`,
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      name: data.playbook?.details?.rule_description || "Unknown Threat",
      description: `SetChain AI — Confidence: ${data.playbook?.confidence}`,
      indicator_types: ["malicious-activity"],
      pattern: `[network-traffic:dst_ref.value = '${data.playbook?.host_ip || "0.0.0.0"}']`,
      pattern_type: "stix",
      valid_from: new Date().toISOString(),
      labels: [
        data.playbook?.threat_level || "unknown",
        data.playbook?.recommended_action || "monitor"
      ],
      external_references: [{
        source_name: "mitre-attack",
        external_id: data.playbook?.details?.technique_id || "T0000"
      }],
      x_setchain_decision:   data.decision,
      x_setchain_confidence: data.playbook?.confidence,
      x_setchain_action:     data.playbook?.recommended_action,
      x_setchain_tactic:     data.playbook?.details?.tactic,
      x_setchain_mitigation: data.playbook?.details?.mitigation,
      x_setchain_alert_id:   data.playbook?.alert_id,
      x_setchain_host_ip:    data.playbook?.host_ip,
      x_setchain_timestamp:  data.playbook?.timestamp
    }
  ]
};

return { json: stix };
```

---

### Node 6 (True): Blockchain (HTTP Request)

Sends the STIX bundle to the Blockchain Connector API:

| Setting | Value |
|---------|-------|
| Method | `POST` |
| URL | `http://192.168.100.34:3005/api/v1/alerts` |
| Send Body | ON |
| Body Content Type | JSON |
| JSON (Expression toggle ON) | `={{ JSON.stringify($json) }}` |

---

### Node 7 (True): fresh token (Code Node)

Gets a fresh Wazuh Manager JWT token for the active response API call:

```javascript
const credentials = Buffer.from('wazuh-wui:wazuh-wui').toString('base64');

const response = await this.helpers.request({
  method: 'POST',
  uri: 'https://192.168.100.33:55000/security/user/authenticate?raw=true',
  headers: {
    'Authorization': `Basic ${credentials}`,
    'Content-Type': 'application/json'
  },
  rejectUnauthorized: false,
});

return { json: { ...$input.item.json, token: response } };
```

> **Why `this.helpers.request()` and not `fetch()`?**
> Two reasons: (1) `fetch()` is not available in n8n's sandboxed Code node runtime. (2) The Wazuh Manager uses a self-signed TLS certificate — `this.helpers.httpRequest()` rejects it. `this.helpers.request()` (Axios-based) supports `rejectUnauthorized: false` to bypass the SSL check on a trusted internal host.

---

### Node 8 (True): Build Response (Code Node)

Maps the AI decision, confidence score, and MITRE tactic to the correct Wazuh active response command and timeout:

```javascript
const ai     = $('If').item.json;
const token  = $input.item.json.token;

const action     = ai.playbook?.recommended_action || "MONITOR_ONLY";
const threatLevel = ai.playbook?.threat_level || "UNKNOWN";
const confidence  = ai.playbook?.confidence || 0;
const srcIp      = ai.playbook?.host_ip || "0.0.0.0";
const agentId    = ai.agent?.id || "001";
const tactic     = ai.playbook?.details?.tactic || "Unknown";

let command = "firewall-drop0";
let timeout = 600;

// Primary mapping: threat level + confidence
if (threatLevel === "APPROVED_RESPONSE" && confidence > 0.85) {
  if (action.includes("KILL_PROCESS"))         { command = "firewall-drop0";   timeout = 3600;  }
  else if (action.includes("ISOLATE_HOST"))    { command = "host-deny0";       timeout = 7200;  }
  else if (action.includes("DISABLE_ACCOUNT")) { command = "disable-account0"; timeout = 86400; }
  else if (action.includes("BLOCK"))           { command = "firewall-drop0";   timeout = 3600;  }
  else                                         { command = "firewall-drop0";   timeout = 1800;  }
}
else if (threatLevel === "NEEDS_HUMAN_REVIEW" && confidence > 0.5) {
  command = "firewall-drop0"; timeout = 600;
}
else {
  command = "firewall-drop0"; timeout = 300;
}

// Tactic-based override
if (tactic === "Credential Access" || tactic === "Brute Force") {
  command = "firewall-drop0";
  if (confidence > 0.8) timeout = 7200;
}
else if (tactic === "Lateral Movement")                    { command = "host-deny0";  timeout = 3600;  }
else if (tactic === "Exfiltration" || tactic === "Impact") { command = "host-deny0";  timeout = 86400; }

return {
  json: {
    token,
    response_body: {
      command: command,
      arguments: ["srcip", srcIp, "timeout", timeout.toString()],
      alert: { data: { srcip: srcIp } }
    },
    response_summary: {
      command,
      timeout_seconds: timeout,
      reason: `AI: ${threatLevel} | Action: ${action} | Confidence: ${confidence} | Tactic: ${tactic}`,
      source_ip: srcIp
    }
  }
};
```

> **Why `firewall-drop0` not `firewall-drop`?** Wazuh internally renames active response commands by appending an index. Run `sudo /var/ossec/bin/agent_control -L` on the Manager to see the exact registered names.

---

### Node 9 (True): Wazuh Active Response (HTTP Request)

| Setting | Value |
|---------|-------|
| Method | `PUT` |
| URL | `https://192.168.100.33:55000/active-response` |
| Send Headers | ON |
| Header `Authorization` | `Bearer {{ $json.token }}` |
| Header `Content-Type` | `application/json` |
| Send Body | ON |
| Body Content Type | JSON |
| JSON (Expression toggle ON) | `={{ JSON.stringify($json.response_body) }}` |
| Options → Ignore SSL Issues | ON |

---

### Node 10 (True): Edit Fields

Switch to **JSON mode** and paste:

```json
{
  "decision":      "{{ $('If').item.json.decision }}",
  "confidence":    "{{ $('If').item.json.playbook.confidence }}",
  "action":        "{{ $('If').item.json.playbook.recommended_action }}",
  "threat_level":  "{{ $('If').item.json.playbook.threat_level }}",
  "tactic":        "{{ $('If').item.json.playbook.details.tactic }}",
  "technique":     "{{ $('If').item.json.playbook.details.technique_id }}",
  "mitigation":    "{{ $('If').item.json.playbook.details.mitigation }}",
  "source_ip":     "{{ $('If').item.json.playbook.host_ip }}",
  "alert_id":      "{{ $('If').item.json.playbook.alert_id }}",
  "stix_bundle_id":"{{ $('STIX').item.json.id }}",
  "blockchain_id": "{{ $('Blockchain').item.json.blockchain_id }}",
  "ipfs_cid":      "{{ $('Blockchain').item.json.ipfs_cid }}",
  "hash":          "{{ $('Blockchain').item.json.hash }}",
  "wazuh_response":"{{ $('Build Response').item.json.response_summary.command }}",
  "timestamp":     "{{ $now.toISO() }}"
}
```

> **Field name note:** The field names here (`decision`, `ipfs_cid`, `wazuh_response`, `source_ip`) must match exactly what the `file` node sends to `/n8n-log` and what `api.py`'s `/chat` endpoint reads. A mismatch causes the chatbot to return "N/A" for all values.

---

### Node 11 (True): file (HTTP Request — Log to AI Chatbot)

| Setting | Value |
|---------|-------|
| Method | `POST` |
| URL | `http://192.168.100.34:8000/n8n-log` |
| Send Body | ON |
| Body Content Type | JSON |
| JSON (Expression toggle ON) | `={{ JSON.stringify($json) }}` |

This logs the complete execution summary to the AI API, which appends it to `n8n_executions.jsonl`. The chatbot reads the last 5 entries as RAG context for every `/chat` request.

---

### Publish the Workflow

Click **Save** → click the **Activate** toggle (top-right). The workflow only receives live Wazuh alerts when it is active.

---

## 11. Component 7 — IPFS Decentralized Storage

**Machine:** Ubuntu Agent (`192.168.100.34`)

```bash
docker run -d --name ipfs_node \
  -p 4001:4001 \
  -p 5001:5001 \
  -p 8080:8080 \
  ipfs/kubo:latest

# Verify
docker ps | grep ipfs
curl http://localhost:5001/api/v0/version

# Open firewall ports
sudo ufw allow 4001/tcp comment "IPFS swarm"
sudo ufw allow 5001/tcp comment "IPFS API"
sudo ufw allow 8080/tcp comment "IPFS Gateway"
```

Every STIX bundle is uploaded to IPFS before blockchain storage. The Content Identifier (CID) returned is recorded in the Hyperledger Fabric transaction, creating a tamper-evident link between the blockchain record and the full threat intelligence data.

---

## 12. Component 8 — Hyperledger Fabric Blockchain

**Machine:** Ubuntu Agent (`192.168.100.34`)

### 12.1 Prerequisites

```bash
sudo apt update && sudo apt install jq git -y

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v    # must be v18+
npm -v
```

### 12.2 Download Fabric (takes 5–10 min)

```bash
mkdir -p ~/project/blockchain && cd ~/project/blockchain
curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/bootstrap.sh | bash -s
```

### 12.3 Start the network

```bash
cd ~/project/blockchain/fabric-samples/test-network
./network.sh down
./network.sh up createChannel -ca
```

Verify containers are running:
```bash
docker ps | grep -E "peer0|orderer|ca_"
```

You must see: `orderer.example.com`, `peer0.org1.example.com`, `peer0.org2.example.com`, `ca_org1`, `ca_org2`, `ca_orderer`.

> **Note:** The anchor peer step may print `Error: can't read the block: &{NOT_FOUND}` — this is non-critical. Both peers have already joined the channel. Continue to chaincode deployment.

### 12.4 Create the ThreatIntel smart contract

```bash
cd ~/project/blockchain/fabric-samples
mkdir threat-intel-chaincode && cd threat-intel-chaincode
npm init -y
npm install fabric-contract-api fabric-shim
```

Edit `package.json` → add to `"scripts"`:
```json
"start": "fabric-chaincode-node start"
```

Create `index.js`:

```javascript
'use strict';
const { Contract } = require('fabric-contract-api');

class ThreatIntelContract extends Contract {

    async initLedger(ctx) {
        console.log('ThreatIntel Ledger Initialized');
        return 'Ledger Ready';
    }

    // IMPORTANT: Never use new Date() inside chaincode.
    // Both peers execute independently — different timestamps → endorsement mismatch.
    // Always pass timestamp as an argument and use it directly.
    async recordAlert(ctx, alertId, severity, agentName, ipfsCid, timestamp) {
        const alert = {
            alertId,
            severity,
            agentName,
            ipfsCid,
            timestamp,
            recordedAt: timestamp    // use the passed value, NOT new Date()
        };
        await ctx.stub.putState(alertId, Buffer.from(JSON.stringify(alert)));
        console.log(`Alert ${alertId} recorded on blockchain`);
        return JSON.stringify(alert);
    }

    async getAlert(ctx, alertId) {
        const data = await ctx.stub.getState(alertId);
        if (!data || data.length === 0) {
            throw new Error(`Alert ${alertId} not found`);
        }
        return data.toString();
    }

    async getAllAlerts(ctx) {
        const iterator = await ctx.stub.getStateByRange('', '');
        const results  = [];
        let result = await iterator.next();
        while (!result.done) {
            results.push(JSON.parse(result.value.value.toString()));
            result = await iterator.next();
        }
        return JSON.stringify(results);
    }
}

module.exports = { contracts: [ThreatIntelContract] };
```

### 12.5 Pull missing image and deploy

```bash
docker pull hyperledger/fabric-nodeenv:2.5

cd ~/project/blockchain/fabric-samples/test-network

./network.sh deployCC \
  -ccn threatintel \
  -ccp ../threat-intel-chaincode \
  -ccl javascript
```

> **If deployment fails** with `orderer system channel is not defined`: run `./network.sh down`, wait 10 seconds, then `./network.sh up createChannel -ca` again before retrying `deployCC`.

> **Redeploying after a code fix** (e.g. after fixing the `new Date()` endorsement bug): use `-ccv 2.0 -ccs 2` to bump the version and sequence number:
> ```bash
> ./network.sh deployCC -ccn threatintel -ccp ../threat-intel-chaincode -ccl javascript -ccv 2.0 -ccs 2
> ```

### 12.6 Initialize the ledger (warms up chaincode containers)

```bash
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile ${PWD}/organizations/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem \
  -C mychannel \
  -n threatintel \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
  -c '{"function":"initLedger","Args":[]}'
```

After this, two chaincode containers start:
```bash
docker ps | grep threatintel
# dev-peer0.org1.example.com-threatintel_...
# dev-peer0.org2.example.com-threatintel_...
```

---

## 13. Component 9 — Blockchain Connector API

**Machine:** Ubuntu Agent (`192.168.100.34`)

### 13.1 Setup project

```bash
mkdir -p ~/project/blockchain/blockchain-connector && cd ~/project/blockchain/blockchain-connector
npm init -y
npm install express fabric-network fabric-ca-client kubo-rpc-client dotenv
sed -i 's/"main": "index.js"/"main": "index.js",\n  "type": "module"/' package.json
```

### 13.2 Create `.env`

```bash
cat > .env << 'EOF'
PORT=3005
CHANNEL_NAME=mychannel
CHAINCODE_NAME=threatintel
USER_ID=appUser
IPFS_URL=http://127.0.0.1:5001
EOF
```

### 13.3 Copy connection file and create wallet directory

```bash
cp ~/project/blockchain/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/connection-org1.json ./connection-org1.json
mkdir wallet
```

### 13.4 Create `server.js`

```javascript
'use strict';

import 'dotenv/config';
import express from 'express';
import { Gateway, Wallets } from 'fabric-network';
import { create } from 'kubo-rpc-client';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const app  = express();
app.use(express.json({ limit: '10mb' }));

const ipfs = create({ url: process.env.IPFS_URL || 'http://127.0.0.1:5001' });

async function getContract() {
    const ccpPath = path.resolve(__dirname, 'connection-org1.json');
    const ccp     = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));
    const wallet  = await Wallets.newFileSystemWallet(path.join(process.cwd(), 'wallet'));
    const gateway = new Gateway();
    await gateway.connect(ccp, {
        wallet,
        identity:  process.env.USER_ID || 'appUser',
        discovery: { enabled: true, asLocalhost: true }
    });
    const network = await gateway.getNetwork(process.env.CHANNEL_NAME || 'mychannel');
    return {
        contract: network.getContract(process.env.CHAINCODE_NAME || 'threatintel'),
        gateway
    };
}

app.get('/api/v1/health', (req, res) => {
    res.json({
        status:    'ok',
        service:   'SetChain Blockchain Connector',
        ipfs:      process.env.IPFS_URL,
        channel:   process.env.CHANNEL_NAME,
        chaincode: process.env.CHAINCODE_NAME
    });
});

app.post('/api/v1/alerts', async (req, res) => {
    try {
        const alertData = req.body;
        const alertId   = alertData.id || `ALERT_${Date.now()}`;
        const dataStr   = JSON.stringify(alertData);
        const dataHash  = crypto.createHash('sha256').update(dataStr).digest('hex');

        // Upload to IPFS
        let ipfsCID = 'IPFS_UNAVAILABLE';
        try {
            const { cid } = await ipfs.add(dataStr);
            ipfsCID = cid.toString();
            console.log(`[IPFS] CID: ${ipfsCID}`);
        } catch (e) {
            console.warn(`[IPFS] Upload failed: ${e.message} — continuing`);
        }

        // Record on Hyperledger Fabric
        const { contract, gateway } = await getContract();
        const timestamp = new Date().toISOString();

        await contract.submitTransaction(
            'recordAlert',
            alertId,
            (alertData.objects?.[0]?.x_setchain_confidence || 'unknown').toString(),
            (alertData.objects?.[0]?.name || 'Unknown Threat').toString(),
            `IPFS_CID:${ipfsCID}|HASH:${dataHash}`,
            timestamp
        );
        await gateway.disconnect();

        console.log(`[✓] Alert ${alertId} secured on blockchain`);

        res.status(200).json({
            success:       true,
            message:       'Alert secured on blockchain + IPFS',
            blockchain_id: alertId,
            ipfs_cid:      ipfsCID,
            hash:          dataHash,
            timestamp
        });

    } catch (error) {
        console.error(`[✗] Failed: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3005;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🔗 Blockchain Connector running on http://0.0.0.0:${PORT}`);
});
```

### 13.5 Enroll identities

```bash
node enrollAdmin.cjs
node registerUser.cjs
```

> **Important:** After every `./network.sh down` + `./network.sh up`, the old wallet is invalid (new CA instances are created). You must re-enroll:
> ```bash
> rm -rf wallet && mkdir wallet
> cp ~/project/blockchain/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/connection-org1.json ./connection-org1.json
> node enrollAdmin.cjs
> node registerUser.cjs
> ```

### 13.6 Create systemd service

```bash
sudo bash -c "cat > /etc/systemd/system/setchain-blockchain.service << 'EOF'
[Unit]
Description=SetChain Blockchain Connector
After=network.target

[Service]
Type=simple
User=agent
WorkingDirectory=/home/agent/project/blockchain/blockchain-connector
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable setchain-blockchain
sudo systemctl start setchain-blockchain
sudo ufw allow 3005/tcp comment "SetChain Blockchain Connector"
```

### 13.7 Verify

```bash
curl http://localhost:3005/api/v1/health

curl -s -X POST http://localhost:3005/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "bundle",
    "id": "bundle-test-001",
    "objects": [{"name": "SSH Brute Force Attempt", "x_setchain_confidence": 0.88}]
  }' | python3 -m json.tool
```

**Expected:**
```json
{
    "success": true,
    "message": "Alert secured on blockchain + IPFS",
    "blockchain_id": "bundle-test-001",
    "ipfs_cid": "QmXxx...",
    "hash": "abc123...",
    "timestamp": "2026-05-25T..."
}
```

---

## 14. Component 10 — AI Chatbot (RAG Integration)

The chatbot reads live n8n execution logs and can answer questions about pipeline activity in natural language.

### 14.1 `/n8n-log` endpoint in api.py

Appends every n8n execution summary to a JSONL file:

```python
import os, json

N8N_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n_executions.jsonl")

@app.post("/n8n-log")
def log_n8n_execution(data: dict):
    try:
        with open(N8N_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        return {"status": "success", "message": "Log saved"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_n8n_executions():
    """Returns the last 5 n8n execution records for RAG context."""
    if not os.path.exists(N8N_LOG_FILE):
        return []
    logs = []
    try:
        with open(N8N_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except Exception:
                        pass
    except Exception:
        pass
    return logs[-5:]
```

### 14.2 `/chat` endpoint with n8n RAG context

```python
@app.post("/chat")
def smart_chat(data: ChatInput):
    n8n_execs = get_n8n_executions()
    n8n_text  = ""

    if n8n_execs:
        n8n_text = "\nRECENT N8N WORKFLOW EXECUTIONS:\n"
        for i, ex in enumerate(n8n_execs):
            # Field names must match EXACTLY what n8n's Edit Fields node sends
            n8n_text += f"  Execution #{i+1} | Time: {ex.get('timestamp', 'N/A')}\n"
            n8n_text += f"    Alert: {ex.get('alert_id', 'N/A')} | Source IP: {ex.get('source_ip', 'N/A')}\n"
            n8n_text += f"    AI Decision: {ex.get('decision', 'N/A')} (Confidence: {ex.get('confidence', 'N/A')})\n"
            n8n_text += f"    Action: {ex.get('action', 'N/A')} | Threat Level: {ex.get('threat_level', 'N/A')}\n"
            n8n_text += f"    Tactic: {ex.get('tactic', 'N/A')} | Technique: {ex.get('technique', 'N/A')}\n"
            if ex.get("ipfs_cid"):
                n8n_text += f"    Blockchain CID: {ex.get('ipfs_cid')}\n"
            if ex.get("wazuh_response"):
                n8n_text += f"    Active Response: {ex.get('wazuh_response')}\n"

    # n8n_text is injected into the Groq LLM system prompt
    # so the model can answer questions about live pipeline activity
```

### 14.3 Start the chatbot manually

```bash
cd ~/project/ai-models/Project/gradModel
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
```

### 14.4 Test the chatbot

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "trace the last alert through the pipeline. tell me the blockchain CID and wazuh response."}' \
  | python3 -m json.tool
```

---

## 15. Wazuh Active Response Configuration

**Machine:** Wazuh Manager (`192.168.100.33`)

### 15.1 Verify `<command>` blocks in ossec.conf

The following command blocks must exist (they are included in the default Wazuh Manager installation):

```xml
<command>
  <name>disable-account</name>
  <executable>disable-account</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<command>
  <name>host-deny</name>
  <executable>host-deny</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>
```

### 15.2 Add the `<active-response>` registration block

Without this block, the command exists but is never registered as an active response — and the API returns error 1652.

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add inside `<ossec_config>` (after the commented-out `<active-response>` block):

```xml
<active-response>
  <command>firewall-drop</command>
  <location>local</location>
</active-response>
```

```bash
sudo systemctl restart wazuh-manager
```

### 15.3 Discover the real command name

Wazuh renames commands by appending an index. Always verify the exact name:

```bash
sudo /var/ossec/bin/agent_control -L
```

Expected output:
```
Wazuh agent_control. Available active responses:

   Response name: firewall-drop0, command: firewall-drop
```

Use `firewall-drop0` everywhere — in the n8n Build Response node and in all test commands.

### 15.4 Test active response directly

```bash
sudo /var/ossec/bin/agent_control -b 45.33.32.156 -f firewall-drop0 -u 001
```

---

## 16. Wazuh ossec.conf Reference

**Machine:** Wazuh Manager (`192.168.100.33`) — `/var/ossec/etc/ossec.conf`

Key sections relevant to this project:

```xml
<ossec_config>

  <global>
    <jsonout_output>yes</jsonout_output>
    <alerts_log>yes</alerts_log>
    <email_notification>no</email_notification>
    <agents_disconnection_time>15m</agents_disconnection_time>
    <update_check>yes</update_check>
  </global>

  <alerts>
    <log_alert_level>3</log_alert_level>
    <email_alert_level>12</email_alert_level>
  </alerts>

  <!-- Active Response commands -->
  <command>
    <name>disable-account</name>
    <executable>disable-account</executable>
    <timeout_allowed>yes</timeout_allowed>
  </command>

  <command>
    <name>firewall-drop</name>
    <executable>firewall-drop</executable>
    <timeout_allowed>yes</timeout_allowed>
  </command>

  <command>
    <name>host-deny</name>
    <executable>host-deny</executable>
    <timeout_allowed>yes</timeout_allowed>
  </command>

  <!-- Active Response registration (required for API to accept requests) -->
  <active-response>
    <command>firewall-drop</command>
    <location>local</location>
  </active-response>

  <!-- Suricata / eve.json integration -->
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/suricata/eve.json</location>
  </localfile>

  <!-- n8n Webhook Integration (smart filter version) -->
  <integration>
    <name>custom-n8n-smart-filter</name>
    <level>3</level>
    <alert_format>json</alert_format>
  </integration>

  <!-- Vulnerability detection -->
  <vulnerability-detection>
    <enabled>yes</enabled>
    <index-status>yes</index-status>
    <feed-update-interval>60m</feed-update-interval>
  </vulnerability-detection>

  <!-- File integrity monitoring -->
  <syscheck>
    <disabled>no</disabled>
    <frequency>43200</frequency>
    <scan_on_start>yes</scan_on_start>
    <alert_new_files>yes</alert_new_files>
    <directories>/etc,/usr/bin,/usr/sbin</directories>
    <directories>/bin,/sbin,/boot</directories>
  </syscheck>

</ossec_config>
```

---

## 17. End-to-End Testing

### Test 1: Full pipeline — ACTION_REQUIRED branch

```bash
curl -s -X POST http://192.168.100.34:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "id": "5712",
      "level": 14,
      "description": "sshd: Multiple failed authentication attempts from a single source",
      "firedtimes": 8,
      "mitre": {
        "tactic": ["Credential Access"],
        "id": ["T1110"],
        "technique": ["Brute Force"]
      }
    },
    "agent": {"id": "001", "name": "ubuntu", "ip": "192.168.100.34"},
    "data": {"srcip": "45.33.32.156", "dstip": "192.168.100.34"},
    "timestamp": "2026-05-25T05:33:00Z"
  }' | python3 -m json.tool
```

In the n8n Executions tab all nodes should be green ✅ with:
- `decision: ACTION_REQUIRED`
- `confidence: 0.88x`
- `ipfs_cid: Qm...`
- `hash: abc123...`
- `wazuh_response: firewall-drop0`

### Test 2: False branch — IGNORE

```bash
curl -X POST http://192.168.100.34:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "id": "5715",
      "level": 3,
      "description": "SSHD successful login from authorized user"
    },
    "agent": {"id": "001", "name": "ubuntu-agent", "ip": "192.168.100.34"},
    "data": {"srcip": "192.168.100.50", "dstip": "192.168.100.34"},
    "timestamp": "2026-05-25T18:01:00Z"
  }'
```

Should take the false branch → No Operation → file log only.

### Test 3: AI API directly

```bash
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "rule": {"id":"5710","level":10,
               "description":"sshd: attempt to login using a denied user",
               "mitre":{"tactic":["Credential Access"],"id":["T1110"]}},
      "agent": {"ip": "192.168.100.34"}
    }
  }' | python3 -m json.tool
```

### Test 4: Blockchain connector directly

```bash
curl -s -X POST http://localhost:3005/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "type": "bundle",
    "id": "bundle-test-002",
    "objects": [{"name": "SSH Brute Force", "x_setchain_confidence": 0.88}]
  }' | python3 -m json.tool
```

### Test 5: Trigger a real alert from Suricata

```bash
# Generates real SSH failed login → Wazuh → smart filter → n8n → full pipeline
for i in {1..8}; do ssh invalid_user@localhost 2>/dev/null || true; done
```

### Test 6: Ask the chatbot

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "trace the last alert through the pipeline. tell me the blockchain CID and wazuh response."}' \
  | python3 -m json.tool
```

### Test 7: Query blockchain directly

```bash
cd ~/project/blockchain/fabric-samples/test-network

export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer chaincode query -C mychannel -n threatintel -c '{"function":"getAllAlerts","Args":[]}'
```

---

## 18. Service Management & Startup Order

### Boot / startup sequence (follow this order after a reboot)

```bash
# 1. Start Suricata (on Agent)
sudo systemctl start suricata

# 2. Start Fabric network (on Agent)
cd ~/project/blockchain/fabric-samples/test-network
./network.sh up createChannel -ca

# 3. Start IPFS (should auto-start if Docker is running)
docker start ipfs_node

# 4. Re-enroll wallet (only needed after network down/up)
cd ~/project/blockchain/blockchain-connector
rm -rf wallet && mkdir wallet
cp ~/project/blockchain/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/connection-org1.json ./connection-org1.json
node enrollAdmin.cjs
node registerUser.cjs

# 5. Start Blockchain Connector (on Agent)
sudo systemctl start setchain-blockchain

# 6. Start AI API (on Agent)
sudo systemctl start setchain-ai

# 7. Start n8n (on Agent)
dstart
# or: cd /opt/n8n && docker compose start

# 8. Restart Wazuh Manager (on Manager — to reload integration scripts)
sudo systemctl restart wazuh-manager
```

### Service management commands

```bash
# n8n (Docker Compose)
dstart                                      # start
dstop                                       # stop
cd /opt/n8n && docker compose restart       # restart
docker logs -f n8n                          # view logs

# AI API (systemd)
sudo systemctl start setchain-ai
sudo systemctl stop setchain-ai
sudo systemctl restart setchain-ai
sudo systemctl status setchain-ai

# Blockchain Connector (systemd)
sudo systemctl start setchain-blockchain
sudo systemctl stop setchain-blockchain
sudo systemctl restart setchain-blockchain
sudo systemctl status setchain-blockchain

# Fabric Network
cd ~/project/blockchain/fabric-samples/test-network
./network.sh down                           # stop all Fabric containers
./network.sh up createChannel -ca           # start fresh

# Suricata
sudo systemctl start suricata
sudo systemctl restart suricata
sudo tail -f /var/log/suricata/eve.json | python3 -m json.tool

# Wazuh (on respective machines)
sudo systemctl restart wazuh-manager        # Manager machine
sudo systemctl restart wazuh-agent          # Agent machine

# Smart filter log (on Manager)
sudo tail -f /var/ossec/logs/n8n-filter.log
```

---

## 19. Problems Encountered & Solutions

### Problem 1 — n8n login page broken (secure cookie)

**Error:** Login page loads but authentication cookies silently fail.  
**Root cause:** n8n v2.21+ sets `N8N_SECURE_COOKIE=true` by default, requiring HTTPS. On plain HTTP the browser refuses to store the session cookie.  
**Fix:** Add `N8N_SECURE_COOKIE=false` to `docker-compose.yml` environment block, then `docker compose down && docker compose up -d`.

---

### Problem 2 — Suricata alert flood (rule 86601)

**Error:** Thousands of duplicate level-3 Suricata `ET INFO pwd= cleartext` alerts flood n8n continuously.  
**Root cause:** The ET INFO rule fires on every HTTP packet containing `pwd=` — including background monitoring traffic that repeats every few seconds.  
**Fix (3-layer):**  
1. Suricata `threshold.config` — max 1 per source IP per 12 hours  
2. Wazuh `local_rules.xml` — throttle rule 86601: frequency=10, timeframe=43200, ignore=43200  
3. Smart Filter `NEVER_FORWARD_RULE_IDS` — always drop 86601 before it reaches n8n

---

### Problem 3 — `fetch is not defined` in n8n Code node

**Error:** `ReferenceError: fetch is not defined`  
**Root cause:** n8n's sandboxed JavaScript runtime does not include the global `fetch()` API.  
**Fix:** Use `this.helpers.request()` (Axios-based helper that n8n exposes in Code nodes).

---

### Problem 4 — Self-signed certificate error (Wazuh Manager TLS)

**Error:** `Error: self-signed certificate in certificate chain`  
**Root cause:** Wazuh Manager uses a self-signed TLS certificate. `this.helpers.httpRequest()` and browser `fetch()` both reject it with no bypass option.  
**Fix:** Use `this.helpers.request()` with `rejectUnauthorized: false`. For HTTP Request nodes, enable **Ignore SSL Issues** under Options.

---

### Problem 5 — `{{ $json }}` renders as `[object Object]`

**Error:** AI API receives `{"alert": "[object Object]"}` and returns a parse error.  
**Root cause:** In n8n's plain JSON mode, `$json` is serialized as a literal string rather than the actual JSON object.  
**Fix:** Click the **Expression toggle (fx)** on the JSON field and use `={{ JSON.stringify({ "alert": $json }) }}`.

---

### Problem 6 — Wazuh Error 1652 — command not defined

**Error:** Wazuh API returns `1652 — The command used is not defined in the configuration`.  
**Root cause:** The `<command>` block exists in `ossec.conf` but no `<active-response>` block registers it as an active response.  
**Fix:** Add `<active-response><command>firewall-drop</command><location>local</location></active-response>` to `ossec.conf` and restart the manager.

---

### Problem 7 — `Selected active response does not exist`

**Error:** `agent_control -f firewall-drop` says "does not exist."  
**Root cause:** Wazuh internally renames active response commands by appending an index number. `firewall-drop` becomes `firewall-drop0`.  
**Fix:** Run `sudo /var/ossec/bin/agent_control -L` to see the exact registered name, then use `firewall-drop0` everywhere.

---

### Problem 8 — Invalid field `{'custom'}` (Wazuh API 400)

**Error:** Wazuh API returns HTTP 400 with `Invalid field found {'custom'}`.  
**Root cause:** Attempted to include `"custom": true` in the active response JSON body. This field is not supported in the installed Wazuh version.  
**Fix:** Remove the `custom` field entirely. The correct body is `{"command": "firewall-drop0", "arguments": [...], "alert": {...}}`.

---

### Problem 9 — `={"command"...` is not valid JSON

**Error:** `Unexpected token '=', "={"command"... is not valid JSON`  
**Root cause:** n8n expression syntax uses `={{ ... }}` — the `=` is a toggle marker, not part of the value. When the field is in Expression mode, the actual expression starts with `{{`, not `={{`.  
**Fix:** Remove the leading `=`. The JSON body value should be `{{ JSON.stringify($json.response_body) }}`.

---

### Problem 10 — Chatbot ignores n8n execution data (field name mismatch)

**Error:** AI chatbot returns "no recent executions" or "N/A" for all values even though n8n is logging correctly.  
**Root cause:** The `api.py` `/chat` endpoint was reading field names that don't match what n8n's Edit Fields node actually sends:

| n8n actually sends | api.py originally expected |
|--------------------|---------------------------|
| `decision` | `ai_decision` |
| `ipfs_cid` | `blockchain_cid` |
| `wazuh_response` | `active_response` |
| `source_ip` | `src_ip` |

**Fix:** Updated `get_n8n_executions()` in `api.py` to read the exact field names that n8n sends.

---

### Problem 11 — Blockchain `Peer endorsements do not match`

**Error:** `No valid responses from any peers. Errors: Peer endorsements do not match`  
**Root cause 1 (non-determinism):** Chaincode used `new Date().toISOString()` inside `recordAlert()`. Both peers execute independently and get different timestamps → their state changes differ → endorsements don't match.  
**Root cause 2 (incomplete install):** Chaincode only installed on one peer, or network not cleanly initialized.  
**Fix 1:** Replace `recordedAt: new Date().toISOString()` with `recordedAt: timestamp` (use the value passed as a function argument — deterministic across both peers).  
**Fix 2:** `./network.sh down` → `docker system prune -f` → `./network.sh up createChannel -ca` → re-deploy with `-ccv 2.0 -ccs 2`.

---

### Problem 12 — Windows venv on Linux

**Error:** `bash: venv/bin/activate: No such file or directory`  
**Root cause:** Python virtual environment was created on Windows. Windows venvs have `Scripts/` instead of `bin/`.  
**Fix:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

---

### Problem 13 — Blockchain wallet invalid after network restart

**Error:** Identity errors after restarting the Fabric network: `WALLET: appUser identity not found` or certificate verification failures.  
**Root cause:** Wallet credentials are cryptographically tied to a specific CA instance. `./network.sh down` destroys all containers including the CAs. New containers start new CAs with new certificates — the old wallet is completely invalid.  
**Fix:** After every network restart, delete the wallet and re-enroll:
```bash
rm -rf wallet && mkdir wallet
cp <new-connection-org1.json path> ./connection-org1.json
node enrollAdmin.cjs
node registerUser.cjs
```

---

## 20. Quick Reference

### Service URLs

| Service | URL | Machine |
|---------|-----|---------|
| n8n UI | http://192.168.100.34:5678 | Agent |
| AI API — health | http://192.168.100.34:8000/health | Agent |
| AI API — analyze | http://192.168.100.34:8000/analyze | Agent |
| AI API — chat | http://192.168.100.34:8000/chat | Agent |
| AI API — n8n log | http://192.168.100.34:8000/n8n-log | Agent |
| Blockchain API — health | http://192.168.100.34:3005/api/v1/health | Agent |
| Blockchain API — alerts | http://192.168.100.34:3005/api/v1/alerts | Agent |
| IPFS API | http://192.168.100.34:5001/api/v0/version | Agent |
| IPFS Gateway | http://192.168.100.34:8080 | Agent |
| Wazuh Manager API | https://192.168.100.33:55000 | Manager |

### Key File Locations

| File | Path | Machine |
|------|------|---------|
| n8n Docker Compose | `/opt/n8n/docker-compose.yml` | Agent |
| AI API | `~/project/ai-models/Project/gradModel/api.py` | Agent |
| AI config | `~/project/ai-models/Project/gradModel/setchain-chatbot/config.py` | Agent |
| n8n execution logs | `~/project/ai-models/Project/gradModel/n8n_executions.jsonl` | Agent |
| Blockchain server | `~/project/blockchain/blockchain-connector/server.js` | Agent |
| Blockchain wallet | `~/project/blockchain/blockchain-connector/wallet/` | Agent |
| Fabric connection file | `~/project/blockchain/blockchain-connector/connection-org1.json` | Agent |
| ThreatIntel chaincode | `~/project/blockchain/fabric-samples/threat-intel-chaincode/index.js` | Agent |
| Wazuh ossec.conf | `/var/ossec/etc/ossec.conf` | Manager |
| Smart filter script | `/var/ossec/integrations/n8n-smart-filter.py` | Manager |
| Smart filter log | `/var/ossec/logs/n8n-filter.log` | Manager |
| Basic forwarder | `/var/ossec/integrations/custom-n8n` | Manager |
| Suricata config | `/etc/suricata/suricata.yaml` | Agent |
| Suricata threshold | `/etc/suricata/threshold.config` | Agent |
| Suricata alerts | `/var/log/suricata/eve.json` | Agent |
| Wazuh local rules | `/var/ossec/etc/rules/local_rules.xml` | Manager |
| Wazuh logs | `/var/ossec/logs/ossec.log` | Manager |

### Wazuh Alert Level Reference

| Level | Meaning | Forwarded to n8n? |
|-------|---------|-------------------|
| 0–2 | Debug / informational | Never |
| 3–6 | Low / informational | Yes (unless NEVER_FORWARD list) |
| 7–9 | Medium — worth attention | Yes |
| 10–12 | High severity | Yes |
| 13–15 | Critical | Yes — bypasses all rate limits |

### AI Decision Reference

| decision | meaning |
|----------|---------|
| `ACTION_REQUIRED` | Threat confirmed — take the true branch (STIX → Blockchain → Active Response) |
| `IGNORE` | Low confidence or benign — take the false branch (log only) |

| threat_level | meaning |
|--------------|---------|
| `APPROVED_RESPONSE` | High confidence — execute active response automatically |
| `NEEDS_HUMAN_REVIEW` | Medium confidence — light response, flag for analyst review |

---

*SetChain — Wazuh · Suricata · n8n · FastAPI · Hyperledger Fabric · IPFS · STIX 2.1 · Groq LLaMA 3*
