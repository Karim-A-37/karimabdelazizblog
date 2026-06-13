---
title: "Scanning Optmization"
date: 2026-06-13
slug: "scanning-optmization"
draft: false
series:
  - "eJPT"
weight: 7
ShowToc: true
---



---

## Session Goals

> In this session we will discuss how to optimize our scan and also how to use the different techniques to evade IDS and detect Firewalls

---

## Concepts Learned

> The Concepts i have learned in this session

### Concept 1: [Firewall Detection]

**What it is:**
Firewalls are considered filters of any type of server if we need to filter ping requests(ICMP echo requests) we need to create rule and put it inside the firewall and based on that rule it will decide to pass the packet or drop(filter) it.
![firewall-explanantion](/images/ejpt/day-5/scanning-optmization/firewall-explanantion.png)
so we want to detect if there is a firewall on target or not, to do this we will use option (-sA) which is scanning uses ACK packet which sees if the ports are filtered or not based on the response, it work like following
![ack-firewall](/images/ejpt/day-5/scanning-optmization/ack-firewall.png)
for using this option like the following
![-sA-for-firewall](/images/ejpt/day-5/scanning-optmization/sa-for-firewall.png)
as we can see in the previous image we see it says 100 unfiltered from this we say that there is no firewall or it exist but doesn't filter on the specific ports we scanned which are most 100 famous ports using option (-F), also as we can see if we capture the process using Wireshark as following image we can see that it uses packets with ACK flag is set to detect if it filter packets or not
![firewall-detection-sA-wireshark-2](/images/ejpt/day-5/scanning-optmization/firewall-detection-sa-wireshark-2.png)

---

### Concept 2: [Intrusion Detection System(IDS) Evasion]

**What it is:**
IDS is system that monitors network for any malicious activity, we are trying to use different techniques to evade this IDS if it is existing:
- fragmentation --> is a technique which Nmap fragment packets into smaller portions of packets, fragmentation is breaking down a packet into smaller individual packets that reassembled as final one when it is arrived to destination , it also takes different options like: 
	- --ttl  --> to specify time to live for packets manually
	- --data-length --> append random data to packets we send
	- --mtu --> it is maximum transmitted unit, which we specify the size of packet transmitted, it is multiply of 8 like (8,16,24,32)
  using option (-f) as we can see :
	- Before fragmentation
		- ![before-frag-nmap](/images/ejpt/day-5/scanning-optmization/before-frag-nmap.png)
		- ![before-frag-wireshark](/images/ejpt/day-5/scanning-optmization/before-frag-wireshark.png)
	- After fragmentation 
		- ![after-frag-nmap](/images/ejpt/day-5/scanning-optmization/after-frag-nmap.png)
		- ![after-frag-wireshark](/images/ejpt/day-5/scanning-optmization/after-frag-wireshark.png)
	One more thing: many modern firewalls, IDS/IPS systems, cloud providers, and Linux network stacks reassemble fragments or simply drop fragmented scans, so `-f` is much less effective today than it was years ago. For a lab or coursework environment it's useful to learn, but in real networks it often provides little or no evasion benefit.
- Decoy --> in Nmap is used to make it harder for a target or IDS/IPS to determine which IP address is actually performing the scan it is known as spoofing, as we can see in the following images how to use decoy IPs
	- ![decoy-nmap](/images/ejpt/day-5/scanning-optmization/decoy-nmap.png)
	- ![decoy-wireshark-1](/images/ejpt/day-5/scanning-optmization/decoy-wireshark-1.png)
	- ![decoy-wireshark-2](/images/ejpt/day-5/scanning-optmization/decoy-wireshark-2.png)
	For your cybersecurity studies, decoys are useful for understanding **IP spoofing concepts, IDS evasion techniques, and how security monitoring correlates scan traffic**, but they are not a reliable way to hide your identity on modern networks.


---

### Concept 3: [Optimizing Nmap scan]

**What it is:**
we are increasing scan performance and manipulate it to get more efficient results like slow down scan or fast up scan by option (-T0:5) it is also called time template we use it to evade the IDS like when we slow down scan when we deal with IDS and when we deal with old network:
- -T0 --> Paranoid --> Extremely slow, designed to avoid IDS detection
- -T1 --> Sneaky --> Very slow, low network footprint
- -T2 --> Polite --> Reduces bandwidth usage
- -T3 --> Normal --> Default timing
- -T4 --> Aggressive --> Faster scans on reliable networks
- -T5 --> Insane --> Very fast, may miss results
each time template has unique name that represent its usage, here are two examples one is using T1 and the other use s T4:
- T1 --> as we can it  is very slow
	- ![t1-nmap](/images/ejpt/day-5/scanning-optmization/t1-nmap.png)
	- ![t1-wireshark](/images/ejpt/day-5/scanning-optmization/t1-wireshark.png)
- T4 --> as we can see it is very fast 
	- ![t4-nmap](/images/ejpt/day-5/scanning-optmization/t4-nmap.png)
	- ![t4-wireshark](/images/ejpt/day-5/scanning-optmization/t4-wireshark.png)
here are some options we use to customize time:
- --scan-delay (time(s/m/h))--> to adjust delay between probes or packets are sent between each other or between one and another
	- ![scan-delay-nmap](/images/ejpt/day-5/scanning-optmization/scan-delay-nmap.png)
	- ![scan-delay-wireshark](/images/ejpt/day-5/scanning-optmization/scan-delay-wireshark.png)
- --max-scan-delay (time(s/m/h))--> to adjust delay between probes or packets are sent between each other or between one and another  by adding maximum delay that must not be exceeded but it is lower and not exceeded the specified time what i mean is it is may be less than the specified time but it must not exceed it
- --host-timeout (time(s/m/h))--> give up on target after this time , we use it if we scan large number of IPs or large CIDR
	- ![host-timeout](/images/ejpt/day-5/scanning-optmization/host-timeout.png)



---

### Concept 4: [Output Manipulating]

**What it is:**
we can save output of Nmap for next phases of penetration testing operation in different formats like :
- -oN --> Normal Format like output in the terminal screen
	- ![normal-output](/images/ejpt/day-5/scanning-optmization/normal-output.png)
- -oX --> XML Format to use it inside Metasploit for exploitation
	- ![xml-output](/images/ejpt/day-5/scanning-optmization/xml-output.png)
- -oS --> script Kiddie Format , but it doesn't used too much
	- ![script-output](/images/ejpt/day-5/scanning-optmization/script-output.png)
- -oG --> Grepable Format to use in commands like grep and other usage, but it doesn't used too much
	- ![Grepable-output](/images/ejpt/day-5/scanning-optmization/grepable-output.png)
- -oA --> for all three main formats (-oN + -oX + -oG) all at once
- -v --> for amount of details info displays on terminal screen while scan is running, we increase (v) for more details like (-vv)
	- ![detailed-output](/images/ejpt/day-5/scanning-optmization/detailed-output.png)
- --reason --> to reason anything like why port appears on that state
	- ![reason-output](/images/ejpt/day-5/scanning-optmization/reason-output.png)
here is example of using XML format inside Metasploit:
-  ![metasploit-step-1](/images/ejpt/day-5/scanning-optmization/metasploit-step-1.png)
- ![metasploit-step-2](/images/ejpt/day-5/scanning-optmization/metasploit-step-2.png)
- ![metasploit-step-3](/images/ejpt/day-5/scanning-optmization/metasploit-step-3.png)

---

## ⚙️ Commands Learned

> The commands i have learned during this session


1. Firewall detection using -sA
```bash
# -sA --> scan ports to find if they are filtered or not
nmap -Pn -sA -F 5.196.105.14

```
![[posts/eJPT/Day-5/Scanning-optmization-images/firewall-detection-sA.png|567]]
![firewall-detection-sA-wireshark](/images/ejpt/day-5/scanning-optmization/firewall-detection-sa-wireshark.png)

2. Decoy and Fragmentation
```bash
# -D --> for Decoy to add spoofing IPs
#-f --data-length 200 --> to fragmentation and appended randowm data lenght is 200
nmap -Pn -sS -sV - -F -D 192.168.210.120 192.168.210.121 192.168.210.122 -f --data-length 200 5.196.105.14

```
![decoy-nmap-1](/images/ejpt/day-5/scanning-optmization/decoy-nmap-1.png)


---

**Honest rating of today's session:** `[ ] 🔴 Struggling` | `[ ] 🟡 Getting it` | `[x] 🟢 Solid`

---

## 📌 Tags

#ejpt #scanning-optimization #week-1  
