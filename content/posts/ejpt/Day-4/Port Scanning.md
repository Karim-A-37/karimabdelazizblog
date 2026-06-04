---
title: Port Scanning
date: 2026-06-04
slug: port-scanning
draft: false
series:
---



## Session Goals

> What do you want to be able to DO by the end of this session?

- [x] Port Scanning ✅ 2026-06-03
- [x] Services versions and Operating Systems detection ✅ 2026-06-03
- [x] Nmap Scripting Engine (NSE) ✅ 2026-06-03

---

## Concepts Learned

> The Concepts i have learned in this session

### Concept 1: [Port Scanning]

**What it is:**
in port scanning we try to discover which ports are open, closed or filtered TCP or UDP in the target system, and each one is going to give us information about what target are doing:
1. open --> we try to find what services are running on it and gives info about currently open ports
2. closed --> this may indicate that the port is closed or unreachable or even the packet blocked by firewall here there are several reasons
3. filtered --> this indicate that there is firewall block our packets
each info is valuable in the information gathering phase, which we are currently in.

---

### Concept 2: [Default command]

**What it is:**
```bash
nmap 192.207.193.0/24
```
![1-default-nmap-cidr-network](/images/ejpt/day-4/port-scanning/1-default-nmap-cidr-network.png)
this command has two ways:
1. Normal user --> it uses the full TCP connect technique to discover the most commonly 1000 ports, the full TCP 3 way handshake which is equal to option (-sT)
	- ![full-tcp-for-normal-user-technique](/images/ejpt/day-4/port-scanning/full-tcp-for-normal-user-technique.png)
	- ![8--sT-full-TCP-all-ports-nmap 1](/images/ejpt/day-4/port-scanning/8-st-full-tcp-all-ports-nmap-1.png)
2. Root user --> it uses SYN half connection technique to discover the most commonly 1000 ports, the half connection of 3 way handshake, also it is called stealthy technique which is equal to option (-sS)
	- ![half-tcp-for-root-user-technique](/images/ejpt/day-4/port-scanning/half-tcp-for-root-user-technique.png)
	- ![7--sS-stealthy-nmap-1](/images/ejpt/day-4/port-scanning/7-ss-stealthy-nmap-1.png)
3. if we deal with windows and we have seen the state is filtered then there is firewall and here how it works
	- ![filtered-state](/images/ejpt/day-4/port-scanning/filtered-state.png)
why is half connection scan (-sS) called stealthy scan or why it is preferred to use it if you are privileged or non privileged user?
there are two reasons:
- it is using the packet with flag SYN is set which is the type of packet the port is expecting to establish any connection, so it isn't contradict with any of the TCP connection handshake
- it doesn't complete the 3 way handshake because it avoids creation of connection log in target system because most OSs log creation of TCP connection sessions and IDS(Intrusion Detection System) detect TCP connection and logs it, but this happens when the full 3 way handshake has been completed, that's why it is called stealthy
if we see in Wireshark retransmission this means that we doesn't receive any response not RST(closed) nor SYN ACK(open), we could say that there is firewall blocking our request.

---

### Concept 3: [Services Versions Detection]

**What it is:**
it is trying to discover services that are running on the open ports, and trying to get their specific versions so we can may exploit this version in the exploitation phase which target specific vulnerability in that specific version, so it is very useful information, we will use Nmap to try to get the services versions detections.
we have option (-sV) for service versions Detection its default intensity is 7, this option is used to detect services and its versions as we can see
	![10-sV-on-all-TCP-ports-nmap-2](/images/ejpt/day-4/port-scanning/10-sv-on-all-tcp-ports-nmap-2.png)
but in many cases it may not detect version of the real name of the services that's why there another option is added to (-sV) which is (--version-intensity <0 : 9>) which is doing aggressive version detection, It controls how aggressively Nmap probes a service to identify its version
	![4-lab-2-canot-discover-servicel-on-port-132](/images/ejpt/day-4/port-scanning/4-lab-2-canot-discover-servicel-on-port-132.png)
0 means fast scan but may miss versions, from 1 to 8 it is increasing number of probes and with better accuracy is services versions detection but it slower than 0 , 9 means trying all types of probes it is most accurate but it is the slowest


---

### Concept 4: [Operating Systems Detection]

**What it is:**
trying to know which operating system the target is running, there are many option to do this inside the Nmap, but it is hard operation even with Nmap options , so there is another options to do this which is using Nmap script engine which try to target serveries that may leak which OS they are running on which is more and more helpful information.
we have the option (-O) which is used for Operating system detection, as we can see
- ![11--O-for-OS-scan-nmap](/images/ejpt/day-4/port-scanning/11-o-for-os-scan-nmap.png)
as we can see it may in many cases see that Nmap can't detect the OS which we will use another option with it (--osscan-guess) which is trying to guess OS even if it isn't very confident
- ![12-osscan-guess-for-aggerissive-os-scan](/images/ejpt/day-4/port-scanning/12-osscan-guess-for-aggerissive-os-scan.png)
we can see also here it is can't also get the OS, that will lead us to use another way which is using Nmap scripting engine which is using the information of the services that leaks what OS it is running on or its host information if it is misconfigured by using this option (-sC) which is performing default and safe categories of Nmap scripting engine which is script scan that chooses the best scripts from those two categories for the specific services on the open ports  as we can see it gives us the kernel version and whish Distribution is used (here is Ubuntu)
- ![14-2-os-detection-with-the-sC 1](/images/ejpt/day-4/port-scanning/14-2-os-detection-with-the-sc-1.png)

---

### Concept 4: [NSE]

**What it is:**
Nmap Scripting Engine is feature of Nmap allows users to write and share specified scripts to automate various tasks like 
- port scan
- OS and Services versions scan
- Vulnerabilities scan
- Exploitation and Brute force
there are huge number of scripts that exist to see all scripts we use this command
```bash
ls /usr/share/nmap/scripts
```
![listing-all-scripts](/images/ejpt/day-4/port-scanning/listing-all-scripts.png)
it uses (.nse) extension which is can be developed by lua programming language, it also is including various categories like
- Discovery --> it contains scripts which gathers information about hosts, services, users, shares, or network resources without attempting attacks.
- Exploitation -->  it contains scripts which attempts to leverage a known vulnerability or weakness to verify whether it can be exploited.
- Brute Force --> it contains scripts which tries multiple username/password combinations or credentials to gain access to a service.
- Safe --> it contains scripts which performs non-intrusive checks that are unlikely to disrupt, crash, or negatively affect the target system.
and there much more categories but those are the most used or famous categories.
we can search for any script to get info about it by using this command:
```bash
nmap --script-help=<name>
```
![scrip-help-info](/images/ejpt/day-4/port-scanning/scrip-help-info.png)

we can use any script into Nmap search by using option (--script=name of script) as we can see
- ![13-using--script-by-using-nse](/images/ejpt/day-4/port-scanning/13-using-script-by-using-nse.png)
option (-sC) which is performing default and safe categories of Nmap scripting engine which is script scan that chooses the best scripts from those two categories for the specific services on the open ports  as we can see
- ![14-1-sC-for-using-default-scripts-from-nse-4](/images/ejpt/day-4/port-scanning/14-1-sc-for-using-default-scripts-from-nse-4.png)

---

## ⚙️ Commands Learned

> commands i have used

- Default Nmap command
	```bash
	# default nmap command it differs which user you are run it
	namp 192.207.193.0/24

	```
	![1-default-nmap-cidr-network-1](/images/ejpt/day-4/port-scanning/1-default-nmap-cidr-network-1.png)
	![1-default-nmap-cidr-network.-wireshark](/images/ejpt/day-4/port-scanning/1-default-nmap-cidr-network-wireshark.png)

- Skipping the host discovery and use fast scan
	```bash
	# -Pn --> to skip host discovery using ping
	# -F --> for fast scan by scanning common 100 ports
	namp -Pn -F 192.207.193.3
	```
	![5--Pn-F-nmap](/images/ejpt/day-4/port-scanning/5-pn-f-nmap.png)
	![5--Pn-F-wireshark](/images/ejpt/day-4/port-scanning/5-pn-f-wireshark.png)

- Skipping the host discovery and scan all ports or specific ports
	```bash
	# -p- --> to scan all ports by specify tcp or udp, but in default it is tcp
	namp -Pn -p- 192.207.193.3
	# -p6421,41288 --> to identify specific ports
	namp -Pn -p6421,41288 192.207.193.3
	```
	![6--Pn-p--nmap](/images/ejpt/day-4/port-scanning/6-pn-p-nmap.png)
	![6--Pn-p--wireshark](/images/ejpt/day-4/port-scanning/6-pn-p-wireshark.png)
	![6--Pn-p--specific-ports-nmap](/images/ejpt/day-4/port-scanning/6-pn-p-specific-ports-nmap.png)
	![6--Pn-p--specific-ports-wireshark](/images/ejpt/day-4/port-scanning/6-pn-p-specific-ports-wireshark.png)

- Stealthy scan
	```bash
	# -sS --> to apply stealthy or half open scan, which not completing the full 3 way handshake
	namp -Pn -sS -F 192.207.193.3
	```
	![7--sS-stealthy-nmap-1](/images/ejpt/day-4/port-scanning/7-ss-stealthy-nmap-1.png)
	![7--sS-stealthy-wireshark](/images/ejpt/day-4/port-scanning/7-ss-stealthy-wireshark.png)
	
- Full TCP connect scan
	```bash
	# -sT --> this is using full tcp connect scan, which is completing 3 way handshake
	namp -Pn -sT -p- 192.207.193.3

	```
	![8--sT-full-TCP-all-ports-nmap 1](/images/ejpt/day-4/port-scanning/8-st-full-tcp-all-ports-nmap-1.png)
	![8--sT-full-TCP-specific-port-wireshark](/images/ejpt/day-4/port-scanning/8-st-full-tcp-specific-port-wireshark.png)

- UDP scan, to scan UDP ports
	```bash
	# -sU --> to use UDP scan to scan the UDP ports
	namp -Pn -sU -p53 192.207.193.3

	```
	![9-sU-udp-scan-nmap](/images/ejpt/day-4/port-scanning/9-su-udp-scan-nmap.png)
	![9-sU-udp-scan-wireshark](/images/ejpt/day-4/port-scanning/9-su-udp-scan-wireshark.png)
	![3-lab-2](/images/ejpt/day-4/port-scanning/3-lab-2.png)

- Services versions detection (default intensity = 7)
	```bash
	# -sV --> for services versions detection
	namp -sS -sV -p- -T4 192.207.193.3
	```
	![10-sV-on-all-TCP-ports-nmap-2](/images/ejpt/day-4/port-scanning/10-sv-on-all-tcp-ports-nmap-2.png)
	![10-sV-on-all-TCP-ports-specific-port-wireshark-2](/images/ejpt/day-4/port-scanning/10-sv-on-all-tcp-ports-specific-port-wireshark-2.png)

- Aggressive services versions detection
	```bash
	# --version-intensity  --> it takes number from 0 to 9 , 0 is fastest but less accurate, while 9 is slowest but is the most accurate in services versions detection
	namp -sU -sV --version-intensity 8 -p132,177,234 192.207.193.3

	```
	![4-lab-2-canot-discover-servicel-on-port-132-1](/images/ejpt/day-4/port-scanning/4-lab-2-canot-discover-servicel-on-port-132-1.png)

- Operating System Detection
	```bash
	# -O --> for OS detection, it in many cases can't detect the OS
	namp -sS -T4 -sV -O -p- 192.15.80.3
	```
	![11--O-for-OS-scan-nmap-1](/images/ejpt/day-4/port-scanning/11-o-for-os-scan-nmap-1.png)

- Operating System Detection with guess option
	```bash
	# --osscan-guess --> is forcing Nmap to guess which operating system is on target, which is aggressive os scan option
	namp -sS -T4 -sV -O --osscan-guess -p- 192.15.80.3
	```
	![12-osscan-guess-for-aggerissive-os-scan-1](/images/ejpt/day-4/port-scanning/12-osscan-guess-for-aggerissive-os-scan-1.png)

- Operating System Detection by using the Nmap Scripting Engine
	```bash
	# -sC --> performing default and safe categories of Nmap scripting engine which is script scan
	namp -sU -F -T4 -sV -sC 192.15.80.3

	```
	![14-1-sC-for-using-default-scripts-from-nse](/images/ejpt/day-4/port-scanning/14-1-sc-for-using-default-scripts-from-nse.png)
	![14-2-os-detection-with-the-sC 1](/images/ejpt/day-4/port-scanning/14-2-os-detection-with-the-sc-1.png)

- Using NSE to get more info
	```bash
	# --script --> to use nse scripts to get more information
	namp -sU -p161 --script=snmp-info 192.15.80.3

	```
	![13-using--script-by-using-nse-1](/images/ejpt/day-4/port-scanning/13-using-script-by-using-nse-1.png)
	![13-2-using--script-by-using-nse-wireshark](/images/ejpt/day-4/port-scanning/13-2-using-script-by-using-nse-wireshark.png)

- Aggressive Scan (-sV + -O + -sC + --traceroute)
	```bash
	# -A --> it is Agressive scan which combines different options togther (-sV + -O + -sC + --traceroute)
	namp -sU -p161 -T4 -A 192.15.80.3

	```
	![15-aggerissive-scan-A](/images/ejpt/day-4/port-scanning/15-aggerissive-scan-a.png)


---

## ✅ End-of-Session Self Test

**Honest rating of today's session:** `[ ] 🔴 Struggling` | `[ ] 🟡 Getting it` | `[x] 🟢 Solid`

---

## 📌 Tags

#ejpt #week-1 #port-scanning
