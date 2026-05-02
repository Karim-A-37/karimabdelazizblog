---
title: "Introduction to information gathering"
date: 2026-05-01
slug: "introduction-to-information-gathering"
draft: false
tags:
  - ejpt
  - recon
---

# Information Gathering (Reconnaissance)

Reconnaissance is the first phase in penetration testing operation and is to collect or gather information that is public available (passive reconnaissance) or private (active reconnaissance) about organization or individual or system or website and so on (information about our target)

## Types of Reconnaissance

1. **Passive information gathering** → collect information that is public available without any active engaging with the target (IP and DNS information - Domain names - web technologies - subdomains and so on)
2. **Active information gathering** → collecting information that isn't public available with active engaging with the target (need authorization from target) (port scanning - information about internal network infrastructure - enumeration of gathered information)

---
## Target Scoping (In-Scope - Out-Scope)

Target scoping is the process of defining what systems, apps and networks are allowed to test or not to test, it is the rules of engaging (what am i allowed to collect information about?), during reconnaissance the target is defined via one of those ways:

|Type|Description|Example|
|---|---|---|
|**Domain based target**|may include primary domain or subdomain|`example.com` or `admin.example.com`|
|**IP based target**|common in internal or lab environments|single IP `192.168.1.1` or network range `192.168.1.0/24`|
|**Application based target**|focus on app only not the entire server|web app or login portal or specific API endpoint|

### In-Scope vs Out-Scope

- **In Scope** → assets i allowed to (collect info from - scan - enumerate)
- **Out Scope** → assets i am not allowed to test or interact with (third party services - external domains not listed in scope - systems owned by other organization)

![scope](/images/ejpt/day-0/introduction-to-information-gathering/scope.png)

> Reconnaissance is about collecting useful information not all information with well defined scope i keep reconnaissance focused and efficient and relevant to later stages.

---
## Passive vs Active Reconnaissance

### 1. Passive Reconnaissance

Collect information that is public available without any active engaging with the target, without direct interaction with the target, usually performed first and lower risk of detection.

**Examples of passive recon data:**

- DNS Records
- Domain registration information
- Public website content
- Search engines results (Google Dorking → techniques to gather info using special words in searching process to get information that is not common to get)
- Public available email addresses

### 2. Active Reconnaissance

Collecting information that isn't public available with active engaging with the target, sends traffic to target, increase visibility, performed after passive recon.

**Examples of active recon data:**

- live hosts
- open ports (using N-map)
- running services
- network responses

> [!tip] Hint Always perform passive reconnaissance before active reconnaissance.

---
## Building a Map of the Target

During info gathering we are trying ==to build map of target==, examples of those information:

- Domains and Subdomains
- IP addresses
- Hosting Infrastructure
- Technologies and services (used web technologies)
- Open ports
- Publicly exposed information

![recon157](/images/ejpt/day-0/introduction-to-information-gathering/recon.png)

---
## Reconnaissance Flow

1. Start by defining the target scope (In-scope and Out-scope)
2. Starting the passive reconnaissance (domains - subdomains - DNS records - [^1]WHOIS data - [^2]website footprinting - OSINT techniques)
3. After the passive recon we start the active reconnaissance (host discovery - port scanning - basic service identification - DNS zone transfer testing)
4. Optimize the findings
5. Start the enumeration and exploitation

---
## Recon Strategy

### 1. Define the Target

- Define IP addresses, domains, network ranges
- Define In-scope and Out-scope

### 2. Perform Passive Reconnaissance

- Gather public info
- Define potential attack surfaces (what is capable to be attacked)
- Build initial understanding of target

### 3. Perform Active Reconnaissance

- Define live hosts
- Define open ports
- Detect exposed services

### 4. Document and Organize the Findings

- Record domains, IPs, ports
- Prepare information for enumeration
- Avoid repeating work later

---
## Common Mistakes to Avoid

> [!warning] Mistakes to Avoid
> 
> 1. Starting scanning without defining scope
> 2. Skipping passive recon
> 3. Scanning everything instead of relevant to target
> 4. Not documenting results
> 5. Trusting tools output without verification

By avoiding those mistakes the accuracy will increased.

---
## Key Takeaways

> [!tip] Hint Always avoid to gather all info about the target try to get only useful info about in scope only (not quantity but useful)

1. Target scoping defines what you are allowed to test
2. Passive recon comes before active recon
3. ==Reconnaissance== is about gathering ==meaningful data==
4. A structured and documented approach improves results and efficiency

---
## Footnotes

[^1]: WHOIS is a request and response protocol that follows the [RFC 3912](https://www.ietf.org/rfc/rfc3912.txt) specification. A WHOIS server listens on TCP port 43 for incoming requests. The domain registrar is responsible for maintaining the WHOIS records for the domain names it is leasing. The WHOIS server replies with various information related to the domain requested. Of particular interest, we can learn: - Registrar: Via which registrar was the domain name registered? - Contact info of registrant: Name, organization, address, phone, among other things. (unless made hidden via a privacy service) - Creation, update, and expiration dates: When was the domain name first registered? When was it last updated? And when does it need to be renewed? - Name Server: Which server to ask to resolve the domain name?

[^2]: Footprinting is the art of gathering essential information from target organizations about their networks and systems for potential vulnerabilities, can be passive Footprinting or active Footprinting