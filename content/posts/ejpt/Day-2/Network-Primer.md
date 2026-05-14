---
title: "Network Primer"
date: 2026-05-14
slug: "network-primer"
draft: false
---

# Day 2 — [Networking Primer]

> **Date:** `=dateformat(date(today), "yyyy-MM-dd")` **Week:** 1 | **Day:** 2 **Module/Section:** (Networking Primer)

---

## 🎯 Session Goals

> What do you want to be able to DO by the end of this session?

- [x] Network Fundamentals ✅ 2026-05-14
- [x] Network Layer and how it works ✅ 2026-05-14
- [x] TCP Layer and how it works ✅ 2026-05-14

---

## 🧠 Concepts Learned

### Concept 1: [Protocol]

**What it is:**
protocol is set of rules the hosts use to connect or communicate with each other, each protocol represent specific service, written as set of rules
**Why it matters in a pentest:**
it is important to understand protocols because they are the milestones of communications between any hosts

---

### Concept 2: [Packets]

**What it is:**
packet is stream of bits that is represent data in the network layer(data + IP(Network layer) + Ports(Transport layer)) so it is data but it is now in Network layer, it is divided into two layers(header + payload) header contains information about packet or data, and payload is the actual data being transferred.

---

### Concept 3: [OSI]

**What it is:**
OSI(Open System Interconnection) is conceptual model representation of network and is divided into 7 layers each layer represent specific phase of network and how it works, it is theoretical model to facilitate the network in studying of troubleshooting, but actually in real word TCP/IP model is being used, the 7 layers are ( Application(7) --> Presentation(6) --> Session(5) --> Transport(4) --> Network(3) --> Data Link(2) --> Physical(1) )
![OSI-Model](/images/ejpt/day-2/network-primer/osi-model.png)

---

### Concept 4: [Network Layer]

**What it is:**
It is the layer responsible for logical addressing(IPs) and routing(routers), identifies the path that the data transfers from source to destination in internal networks or different networks(external networks), there are two types of IPs(IPv4 -->32 bits this is the foundation of the communication of the internet , IPv6 --> 128 bits this provides broader scope for IPs ) also has another protocol which is ICMP(Internet Control Message Protocol) which is used for error reporting and diagnostic, it uses echo requests and replies (ping utility), there another protocol is called DHCP(Dynamic Host Configuration Protocol) which assigns IPs to devices dynamically to avoid that two devices take the same IP.

---

### Concept 5: [Internet Protocol(IP)]

**What it is:**
it enables communication between different hosts by providing standardized way to identify hosts in different networks, it is responsible for addressing, routing, fragmentation, packets reassembling, packet structure, and subnetting(it is techniques to divides large IP networks into subnetworks or smaller networks to be easy to manage and enhance security and efficiency), it has two versions (IPv4 --> (x.x.x.x) set of 4 octets, 32 bits this is the foundation of the communication of the internet , IPv6 --> (x:x:x:x:x:x:x:x) represented in hexadecimals,128 bits this provides broader scope for IPs ), IPs can be classified into 3 types(unicast(1 to 1) , broadcast (1 to all) , multicast(1 to many in group)), there are classes of IPs as it is illustrated in this figure
![IP-classes](/images/ejpt/day-2/network-primer/ip-classes.png)
in IP header there are various data is written in binary values that IPv4 services references as they forward packets
![IP-header-format](/images/ejpt/day-2/network-primer/ip-header-format.png)
- **Version** — Identifies the IP version being used (IPv4 = 4).
- **Internet Header Length (IHL)** — Specifies the size of the IPv4 header.
- **Type of Service (ToS) / DSCP + ECN** — Defines packet priority, QoS handling, and congestion notification.
- **Total Length** — Indicates the total size of the IP packet (header + data).
- **Identification** — Unique value used to identify packet fragments belonging to the same original packet.
- **Flags** — Controls fragmentation behavior (e.g., Don’t Fragment flag).
- **Fragment Offset** — Shows the position of a fragment within the original packet.
- **Time To Live (TTL)** — Limits how many routers the packet can pass through before being discarded.
- **Protocol** — Identifies the upper-layer protocol being carried (e.g., TCP, UDP, ICMP).
- **Header Checksum** — Error-checking value for the IPv4 header.
- **Source IP Address** — IPv4 address of the sender.
- **Destination IP Address** — IPv4 address of the receiver.
- **Options** — Optional settings for special routing, security, or debugging purposes.
- **Padding** — Extra bits added to ensure the header length is a multiple of 32 bits.

---

### Concept 6: [Transport Layer]

**What it is:**
Transport Layer is the 4th layer and it is responsible for end to end communication and flow control and segmentation and ports is added to data here in this layer so data here is called(segment ---> data + port number), port is numerical number from 0 to 65535 which represent different protocol or services, from 0 to 1023 those are reserved ports for famous services like (80 --> http, 443 --> https), from 1024 to 49151 are registered for specific services like (3306 --> MySQL Database), in transport layer we have two main protocols TCP and UDP.

---

### Concept 7: [TCP]

**What it is:**
TCP(Transmission Control Protocol) which is connection oriented(which establishes a connection between client and server before any data is exchanging), reliable(which this connection is reliable or guarantee the delivery of data that the data has been delivered and not lost on the way and if it finds it is lost it resents it again) and is ordered data transfer(it ensures that data is delivered in correct order), TCP achieves the connection oriented via Three way handshake which is method used to achieve connection orientation between client and server, the client send packet with SYN(Synchronization) flag activated to the server with ISN(Initial Sequence Number --> random unique value) (1st way), then the server respond with SYN+ACK flags activated, and ACK is set as one more the ISN of SYN of client and the server SYN ISN is set to random number also(2nd way), then the client respond with only ACK flag activated which is one more the ISN of SYN of the server that was sent with SYN+ACK packet (3rd way) then the connection is established and after that client start sending the data
![three-way-handshake](/images/ejpt/day-2/network-primer/three-way-handshake.png)
and TCP header will be as the following
![TCP-header-fields](/images/ejpt/day-2/network-primer/tcp-header-fields.png)
- **Source Port** — Port number of the sending application.
- **Destination Port** — Port number of the receiving application.
- **Sequence Number** — Indicates the order number of the first byte in this TCP segment.
- **Acknowledgment Number** — Confirms receipt of data by specifying the next expected byte.
- **Data Offset (Header Length)** — Specifies the size of the TCP header.
- **Reserved** — Reserved bits for future use; normally set to zero.
- **Flags (Control Bits)** — Control connection behavior (e.g., SYN, ACK, FIN, RST, PSH, URG).
- **Window Size** — Specifies how much data the receiver can accept at one time.
- **Checksum** — Error-checking value for the TCP header and data.
- **Urgent Pointer** — Indicates the location of urgent data when the URG flag is set.
- **Options** — Optional TCP features such as Maximum Segment Size (MSS) and Window Scaling.
- **Padding** — Extra bits added so the header length becomes a multiple of 32 bits.

---

### Concept 8: [UDP]

**What it is:**
UDP(User Datagram Protocol) is the opposite of TCP which is connectionless(does not depend on creating conation between client and server), unreliable(which doesn't care about data is delivered or not it just sent it and doesn't check if packet lost or not), it is stateless(doesn't save the client state so the server doesn't recognize him each time so it doesn't save the client info or states on server),it is used for streaming(VoIP) and online gaming, UDP header format will be as following
![UDP-header-fields](/images/ejpt/day-2/network-primer/udp-header-fields.png)
- **Source Port** — Port number of the sending application.
- **Destination Port** — Port number of the receiving application.
- **Length** — Specifies the total size of the UDP header and data.
- **Checksum** — Error-checking value for the UDP header and transmitted data.

---


## ⚙️ Commands Learned

this command is used to list active TCP connections that our device is connected to or created

```bash
# for linux
netstat -antp
```
![netstat-linux](/images/ejpt/day-2/network-primer/netstat-linux.png)

```bash
# for windows
netstat -ano

```
![netstat-win](/images/ejpt/day-2/network-primer/netstat-win.png)


---

## ⚙️ Tools Used
### Wireshark
we have used tool called Wireshark, and it is one the best tools to analyze traffic on network, it shows it as OSI layers each layer with all the information sent via it or it role inside the sending operation, and here we have used it to analyze the Transport layer and Network layer as following
- ![wireshark-network](/images/ejpt/day-2/network-primer/wireshark-network.png) as we can see in the image of Wireshark this represents the Network layer and IP and its header values we have discussed it in section of IP like (TTL : 64 , Flags : Don't fragment is set , source and destination IPs , IP Version : 4) those info shows us the exactly packet that is sent via internet and let us to see what is inside each layer.
- ![wireshark-transport](/images/ejpt/day-2/network-primer/wireshark-transport.png)as we can see in the image exactly the TCP 3 way handshake to build connection between client and server, as we discussed it before in TCP section
- ![wireshark-transport-tcp](/images/ejpt/day-2/network-primer/wireshark-transport-tcp.png) here we can find all info about TCP protocol and all header info we have discussed in the TCP section, and the ISN of SYN packet and only flag of SYN is set because this is the first packet in the 3 way handshake method, also we can see that the port numbers(source + destination) is set to the data.

---

**Honest rating of today's session:** `[ ] 🔴 Struggling` | `[ ] 🟡 Getting it` | `[x] 🟢 Solid`

---

## 📌 Tags

`#ejpt` `#Networking`
