---
title: "Introduction to information gathering"
date: 2026-05-01
slug: "introduction-to-information-gathering"
draft: false
---

﻿---
title: "Introduction to information gathering"
date: 2026-05-01
slug: "introduction-to-information-gathering"
draft: false
tags:
  - ejpt
  - recon
---
Information Gathering (Reconnaissance)
	 Reconnaissance is the first phase in penetration testing operation and  is to collect or gather information that is public available (passive reconnaissance) or private (active reconnaissance) about organization or individual or system or website and so on (information about our target)
		 1- passive information gathering --> collect information that is public available without any active engaging with the target (IP and DNS information - Domain names - web technologies - subdomains and so on)
		 2- active information gathering --> collecting information that isn't public available with active engaging with the target (need authorization from target) (port scanning - information about internal network infrastructure - enumeration of gathered information )
	Target scoping (In-Scope - Out-Scope) --> is the process of defining what systems, apps and networks are allowed to test or not to test, it is the rules of engaging (what am i allowed to collect information about?), during reconnaissance the target is defined via one of those ways 
		1- Domain based target (may include primary domain  or subdomain  --> example.com or admin.example.com) 
		2- IP based target (common in internal or lab environments --> single IP (192.168.1.1) or network range (192.168.1.0/24))
		3- Application based target (focus on app only not the entire server --> web app or login portal or specific API endpoint)
	here are the differences between 
		1- In Scope --> assets i allowed to (collect info from - scan - enumerate)
		2- Out Scope --> assets i am not allowed to test or interact with (third party services - external domains not listed in scope - systems owned by other organization)
![scope](/images/ejpt/day-0/introduction-to-information-gathering/scope.png)
	reconnaissance is about collecting useful information not all information with well defined scope i keep reconnaissance focused and efficient and relevant to later stages.
	now i will discuss the difference between passive and active reconnaissance in some of details:
		1- Passive Reconnaissance --> collect information that is public available without any active engaging with the target, without direct interaction with the target, usually performed first and lower risk of detection, some of examples of passive recon data :
			1- DNS Records
			2- Domain registration information
			3- Public website content
			4- Search engines results(Google Dorking-->techniques to gather info using special words in searching process to get information that is not common to get)
			5- Public available email addresses
		2- Active Reconnaissance --> collecting information that isn't public available with active engaging with the target, sends traffic to target, increase visibility, performed after passive recon,  some of examples of active recon data:
			1- live hosts
			2- open ports (using N-map)
			3- running services
			4- network responses
		#Hint  Always perform passive reconnaissance before active reconnaissance.
	During info gathering we are trying ==to build map of target==, examples of those  information : 
		1- Domains and Subdomains
		2- IP addresses
		3- Hosting Infrastructure
		4- Technologies and services ( used web technologies )
		5- Open ports
		6- Publicly exposed information
	![recon mapping flow](/images/ejpt/day-0/introduction-to-information-gathering/recon.png) 
		1- start by defining the target scope (In-scop and Out-scope)
		2- starting the passive reconnaissance (domains - subdomains - DNS records - [^1]WHOIS data - [^2]website footprinting - OSINT techniques )
		3- after the passive recon we start the active reconnaissance (host discovery -  port scanning - basic service identification - DNS zone transfer testing ) 
		4- optimize the findings
		5- start the enumeration and exploitation
	we can simple define recon strategy as following:
		1- Define the target
			1- define IP addresses, domains , network ranges
			2- define In-scope and Out-scope
		2- Perform Passive reconnaissance
			1- gather public info
			2- define potential attack surfaces (what is capable to be attacked)
			3- build initial understanding of target
		3- Perform Active reconnaissance
			1- define live hosts
			2- define open ports
			3- detect exposed services
		4- Document and Organize the findings
			1- record domains, IPs, ports
			2- prepare information for enumeration
			3- avoid repeating work later
	there are some mistakes we should avoid
		1- starting scanning without defining scope
		2- skipping passive recon
		3- scanning everything instead of relevant to target
		4- not documenting results
		5- trusting tools output without verification
	by avoiding those mistakes the accuracy will increased.
	here are some advices:
		1- Target scoping defines what you are allowed to test
		2- passive recon comes before active recon
		3- ==reconnaissance== is about gathering ==meaningful data==
		4- A structured and documented approach improves results and efficiency


#Hint always avoid to gather all info about the target try to get only useful info about in scope 
only (not quantity but useful)
slug: "introduction-to-information-gathering"
date: 2026-05-01
draft: false
---
[^1]: WHOIS is a request and response protocol that follows the [RFC 3912](https://www.ietf.org/rfc/rfc3912.txt) specification. A WHOIS server listens on TCP port 43 for incoming requests. The domain registrar is responsible for maintaining the WHOIS records for the domain names it is leasing. The WHOIS server replies with various information related to the domain requested. Of particular interest, we can learn:
	
	- Registrar: Via which registrar was the domain name registered?
	- Contact info of registrant: Name, organization, address, phone, among other things. (unless made hidden via a privacy service)
	- Creation, update, and expiration dates: When was the domain name first registered? When was it last updated? And when does it need to be renewed?
	- Name Server: Which server to ask to resolve the domain name?

[^2]: Footprinting is the art of gathering essential information from target organizations about their networks and systems for potential vulnerabilities, can be passive Footprinting or active Footprinting
