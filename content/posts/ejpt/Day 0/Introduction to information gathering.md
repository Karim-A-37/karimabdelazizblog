---

---
---

title: "Introduction to Information Gathering" date: 2026-05-01 draft: false tags:

- ejpt
- recon
- reconnaissance
- passive-recon
- active-recon
- pentesting

---

## Information Gathering (Reconnaissance)

Reconnaissance is the first phase in a penetration testing operation. The goal is to collect or gather information that is publicly available (**passive reconnaissance**) or not publicly available (**active reconnaissance**) about an organization, individual, system, or website — essentially anything about our target.

### Types of Information Gathering

- **Passive information gathering** → collect information that is publicly available without any active engagement with the target (IP and DNS information, domain names, web technologies, subdomains, etc.)
- **Active information gathering** → collecting information that isn't publicly available, requires direct engagement with the target (needs authorization) — port scanning, internal network infrastructure info, enumeration of gathered information.

---

## Target Scoping (In-Scope vs Out-Scope)

Target scoping is the process of defining what systems, apps, and networks are allowed to be tested. It is the **rules of engagement** — what am I allowed to collect information about?

During reconnaissance, the target is defined via one of these ways:

1. **Domain based target** — may include primary domain or subdomain (e.g. `example.com` or `admin.example.com`)
2. **IP based target** — common in internal or lab environments, single IP (`192.168.1.1`) or network range (`192.168.1.0/24`)
3. **Application based target** — focus on app only, not the entire server (web app, login portal, or specific API endpoint)

### In-Scope vs Out-Scope

||Definition|
|---|---|
|**In-Scope**|Assets I am allowed to collect info from, scan, and enumerate|
|**Out-Scope**|Assets I am NOT allowed to test — third party services, external domains not listed in scope, systems owned by other organizations|

![scope.png](/images/Introduction to information gathering/scope.png)

> Reconnaissance is about collecting **useful** information, not all information. A well-defined scope keeps reconnaissance focused, efficient, and relevant to later stages.

---

## Passive vs Active Reconnaissance (In Detail)

### 1. Passive Reconnaissance

Collect information that is publicly available **without any direct interaction** with the target.

- Usually performed **first**
- **Lower risk** of detection
- Examples of passive recon data:
    1. DNS Records
    2. Domain registration information
    3. Public website content
    4. Search engine results (Google Dorking — using special search operators to find non-obvious information)
    5. Publicly available email addresses

### 2. Active Reconnaissance

Collecting information by **directly engaging** with the target — sends traffic to target, increases visibility.

- Performed **after** passive recon
- Examples of active recon data:
    1. Live hosts
    2. Open ports (using Nmap)
    3. Running services
    4. Network responses

> **Hint:** Always perform passive reconnaissance before active reconnaissance.

---

## Building a Map of the Target

During information gathering we are trying to **build a map of the target**. Examples of the information we collect:

1. Domains and Subdomains
2. IP addresses
3. Hosting Infrastructure
4. Technologies and services (used web technologies)
5. Open ports
6. Publicly exposed information

![recon mapping flow.png](/images/Introduction to information gathering/recon%20mapping%20flow.png)

### Recon Flow

1. Define the target scope (In-Scope and Out-Scope)
2. Start **passive reconnaissance** — domains, subdomains, DNS records, WHOIS data[^1], website footprinting[^2], OSINT techniques
3. Start **active reconnaissance** — host discovery, port scanning, basic service identification, DNS zone transfer testing
4. Organize and optimize the findings
5. Begin enumeration and exploitation

---

## Recon Strategy (Simple Definition)

**Step 1 — Define the Target**

- Define IP addresses, domains, network ranges
- Define In-Scope and Out-Scope

**Step 2 — Passive Reconnaissance**

- Gather public info
- Define potential attack surfaces (what is capable of being attacked)
- Build initial understanding of the target

**Step 3 — Active Reconnaissance**

- Identify live hosts
- Identify open ports
- Detect exposed services

**Step 4 — Document and Organize Findings**

- Record domains, IPs, ports
- Prepare information for enumeration
- Avoid repeating work later

---

## Common Mistakes to Avoid

1. Starting scanning without defining scope
2. Skipping passive recon
3. Scanning everything instead of only what is relevant to the target
4. Not documenting results
5. Trusting tools output without verification

> Avoiding these mistakes increases accuracy and efficiency.

---

## Key Takeaways

1. Target scoping defines what you are allowed to test
2. Passive recon comes before active recon
3. **Reconnaissance** is about gathering **meaningful data**
4. A structured and documented approach improves results and efficiency

> **Hint:** Always avoid gathering all info about the target — try to get only **useful** info about in-scope targets. Quality over quantity.

---

[^1]: **WHOIS** is a request and response protocol (RFC 3912). A WHOIS server listens on TCP port 43 for incoming requests. The domain registrar maintains the WHOIS records. Key info returned includes: Registrar, Contact info of registrant, Creation/update/expiration dates, and Name Servers.

[^2]: **Footprinting** is the art of gathering essential information from target organizations about their networks and systems for potential vulnerabilities. Can be passive or active footprinting.