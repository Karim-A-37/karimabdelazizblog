---
title: "Active Reconnaissance"
date: 2026-05-08
slug: active-reconnaissance
draft: false
tags:
  - ejpt
  - recon
---

  

# Active Reconnaissance

  

We have already discussed passive reconnaissance, but now we are going to talk about active reconnaissance, active recon means gathering information by engaging with the target not like passive which gather public info, sending and receiving packets or other things to the target like DNS transfer zone and scanning ports with Nmap.

  

---

  

## 1. DNS Zone Reconnaissance

  

We have discussed before in passive reconnaissance about DNS and how it actually it works in details, it is protocol mostly used to transfer hostnames into their corresponding IP addresses, as we said before it contains about several records each record is responsible to display specific information like:

  

1. **NS** → Name Server which contain Name servers that if client asked about specific domain then it will be forwarded to those specific name servers that related to that specific domain, every domain needs at least two NS records for redundancy

2. **A** → to transfer the hostname into its corresponding IPv4

  

And so on you can find all famous records and their usage inside passive reconnaissance section, now we will discuss something called DNS zones.

  

### 1.1 What is a DNS Zone?

  

DNS Zone is logical (not physical separation it is just logical separation) entity within domain namespace of DNS used to provide more control to admin, org or other legal entity responsible for managing it, so we can say it is part of the domain system that one person or organization is responsible for managing, so we split DNS into logical parts called zones so different admins or organizations can control their specific zone we can see it as this:

  

- Internet (country) → DNS (cities) → Zones (neighborhoods) ← admin (who manage neighborhood)

  

A DNS zone specifies that a domain, or part of a domain (subdomain), is managed by a specific administrator, may the domain has specific zone and its subdomain is has its specific zone, the reason for this is that number of devices connected to subdomain is large and the volume of records related to this subdomain is also big, so admin needs to much granular control on this subdomain and that's why it specify zone for the subdomain, and for this zone may have multiple subdomains and multiple zones.

  

- It makes less burden on the admin for specific domain

- It distributes DNS query load and enhance efficiency and scalability of DNS services

  

### 1.2 DNS Zone File

  

**DNS Zone File** is a plain text file stored on DNS servers that contains all the records for the domains within that zone, each line of a zone file specifies a resource record.

  

**Resource record** is a single piece of information about the nature of, typically organized by data type, resource records ensure that when a user initiates a query, the DNS can quickly direct users to the correct server.

  

Zone file has two mandatory types of records:

  

- **SOA record** → specifies the primary authoritative name server for the DNS zone

- **TTL record** → indicates how records should be stored in the local DNS cache

  

It has also other records:

  

| Record | Description |

| --- | --- |

| A | Maps hostname to IPv4 |

| AAAA | Maps hostname to IPv6 |

| MX | Specifies an SMTP email server for a domain |

| CNAME | Redirects hostnames from an alias (subdomain) to another domain |

| NS | Indicates that a DNS server is attached to a specific authoritative name server, and ask that server for anything need for that domain |

| PTR | Specify a reverse DNS lookup, from IP to domain opposite of A record |

| TXT | Indicate the sender policy framework record for email authentication |

  

### 1.3 DNS Zone Types

  

- **Primary DNS zone** → The main read/write zone that holds the original DNS records; all updates happen here, contains the original zone file.

- **Secondary DNS zone** → A read-only copy of the primary zone (zone transfer) used for redundancy and load balancing, DNS requests are typically distributed across the primary and secondary servers. If the primary server is down, the secondary servers can take on all or part of the load by using zone transfers, contains copied zone file.

- **Forward lookup zone** → Converts domain names (like example.com) into IP addresses using A/AAAA records.

- **Reverse lookup zone** → Converts IP addresses back into domain names using PTR records.

- **Stub zone** → A lightweight zone that only contains info about authoritative DNS servers for a zone to speed up queries, they serve as a pointer, reducing dependence on recursive servers for querying upper-level zones to locate the authoritative server which reduce DNS query traffic and shorten resolution times.

  

### 1.4 DNS Zone Benefits

  

- **Decentralization** → Orgs use different zones to distribute the admin workloads that associated with specific domain and prevent admin or server from being overwhelmed

- **Administrative autonomy** → Zones gives the Orgs granular control over management of DNS records and traffic distribution

- **Load distribution** → DNS zones facilitate the distribution of internet traffic across different servers by enabling zone administrators to configure custom DNS settings for load balancing and failover

- **Speed** → Delegation of authority within zones means that DNS resolvers can reduce the number of hops needed to resolve a domain name, ultimately accelerating the routing and data retrieval processes

  

### 1.5 DNS Zone Transfers (AXFR)

  

A full zone transfer copies the entire contents of a zone file from the primary DNS server to secondary servers, creating an exact replica of the zone. Full zone transfers are commonly used during initial configuration of secondary servers or when secondary servers need to be re-synced after lengthy downtime, on the other hand Incremental zone transfers only comprise changes to the zone since the last transfer. Because they require less bandwidth and processing power to maintain syncing processes, incremental zone transfers can be useful in dynamic zones that undergo frequent changes, maintain optimal system functionality especially in environments where high availability and redundancy are priorities.

  

![zone-transfer-diagram](/images/ejpt/day-1/active-reconnaissance/zone-transfer-diagram.png)

  

It will be very critical vulnerability if attacker can catch or see the content of zone file after transfer or while it, so it is very required to hide it as we will see two types one is hide and the other isn't hidden, which also make attacker can get a list of all hosts for a domain, which gives them a lot of potential attack vectors.

  

We will work on **zonetransfer.me** which is web app that allow us to make different recon on DNS and its zones so this web app doesn't hide the zone file while transfer so we will work on it to see this operation.

  

#### DNS Dumpster

  

DNS dumpster is a website which do passive recon on DNS by querying its records, maps a target's network infrastructure by querying multiple public sources, such as search engines, certificate transparency logs, and web crawlers, rather than interacting directly with the target, the same is dnsrecon tool which is cli tool do also passive recon on DNS like DNS dumpster website.

  

This is DNS dumpster results on zonetransfer.me:

  

1. ![dnsdumpster-1](/images/ejpt/day-1/active-reconnaissance/dnsdumpster-1.png)

2. ![dnsdumpster-2](/images/ejpt/day-1/active-reconnaissance/dnsdumpster-2.png)

  

#### dnsrecon

  

This is the dnsrecon cli tool results on zonetransfer.me. Here is what dnsrecon does:

  

- Check all NS Records for Zone Transfers.

- Enumerate General DNS Records for a given Domain (MX, SOA, NS, A, AAAA, SPF and TXT).

- Perform common SRV Record Enumeration.

- Top Level Domain (TLD) Expansion.

- Check for Wildcard Resolution.

- Brute Force subdomain and host A and AAAA records given a domain and a wordlist.

- Perform a PTR Record lookup for a given IP Range or CIDR.

- Check a DNS Server Cached records for A, AAAA and CNAME Records provided a list of host records in a text file to check.

  

![dnsrecon](/images/ejpt/day-1/active-reconnaissance/dnsrecon.png)

  

#### dnsenum

  

**dnsenum** tool is an active reconnaissance tool used to work on gathering information of DNS server of the targeted domain, it queries DNS servers which is making by interacting with the target and It gathers records, subdomains, IP ranges and possible misconfigurations, it can do DNS zone transfer automatically which is very important thing, gather public records and can do DNS brute force which used to identify records and subdomains.

  

This first part is what we have checked on it before which is passive reconnaissance:

  

![dnsenum-passive](/images/ejpt/day-1/active-reconnaissance/dnsenum-passive.png)

  

This is second part which is trying to automatically apply zone transfer and it has succeeded and here are the results, it has forced zones to apply zone transfer to reveal content of zone file which contain DNS records for specific domain or subdomain (which here as we can see in the two trial we see (canberra-office.zonetransfer.me with IP 202.14.81.230) if we try to access it will not be accessed and from this we can say that this subdomain is internal network subdomain which is very big security issue which make us reveals the internal network infrastructure).

  

This is the trail on the first NS, and as we can see it reveals very different secret information about records of domain by revealing the records that existed inside the zone file:

  

![dnsenum-active-1](/images/ejpt/day-1/active-reconnaissance/dnsenum-active-1.png)

  

This the trial on the second NS, as we can see also it reveals very different secret information about records of domain by revealing the records that existed inside the zone file:

  

![dnsenum-active-2](/images/ejpt/day-1/active-reconnaissance/dnsenum-active-2.png)

  

#### dig

  

**dig** (domain information groper) is DNS lookup utility cli tool, is very flexible tool that can be used to interrogate DNS name servers. It performs the DNS lookups and then shows the answers returned from the interrogated name server(s) in the output, it has varsities usage as DNS tool, but in this case we will use it to perform zone transfer as following.

  

This is zone transfer using dig with axfr (to get copy of the zone file from the primary server → zone transfer) and the NS (one of name servers of the targeted domain we can get it using dnsrecon or dnsenum):

  

1. ![dig-zonetransfer](/images/ejpt/day-1/active-reconnaissance/dig-zonetransfer.png)

2. ![dig-zonetransfer-2](/images/ejpt/day-1/active-reconnaissance/dig-zonetransfer-2.png)

  

#### Fierce

  

**Fierce** is a DNS reconnaissance tool used to gather information about a target domain and discover its network infrastructure. It helps identify hosts, subdomains, and IP addresses associated with an organization (non-contiguous IP space → IP addresses and network ranges that are spread across different, unrelated blocks instead of being located within one continuous range) by analyzing DNS records and performing techniques such as DNS enumeration and zone transfer checks. For example, when scanning a domain such as `example.com`, Fierce may discover `mail.example.com` hosted on `192.168.1.10`, `vpn.example.com` on `10.10.50.5`, and `dev.example.com` on `172.16.8.20`. Since these IP addresses belong to different network ranges, they are considered non-contiguous IP spaces.

  

DNS zone transfer using Fierce tool:

  

1. ![fierce-1](/images/ejpt/day-1/active-reconnaissance/fierce-1.png)

2. ![fierce-2](/images/ejpt/day-1/active-reconnaissance/fierce-2.png)

  

### 1.6 Testing a Protected Domain (Zone Transfer Disabled)

  

Now we will test website that hides or disables zone transfer, so it is protected against this disclosure vulnerability, that reveals records of specific domain.

  

**By using dnsenum:**

- It will apply the passive recon part successfully

  ![dnsenum-protected-1](/images/ejpt/day-1/active-reconnaissance/dnsenum-protected-1.png)

- In the active recon part it will not apply the dns zone transfer due to that is disabled by dns owner or provider

  ![dnsenum-protected-2](/images/ejpt/day-1/active-reconnaissance/dnsenum-protected-2.png)

  

**By using dig tool:**

  

![dig-protected](/images/ejpt/day-1/active-reconnaissance/dig-protected.png)

  

**By using fierce tool**, we see here the failure as it is protected:

  

![fierce-protected](/images/ejpt/day-1/active-reconnaissance/fierce-protected.png)

  

---

  

## 2. Host Discovery & Port Scanning

  

Now we will talk about another section of active reconnaissance, which is about hosts discovery over network and also port scanning now we will discuss about definition of host discovery and port scanning:

  

- **Host Discovery** → is discovering online hosts in specific range of network, is trying to tell if the target is up and respond, the process of identifying active devices (hosts) on a network, such as computers, servers, or IoT devices, by determining which IP addresses are currently in use.

- **Port Scanning** → use to discover open doors or weak points in a network.

  

### 2.1 netdiscover

  

This tool is active/passive ARP reconnaissance tool, initially developed to gain information about wireless networks without DHCP servers in wardriving scenarios, It can also be used on switched networks. Built on top of libnet and libpcap, it can passively detect online hosts or search for them by sending ARP requests, also it, it can be used to inspect your network's ARP traffic, or find network addresses using auto scan mode, which will scan for common local networks, but now we will focus in host discovery (send ARP requests to discover live hosts), it works only on local networks because we can't scan remote networks using ARP packets.

  

- **ens33** → network interface

  

![nestdiscover](/images/ejpt/day-1/active-reconnaissance/nestdiscover.png)

  

### 2.2 Nmap — Host Discovery

  

This section will have one of the most famous and most important tools in network troubleshooting and reconnaissance as penetration tester which is **Nmap**.

  

Nmap ("Network Mapper") is an open source tool for network exploration and security auditing. It was designed to rapidly scan large networks, although it works fine against single hosts. Nmap uses raw IP packets in novel ways to determine what hosts are available on the network, what services (application name and version) those hosts are offering, what operating systems (and OS versions) they are running, what type of packet filters/firewalls are in use, and dozens of other characteristics. While Nmap is commonly used for security audits, many systems and network administrators find it useful for routine tasks such as network inventory, managing service upgrade schedules, and monitoring host or service uptime. It uses different techniques or packet types for discovering live hosts like:

  

- ICMP echo requests (ping)

- TCP SYN packets

- ACK packets

- UDP probes

- ARP requests (on local LANs)

  

**`-sn`** → option to scan live hosts only without port scanning

  

![nmap-host-discovery](/images/ejpt/day-1/active-reconnaissance/nmap-host-discovery.png)

  

---

  

## 3. Port Scanning

  

Port Scanning is used to discover open doors or weak points in a network, helps us to find open ports and figure out whether they are receiving or sending data, can provide information like Services that are running, Users who own services, Whether anonymous logins are allowed and Which network services require authentication.

  

A port is a point on a computer where information exchange between multiple programs and the internet to devices or other computers takes place. To ensure consistency and simplify programming processes, ports are assigned port numbers. This, in conjunction with an IP address, forms vital information that each internet service provider (ISP) uses to fulfill requests. Port numbers range from 0 through to 65,535 and are ranked in terms of popularity. Ports numbered 0 to 1,023 are called "well-known" ports, which are typically reserved for internet usage but can also have specialized purposes:

  

| Port | Protocol | Service |

| --- | --- | --- |

| 20 (UDP) | FTP | File Transfer Protocol used for transferring data |

| 22 (TCP) | SSH | Secure Shell protocol used for FTP, port forwarding, and secure logins |

| 53 (UDP) | DNS | The DNS which translates internet domain names into machine-readable IP addresses |

| 80 (TCP) | HTTP | The World Wide Web HTTP |

  

### 3.1 Port Scanning Techniques

  

- **Ping Scan** → Uses ICMP requests to check whether a host is alive and reachable on the network

- **Vanilla Scan** → Attempts a full TCP connection to all ports to identify which ports are open

- **SYN Scan** → Sends a SYN packet and waits for a SYN-ACK response without completing the connection to detect open ports stealthily

- **XMAS Scan** → Sends packets with multiple unusual TCP flags set to gather information about open ports and firewall behavior

- **FIN Scan** → Sends a FIN packet to a target port to determine whether the port is open or closed based on the response

- **FTP Bounce Scan** → Uses an FTP server as an intermediary to hide the attacker's real IP address during scanning

- **Sweep Scan** → Scans the same port across multiple hosts to identify which systems are active on the network

  

### 3.2 Nmap — Port Scanning Options

  

First thing we will do is host discovery to see live hosts, and we will choose one of hosts:

  

![nmap-port-scan-1](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-1.png)

  

Then we will apply port scanning on this port, we will use default nmap scan, we can see it works using ICMP pings or ping Probes, if it displays nothing then the target system may block ICMP pings or ping Probes so we use option (`-Pn`) to avoid ping (windows by default block ICMP pings or ping Probes):

  

1. ![nmap-port-scan-2](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-2.png)

2. ![nmap-port-scan-3](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-3.png)

  

**`-p-`** → option scans all 65535 port numbers

  

![nmap-port-scan-4](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-4.png)

  

**`-p80,22,21`** → option to specify which port numbers to scan, as well as we can specify a range of numbers with option (`-p1-1000`) to scan numbers from 1 to 1000:

  

1. ![nmap-port-scan-5](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-5.png)

2. ![nmap-port-scan-6](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-6.png)

3. We can see the closed one also, instead of closed we could see filtered which mean it is filtered by a firewall or IDS

   ![nmap-port-scan-7](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-7.png)

  

**`-F`** → fast scan option which scans 100 of the mostly used ports on the target system

  

![nmap-port-scan-8](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-8.png)

  

**`-sU`** → it is option to enable UDP scan

  

![nmap-port-scan-9](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-9.png)

  

**`-v`** → verbose mode option It makes Nmap show more details while the scan is running, instead of waiting until the end, it has different levels (`-v` → some extra info), (`-vv` → more detailed) and (`-vvv` → even more (you can keep increasing))

  

![nmap-port-scan-10](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-10.png)

  

**`-sV`** → it is option to detect and show service version, Probe open ports to determine service/version info, it may get some and other not

  

![nmap-port-scan-11](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-11.png)

  

**`-O`** → this option is used to discover Operating System of the target, it isn't 100% reliable because it gives range of suspected versions, so it isn't always accurate

  

1. ![nmap-port-scan-12](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-12.png)

2. ![nmap-port-scan-13](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-13.png)

  

**`-sC`** → this option is used to run list of scripts on open ports to obtain more information we can use specific ports or we can use default ones

  

1. ![nmap-port-scan-14](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-14.png)

2. ![nmap-port-scan-15](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-15.png)

  

**`-A`** → this option is aggressive scan mode which combines (`-sV` + `-O` + `-sC` + `--traceroute`) together, it is louder so it is detected easily because it sends more packets

  

1. ![nmap-port-scan-16](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-16.png)

2. ![nmap-port-scan-17](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-17.png)

  

**`-T<0-5>`** → this option is used to set timing template (higher is faster → 5) and (lower is slower → 0) which their names are (paranoid => 0 | sneaky => 1 | polite => 2 | normal => 3 | aggressive => 4 | insane => 5) we use slow scan to evade IDS from blocking us

  

![nmap-port-scan-18](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-18.png)

  

**`-o<N,X,S,G>`** → this option is used to put the output of nmap inside file with different formats, (N)ormal which is txt like the output that appears in terminal, (X)ML which is used into metasploite, (S)cript Kiddie which is joke format (intentionally messy text), (G)repable which is simplified format for command-line parsing

  

- **Normal**

  ![nmap-port-scan-19-N](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-19-n.png)

- **XML**

  ![nmap-port-scan-20-X](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-20-x.png)

- **Script Kiddie**

  ![nmap-port-scan-21-S](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-21-s.png)

- **Grepable**

  ![nmap-port-scan-22-G](/images/ejpt/day-1/active-reconnaissance/nmap-port-scan-22-g.png)
 This is the end of active reconnaissance.