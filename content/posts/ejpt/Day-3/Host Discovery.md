---
title: "Host Discovery"
date: 2026-05-30
slug: "host-discovery"
draft: false
---

# Day 3 — [Host Discovery]

> **Date:** 2026 **Week:** 1 | **Day:** 3? **Module/Section:** Host Discovery

---

## 🎯 Session Goals

> What do you want to be able to DO by the end of this session?

- [x] Network Mapping ✅ 2026-05-30
- [x] Ping Sweeps ✅ 2026-05-30
- [x] Host Discovery ✅ 2026-05-30

---

## 🧠 Concepts Learned

> The Concepts i have learned in this session

### Concept 1: [Network Mapping]

**What it is:**
Network mapping encapsulates active recon techniques to draw a blueprint of the live hosts or devices on the network, it is the process of discovering live hosts to map the network architecture, by discovering different elements  


---

### Concept 2: [Host Discovery Techniques]

**What it is:**
it is the process to detect the live host on specific network CIDR or scan specific IP to see it is live or not to map the network of live hosts, there are different techniques for host discovery:
- ping sweeps -->> ICMP echo requests, it is blocked via windows by default
- ARP scanning -->> identify hosts only on local network by sending broadcasted message to get IPs of devices using MAC , if the device sends back its IP so it is live
- TCP  SYN ping -->> it is half open connection by send SYN packet and if host respond with SYN ACK so it is life and source will send RST packet, it is in Nmap called stealth scan
- UDP ping -->> uses UDP packets to target host to see if it is live or not
- TCP ACK ping and SYN ACK ping if RST packet received then the host is live


---
### Concept 3: [Ping Sweeps]

**What it is:**
it is host discovery techniques it is using ICMP echo request or ping messages to see if the target is reachable if we receive response then it is live if not then it is not live or it is blocked or network congestion or temporary unavailability, windows by default block ICMP echo request, the two ICMP messages are:
- ICMP echo request -->> type : 8 , code : 0
- ICMP echo response -->> type : 0 , code : 0
- type -->> represent the purpose of the ICMP function
- code -->> additional information related to message type
there are two utilities used for doing ICMP echo requests or ping messages:
- ping -->> it is utility based on ICMP echo requests that sends them and wait for reply
- fping -->> it is the same function of ping but differs from it that we can specify any number of targets
- we can do ping sweeps with namp with -sn option
![ping-sweeps-visual](/images/ejpt/day-3/host-discovery/ping-sweeps-visual.png)

---

### Concept 4: [-sn option]

**What it is:**
for ping sweeps by using it, it disable port scan and do host discovery only, it consist of three techniques of host discovery
- ICMP echo request + TCP SYN(443 port) + TCP ACK(80 port)
	- ![-sn](/images/ejpt/day-3/host-discovery/sn.png)
- if we are in local network Nmap will use ARP in ping
	- ![nmap-sn-arp-localnetwork](/images/ejpt/day-3/host-discovery/nmap-sn-arp-localnetwork.png)
- use (--send-ip) to override ARP in local network and use other requests like ICMP
	- ![local-network-sn-use-icmp-by--send-ip-to-override-on-arp](/images/ejpt/day-3/host-discovery/local-network-sn-use-icmp-by-send-ip-to-override-on-arp.png)


---
### Concept 5: [-iL option]

**What it is:**
is used to make Nmap take IPs from a text file instead of writing IP
![-iL-to-put-ips-into-file](/images/ejpt/day-3/host-discovery/il-to-put-ips-into-file.png)


---
### Concept 6: [TCP SYN Ping]

**What it is:**
it is half open connection scan, so we send TCP packet with SYN flag only is set to port(80 the default, we can specify any other port or range of ports) and if it is opened the host will send SYN ACK packet then the we will send back RST packet to reset the connection, if it is closed host will send RST packet directly, in Nmap we use this by (-PS) option and (S stands for SYN), the connection is being half open because it isn't sending the final ACK because we need to discover only if the host is live or not


---
### Concept 7: [TCP ACK Ping]

**What it is:**
it sends TCP packet with ACK flag only is set to port 80 the default and we can specify any other port or range of ports, if this is closed or firewall block ACK it will not respond to the request, and if it is opened it will return RST packet if there is no portable three way handshake which RST packet defines that the target is online, in Nmap we use this by (-PA) option (A stands for ACK) it has limitation which some networks or targets may block packet with ACK flag set.

---
### Concept 8: [ICMP Ping echo request only]

**What it is:**
it send ICMP echo request(type:8,code:0) which is internet control message protocol packet to the target if target is reachable and firewall allows this type of packets not blocked it will respond with ICMP reply(type:0,code:0), in Nmap we use this by (-PE) option (E stands for Echo).


---
### Concept 10: [-Pn]

**What it is:**
The `-Pn` option in Nmap disables the host discovery phase and instructs Nmap to assume that the target host is online. This is particularly useful when scanning systems that block ICMP ping requests or other discovery probes, such as Windows hosts protected by a firewall. By skipping host discovery, Nmap proceeds directly to port scanning, allowing it to identify open ports and services even when the target does not respond to ping. As a result, `-Pn` helps ensure that potentially reachable hosts are not missed during a scan.

---

## ⚙️ Tools Used
> The Tools i have used during this session
### Nmap
Nmap stands for Network Mapper, which is tool dedicated for network analysis and for our use in this session we will use it for host discovery which uses:
- ARP --> uses for local networks only and it is the default when scan local network
- ICMP --> ICMP echo requests or ping requests
- TCP/UDP probes 
it is used for port scanning and OS detection and services versions detection, we will discuss later.


---


## ⚙️ Commands Learned

> The commands i have learned during this session

1. ping utility

```bash
# ping utility is used to send ICMP echo request and wait for reply
ping google.com

# to specify the number of the requests being sent(-c in linux and -n for windows)
#for linux
ping -c 5 google.com

#for windows
ping -n 5 google.com
```
for Linux![ping-linux](/images/ejpt/day-3/host-discovery/ping-linux.png)
for windows![ping-windows](/images/ejpt/day-3/host-discovery/ping-windows.png)

2. fping utility
```bash
# the of ping but it differes that we can target multiple targets and it doesnot wait for reply
fping -a -g 142.251.208.0/24
# -a for showing live hosts
# -g for generate target list to secify subnet or network CIDR
```
![fping-with-g](/images/ejpt/day-3/host-discovery/fping-with-g.png)
![fping-without-g](/images/ejpt/day-3/host-discovery/fping-without-g.png)
3. namp for ping sweeps
```bash
# -sn
nmap -sn 142.251.208.238
```
![nmap-sn-linux](/images/ejpt/day-3/host-discovery/nmap-sn-linux.png)

```bash
# this target is windows system so it is blocking our ping request
nmap -sn 10.5.22.188
```
![-sn--nmap](/images/ejpt/day-3/host-discovery/sn-nmap.png)

```bash
# to override arp if i scan local network
nmap -sn 10.10.44.0/24 --send-ip

```
![local-network-sn-use-icmp-by--send-ip-to-override-on-arp--nmap](/images/ejpt/day-3/host-discovery/local-network-sn-use-icmp-by-send-ip-to-override-on-arp-nmap.png)
![local-network-sn-use-icmp-by--send-ip-to-override-on-arp 1](/images/ejpt/day-3/host-discovery/local-network-sn-use-icmp-by-send-ip-to-override-on-arp-1.png)
4. IPs inside file
```bash
# to take target IPs as file
nmap -sn -iL IPs.txt
```
![-iL-to-put-ips-into-file--nmap](/images/ejpt/day-3/host-discovery/il-to-put-ips-into-file-nmap.png)
![-iL-to-put-ips-into-file--wireshark](/images/ejpt/day-3/host-discovery/il-to-put-ips-into-file-wireshark.png)
5. using TCP SYN Ping
```bash
# -PS overrides on -sn , and uses only TCP SYN ping on default port 80
nmap -sn -PS 10.5.22.188
```
![-ps--nmap](/images/ejpt/day-3/host-discovery/ps-nmap.png)
![-ps--wireshark](/images/ejpt/day-3/host-discovery/ps-wireshark.png)

```bash
# we can change the port to any othr ports or range of ports as following
nmap -sn -PS1-1000 10.5.22.188
```
![-ps--nmap-different-ports](/images/ejpt/day-3/host-discovery/ps-nmap-different-ports.png)
![-ps--wireshark-different-ports](/images/ejpt/day-3/host-discovery/ps-wireshark-different-ports.png)

6. Using TCP ACK Ping
```bash
# -PS overrides on -sn , and uses only TCP ACK ping on default port 80
nmap -sn -PA1-1000 10.5.22.188
```
![-pa--nmap](/images/ejpt/day-3/host-discovery/pa-nmap.png)
![-pa--wireshark](/images/ejpt/day-3/host-discovery/pa-wireshark.png)

7. ICMP echo request only
```bash
# uses to send ICMP echo request and waiting for reply it it is replying with ICMP reply so it is online, if there is no reply then it is offline
nmap -sn -PE 10.5.22.188
```
![-pe--nmap](/images/ejpt/day-3/host-discovery/pe-nmap.png)
![-pe--wireshark](/images/ejpt/day-3/host-discovery/pe-wireshark.png)

```bash
# --send-ip --> it is overriding on ARP in local network to use ICMP echo requests
nmap -sn -PE 10.10.44.0/24 --send-ip
```
![-pe--nmap--send-ip](/images/ejpt/day-3/host-discovery/pe-nmap-send-ip.png)
![-pe--wireshark--send-ip 1](/images/ejpt/day-3/host-discovery/pe-wireshark-send-ip-1.png)

8. skipping host scanning and ping discovery
```bash
# to skip ping discovery if the target is windows which block ping requests by default
nmap -sn -Pn 10.5.22.188
```
![-pn--nmap](/images/ejpt/day-3/host-discovery/pn-nmap.png)

9. the full test architecture
```bash
# full test architecture of using nmap
nmap -sn -v -T4 10.5.22.188 -PS -PU
# -sn --> no port scanning, host discovery only
# -v --> verposity, contorl deteails of output that appear of the screen
# -T4 --> the speed or numbers of packets send [1 --> slowest, 5 --> fastest]
# -PS --> TCP SYN Ping scan 
# -PU --> UDP scan , to scan services that are running via UDP to see if there any response which means it is reachable
```
![full-flow](/images/ejpt/day-3/host-discovery/full-flow.png)
![full-flow-wireshark](/images/ejpt/day-3/host-discovery/full-flow-wireshark.png)

---

## ✅ End-of-Session Self Test

> Answer without looking at your notes

- [x] Can I explain today's main concept in one sentence? ✅ 2026-05-30
- [x] Can I run the key commands from memory? ✅ 2026-05-30
- [x] Can I reproduce the lab attack chain without help? ✅ 2026-05-30

**Honest rating of today's session:** `[ ] 🔴 Struggling` | `[ ] 🟡 Getting it` | `[x] 🟢 Solid`

---

## 📌 Tags

`#ejpt` `#host discovery` `#week-1` `#host-discovery

---
