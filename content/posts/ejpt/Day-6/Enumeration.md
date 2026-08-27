---
title: "Enumeration"
date: 2026-08-27
slug: "enumeration"
draft: false
series:
  - "eJPT"
weight: 8
ShowToc: true
---


---

## Session Goals

> Inside this session we will practicing Enumeration on different services like FTP, SMB, Web server, MYSQL, SSH and SMTP

---

## Concepts Learned

> The Concepts i have learned at this session

### Concept 1: [Enumeration]

**What it is:**
Enumeration is active process of gathering detailed information about specific target or service, it is the process of querying the target system by interacting with it to get more information that  might be useful for other steps of the penetration testing process, there are three types of Enumeration:
- Network Enumeration -->> trying to find number of active hosts and IPs by using scanning protocols like ICMP and SNMP and their applications
- Service Enumeration -->> trying to find or discover the running services and the open ports and their configurations and versions exist on the target system 
- User Enumeration -->> trying to get the usernames of accounts exist on the target system 

---

### Concept 2: [FTP Enumeration]

**What it is:**
FTP(File Transfer Protocol on port 21 TCP) is a protocol used to transfer files from one host to another one, by Enumerating FTP we try to get more information that could be later exploit to get advantage on the FTP server so we can get credentials so we can login with them.
To do this we will use auxiliary modules inside Metasploit:
- auxiliary modules --> are helping modules which have its objective, each auxiliary can do something, each one has its job
For doing the FTP Enumeration, those are the steps:
1. scanning the target IP so we can identify if the FTP service work or not, the following appears that the port 21/TCP(which is the default port of FTP service) is open![1-portscan-for-ftp](/images/ejpt/day-6/enumeration/1-portscan-for-ftp.png)
2. After that, we will try to get more information about the FTP service that is running like its version using specific auxiliary module (ftp_version), as we can see it gives us the version of the running ftp service (ProFTPD 1.3.5a) and its name also, all those inside something is called FTP Banner which appears to the clients who successfully connected to the FTP server![[posts/eJPT/Day-6/Enumeration-images/2-ftp-version-checker.png|672]]
3. Now we are in login phase, we now will try to login into the ftp service without any credentials as anonymous credentials using auxiliary module (anonymous), as we can see this ftp server disallow the anonymous login, so this trial failed![8-check-anonymous-access](/images/ejpt/day-6/enumeration/8-check-anonymous-access.png)
4. Now we will try to get credentials by brute forcing auxiliary module (ftp_login), but before that we need to set wordlists for usernames and passwords so it can be used in brute forcing, and as we we can see in the following images we have found two successful credentials, we will use them so we can access to the ft![3-ftp-login-bruteforce-wordlists](/images/ejpt/day-6/enumeration/3-ftp-login-bruteforce-wordlists.png)![4-bruteforce-result-found-username-and-password](/images/ejpt/day-6/enumeration/4-bruteforce-result-found-username-and-password.png)![5-another-username-and-password](/images/ejpt/day-6/enumeration/5-another-username-and-password.png)
5. Final step we will login with the credentials we found, using ftp command which allow us to connect to the ftp of the targeted server, and after that we will input our credentials which username and password and as we can see we have successfully got into the server and we can even download or upload as we can see![6-first-user-test-login](/images/ejpt/day-6/enumeration/6-first-user-test-login.png)![7-second-user-test-login](/images/ejpt/day-6/enumeration/7-second-user-test-login.png)
For conclusion, we try to get more information about the FTP service so it helps us in our information gathering phase that is the FTP Enumeration.

---

### Concept 3: [SMB Enumeration]

**What it is:**
SMB(Server Message Block) is client to server communication protocol, it is used for shared access to files, directories and printers over a network (LAN), it provides an authenticated Inter process communication mechanism, by enumerating the SMB we try to get more specific information about the one who is running on the target, Its application on Linux is called SAMBA which is an implementation of SMB on Linux and it allows the sharing between Windows and Linux, it uses port 445 over TCP but originally it uses port 139 over NetBIOS.
For doing the SMB Enumeration, those are the steps
1. The first of all we will scan the target IP using Nmap by using stealth scanning, and scan all ports, as we can see in the image there are two open ports 139 and 445 which are the ports of the SMB or its implementation SAMBA ![1-find-all-tcp-running-services-using-nmap](/images/ejpt/day-6/enumeration/1-find-all-tcp-running-services-using-nmap.png)here is another scan using UDP ports![2-find-smb-port-that-run-on-udp](/images/ejpt/day-6/enumeration/2-find-smb-port-that-run-on-udp.png)
2. After that, we will try to gather specific information about the SMB version using module (smb_version), as we can see in the image it is (samba 4.3.11) running on Ubuntu distribution, this information we will need it in the exploitation ![3-smb-version-samba-version](/images/ejpt/day-6/enumeration/3-smb-version-samba-version.png)
3. the Next thing we need to find the existed users on the SMB server by using (smb_enumusers) module, we can see that there are users existing ![4-smb-users-finding](/images/ejpt/day-6/enumeration/4-smb-users-finding.png)
4. also we need to know each user share, or what each user share on the SMB server by using (smb_enumshares) modules, share in SMB is a directory or set of resources which are exposed on the SMB server and its owner identifies what to appear and who can access it![5-smb-shares-finding](/images/ejpt/day-6/enumeration/5-smb-shares-finding.png)we can use anther tool to get more information like shares, the tool is called smbclient![8-using-smbclient-to-find-more-information](/images/ejpt/day-6/enumeration/8-using-smbclient-to-find-more-information.png)
5. Now we will try to find credentials for login into the SAMBA server by using brute forcing auxiliary module (smb_login), by setting specific username from one we found before and then putting the password wordlist, as it appear we put the username as admin and we found its password, also in we tried on another user is called emma![6-bruteforce-to-get-admin-user-password](/images/ejpt/day-6/enumeration/6-bruteforce-to-get-admin-user-password.png)![7-bruteforce-to-get-emma-user-password 1](/images/ejpt/day-6/enumeration/7-bruteforce-to-get-emma-user-password-1.png)
6. Now we will use the credentials we have found to get into the SMB server using a tool is called smbclient,as we can see we should put username and the target share from shares we found before then we will put the password, and as we can see we get into the server and even we have downloaded a file![9-displaying-the-actual-smb-and-logging-with-share-public](/images/ejpt/day-6/enumeration/9-displaying-the-actual-smb-and-logging-with-share-public.png)also for the another user which is emma![10-displaying-the-actual-smb-and-logging-with-another-user-emma-and-share-emma](/images/ejpt/day-6/enumeration/10-displaying-the-actual-smb-and-logging-with-another-user-emma-and-share-emma.png)
7. Also we should find if we can login as anonymous without needing username or password, on this specific target we can see shares without username or password so the anonymous login is allowed![14-anonymous-full-session-is-allowed-without-need-to-username-or-password](/images/ejpt/day-6/enumeration/14-anonymous-full-session-is-allowed-without-need-to-username-or-password.png)and now we will login, as we can see we got in without any credentials![15-login-with-give-the-share-name-and-without-username-or-password](/images/ejpt/day-6/enumeration/15-login-with-give-the-share-name-and-without-username-or-password.png)we can use another tool to login into the SMB server either anonymous or with credentials, but in the image we have logged as anonymous ![16-login-into-rpcclient-without-any-username-or-password 1](/images/ejpt/day-6/enumeration/16-login-into-rpcclient-without-any-username-or-password-1.png)
8. we can get more information about the host OS and NetBIOS computer name using Nmap scripting engine scripts like (smb-os-discovery.nse) which try to get the OS and its version and other information like NetBIOS computer name which is (SAMBA-RECON)![12-smb-os-discovery-by-nmap-scripts](/images/ejpt/day-6/enumeration/12-smb-os-discovery-by-nmap-scripts.png)
For conclusion we can see that we are trying to find information as we can about the SMB using different tools and different modules so this information will help us on next penetration testing phase.
---

### Concept 4: [WEB SERVER Enumeration]

**What it is:**
Web Server is software that serves websites data on the web by using HTTP to facilitate the communication between client and webserver:
- port 80/TCP --> unencrypted communication --> HTTP
- port 443/TCP --> secured and encrypted communication(with SSL/TLS) --> HTTP
Web Server Enumeration is trial to gather more information about the webserver that runs on the target like:
- version of webserver
- which webserver is running
- HTTP headers
- brute forcing the directories to find hidden ones
the steps of web server enumeration as following:
1. the first thing we will try to find the version of the web server and its type![1-find-webserver-version-using-http](/images/ejpt/day-6/enumeration/1-find-webserver-version-using-http.png)so as we can see it s is Apache web server running on Ubuntu Linux distribution and its version is (2.4.18), those information will help us in the exploitation phase to find vulnerabilities related to this type of webserver and this specific version
2. we can also run another auxiliary module to get the http headers which will reveal more information about the webserver, it is another way to get the name and version of the webserver![2-use-http-headers-to-get-more-information-about-webserver](/images/ejpt/day-6/enumeration/2-use-http-headers-to-get-more-information-about-webserver.png)and as we can see there are 3 headers found and one of them is SERVER which reveals information about the webserver's name and version, as i say it is another way
3. After that we will use another auxiliary module to get the robots.txt content which has allowed and  disallowed to be indexed by the search engine, which we can find from it more information about the webserver content![3-using-robots-to-get-disallowed-directories-that-the-search-engine-disallowed-to-index-them](/images/ejpt/day-6/enumeration/3-using-robots-to-get-disallowed-directories-that-the-search-engine-disallowed-to-index-them.png)as we can see that the admin of the webserver disallowed 2 directories or endpoints from being indexed by the search engine, this means that they are existed but we can't find them by normal searching, as we can see in the following image![4-test-the-hidden-dirs-detected-in-robots-file](/images/ejpt/day-6/enumeration/4-test-the-hidden-dirs-detected-in-robots-file.png)they are exist but we should discover them by ourselves since they will not appear by  normal google searching
4. Now we will try to find the interested directories that may exist by using wordlist that contains popular directories names![5-find-hidden-directories](/images/ejpt/day-6/enumeration/5-find-hidden-directories.png)we found a lot of directories that we can't get by normal search, and also we find the two that was disallowed by the admin to be indexed by search engine, also we are trying to find files that exist inside those directories as following![6-bruteforce-to-find-files-exsited-in-dirs](/images/ejpt/day-6/enumeration/6-bruteforce-to-find-files-exsited-in-dirs.png)
5. At this step we are trying to find credentials so we can access the login page which we found before /secure endpoint, by brute forcing auxiliary module![7-1-bruteforce-authentication-form-of-website](/images/ejpt/day-6/enumeration/7-1-bruteforce-authentication-form-of-website.png)![7-2-find-username-and-password](/images/ejpt/day-6/enumeration/7-2-find-username-and-password.png)we got credentials and we logged in with them and it have been succussed like following ![7-3-login-with-credintial-that-we-bruteforced](/images/ejpt/day-6/enumeration/7-3-login-with-credintial-that-we-bruteforced.png)we can also use another module to get the interesting directories which search within wordlist about the popular directories names that could have interesting information![9-bruteforce-intersteing-directories](/images/ejpt/day-6/enumeration/9-bruteforce-intersteing-directories.png)
6. Now we are brute forcing to get information about user directories which could reveal information about the users on Apache server, for simplification  the Apache server gives or makes directory for each user with its same name of username, so we are trying to find those directories which is the same as the their users so we actually find the usernames![8-1-find-user-directories-of-apache](/images/ejpt/day-6/enumeration/8-1-find-user-directories-of-apache.png)![8-2-all-users-have-been-found](/images/ejpt/day-6/enumeration/8-2-all-users-have-been-found.png)as we can see we have found all users existed on the Apache server.
7. there is another auxiliary module trying to abuse the misconfiguration by sending data via specific HTTP header which is PUT (http_put) by trying to upload or delete content using PUT or DELETE requests which they are http headers, PUT is the default which is trying to upload file to abuse the misconfiguration, and we can switch to DELETE so we can send DELETE request to delete the content![10-for-abusing-misconfigurations](/images/ejpt/day-6/enumeration/10-for-abusing-misconfigurations.png)
At the end as all other services by enumerating the Web Server we are trying to get more specified information about the specific webserver.
---

### Concept 5: [MYSQL Enumeration]

**What it is:**
MYSQL(Structured Query Language) is open source relational database Management system the stores records of different types of data, and it is used to store data for web applications, works on port 330/TCP but companies always change the default port to deceive attacker but the attacker simply can scan all ports to find which port MYSQL runs on, MYSQL is designed to store, manage and retrieve data efficiently, by enumerating MYSQL we are trying to find information about this system as we can like its version and if we can dump the data that is stored in it.
For doing this we will do:
1. First, we need to scan all ports to find which port does the MYSQL runs on, and as we can see it runs on its default port 330/TCP![1-scan-all-tcp-ports-to-find-mysql-run-on-which-port](/images/ejpt/day-6/enumeration/1-scan-all-tcp-ports-to-find-mysql-run-on-which-port.png)
2. Second, we will get MYSQL version and as we can see in the following image the version of MYSQL server is (5.5.61) and as a beside information we got the OS which is (ubuntu) and its version also![2-run-aux-module-to-find-mysql-version](/images/ejpt/day-6/enumeration/2-run-aux-module-to-find-mysql-version.png)
3. Third, we are trying to brute forcing to get the credentials to able to login to MYSQL server and expose the data inside it, as we can see in the image this auxiliary module puts the default username as root(which is quite the most common username as root username) then we put our wordlist for password, we can put verbose option either true or false which says reveal detailed information or not, and as we can see it has found root's password which is (twinkle)![3-bruteforcing-to-find-password-of-root-user-to-have-full-access-to-the-entire-database](/images/ejpt/day-6/enumeration/3-bruteforcing-to-find-password-of-root-user-to-have-full-access-to-the-entire-database.png)
4. Fourth, will try to connect to server with the leaked credentials to see how it will response, as it appears in the image it has connected successfully and it shows us more information about the server like the exactly OS, its architecture and data directory![4-1-enumerate-using-the-leaked-credentials-of-root-user-to-get-more-info-like-mysql-version-and-os-distro](/images/ejpt/day-6/enumeration/4-1-enumerate-using-the-leaked-credentials-of-root-user-to-get-more-info-like-mysql-version-and-os-distro.png)and in the following image we can see it reveals the users that exists on MYSQL server and its hashed passwords![4-2-different-existed-user-and-their-pass-hashes](/images/ejpt/day-6/enumeration/4-2-different-existed-user-and-their-pass-hashes.png)we can use separate auxiliary module to make hash dump so we can later crack them![8-dumping-hasches-of-users-to-crack-them-later](/images/ejpt/day-6/enumeration/8-dumping-hasches-of-users-to-crack-them-later.png)
5. Fifth, we will use the revealed credentials to send quires so we can manipulate the data records in MYSQL server, the following image appear that we sent a SELECT query to reveal the version, since SELECT is working all other queries should work also![5-1-executing-different-sql-quiries-to-get-more-information](/images/ejpt/day-6/enumeration/5-1-executing-different-sql-quiries-to-get-more-information.png)like the following image appears we use different query to show what databases are existed, and we can do show what exist inside each database table![5-2-use-more-types-of-quiries](/images/ejpt/day-6/enumeration/5-2-use-more-types-of-quiries.png)we can do the same thing of the previous image but with different auxiliary module like the following image illustrates![6-extract-databases-and-its-tables-using-aux-schema](/images/ejpt/day-6/enumeration/6-extract-databases-and-its-tables-using-aux-schema.png)
6. Sixth, we can brute force to find the existed files inside MYSQL server, to do this we will use auxiliary module and set file names wordlist, and as we can see it found more than file already so if someone is already interest we can use it![7-find-existed-files-and-directories](/images/ejpt/day-6/enumeration/7-find-existed-files-and-directories.png)
7. Finally, we can brute force to find writeable directories(the directories that i could write on it), and as it appears we have already found two that are existed![9-finding-dirs-that-i-could-write-on-them](/images/ejpt/day-6/enumeration/9-finding-dirs-that-i-could-write-on-them.png)
At conclusion, we can see as other enumeration MYSQL enumeration is like them we try to find information as we can to use them for the later stages of penetration testing.
---

### Concept 6: [SSH Enumeration]

**What it is:**
SSH(Secure Shell) is remote administration protocol that provides encrypted remote access over port 22/TCP by default, it is like the shell on the Linux but it is remotely so if we have access to SSH terminal we are now controlling the target, but we enter of the credentials access we got, but there is a solution which is privilege escalation which is technique to give us more permissions than the allowed ones, but we will do this later.
For now the steps to get more information are:
1. Initially, we need to know on which port does the SSH exist, as we say before it may not be the default port as the companies change it, but in our case it is the default one which is 22/TCP![1-find-on-which-port-ssh-service-is-running](/images/ejpt/day-6/enumeration/1-find-on-which-port-ssh-service-is-running.png)
2. Secondly, we will try to get the SSH version and its OS that it is running on, as we can see we found the SSH version and the server encryption fingerprint as we said before it provides encrypted communication, and it gives also detailed information about all things ![2-1-find-ssh-version](/images/ejpt/day-6/enumeration/2-1-find-ssh-version.png)![2-2-morse-info-from-version-aux-module-like-os-distro-and-its-version](/images/ejpt/day-6/enumeration/2-2-morse-info-from-version-aux-module-like-os-distro-and-its-version.png)
3. Thirdly, we are trying brute forcing to find the proper credentials so we can create an authenticated communication channel, we will input usernames and passwords wordlists, and as it appears it actually found credentials, also as we can see it uses password for authentication that's why we used this auxiliary module (ssh_login) but if the authentication by the Key pair (public and private keys) we will use this auxiliary module (ssh_login_pubkey), it also have connecting to SSH server by opening a session called session 1 with the credentials it found before ![3-1-bruteforcing-to-get-username-and-password](/images/ejpt/day-6/enumeration/3-1-bruteforcing-to-get-username-and-password.png)
4. Finally, we can normally interact with the opened session it opened before as we can see all commands works efficiently, we can list directory or either change directory and so on all commands that this user is able to do we can do it ![3-2-connecting-to-ssh](/images/ejpt/day-6/enumeration/3-2-connecting-to-ssh.png)![3-3-chnaging-directory-and-finding-flag](/images/ejpt/day-6/enumeration/3-3-chnaging-directory-and-finding-flag.png)
At conclusion, we can see as other enumeration SSH enumeration is like them we try to find information as we can to use them for the later stages of penetration testing
---

### Concept 7: [SMTP Enumeration]

**What it is:**
SMTP(Simple Mail Transfer Protocol) is communication protocol that is used to transfer emails works over port 25/TCP by default and if there is an SSL certificate it will run over port 465/TCP and 587/TCP, we are enumerating SMTP to gather information that we will use it for other attacks so it operates other attacks.
The steps of doing SMTP Enumeration:
1. First, we will try to find which port does SMTP works on and as we can see it works on 25 which says that there is no SSL certificate activated![1-search-for-smtp-port-number](/images/ejpt/day-6/enumeration/1-search-for-smtp-port-number.png)
2. Second, we will try to grab SMTP Banner which reveals information like name and the domain used in emails![2-find-smtp-name-and-banner-and-domain-used-in-emails](/images/ejpt/day-6/enumeration/2-find-smtp-name-and-banner-and-domain-used-in-emails.png)
3. Third, we are trying to enumerate the users or finding the existed users by using two internal commands(VRFY --> confirms names of valid users and EXPN --> reveals actual address fo users aliases and lists of emails)![3-enumeration-user-names-from-unix-list](/images/ejpt/day-6/enumeration/3-enumeration-user-names-from-unix-list.png)we can use another tool to find usernames which is called (smtp-user-enum) by giving it the targeted domain or IP and usernames wordlist![4-2-using-another-wordlist-to-enum-users-another-way](/images/ejpt/day-6/enumeration/4-2-using-another-wordlist-to-enum-users-another-way.png)we will try connecting to server to see if two users exist and how it will respond to us for each one (admin (existed) - commander (not existed))![5-connecting-to-smtp-to-check-if-user-admin-and-commander-exsit-or-not](/images/ejpt/day-6/enumeration/5-connecting-to-smtp-to-check-if-user-admin-and-commander-exsit-or-not.png)
4. Fourth, we will use telnet and connect to SMTP server to check the available commands![6-using-telnet-to-connect-to-smtp-and-check-available-commands](/images/ejpt/day-6/enumeration/6-using-telnet-to-connect-to-smtp-and-check-available-commands.png)
5. Finally, we now connected to the SMTP server and sending fake email to root user![7-2-send-fake-email-to-root-user-by-connecting-to-smtp-by-sendemail-command](/images/ejpt/day-6/enumeration/7-2-send-fake-email-to-root-user-by-connecting-to-smtp-by-sendemail-command.png)we can use telnet also to send it ![7-send-fake-email-to-root-user-by-connecting-to-smtp-using-telnet](/images/ejpt/day-6/enumeration/7-send-fake-email-to-root-user-by-connecting-to-smtp-using-telnet.png)
At conclusion, we can see as other enumeration SMTP enumeration is like them we try to find information as we can to use them for the later stages of penetration testing and operates other attacks.
---

**Honest rating of today's session:** `[ ] 🔴 Struggling` | `[ ] 🟡 Getting it` | `[x] 🟢 Solid`

---

## 📌 Tags

#ejpt #Enumeration #week-1 
