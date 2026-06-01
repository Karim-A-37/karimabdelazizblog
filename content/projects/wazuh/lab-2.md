---
title: "Lab 2 - Malware Detection with Wazuh"
date: "2025-12-09"
slug: "wazuh-lab-2-malware-detection"
description: "Malware detection using Wazuh FIM, CDB hash lists, VirusTotal, Windows Defender log forwarding, and Sysmon for fileless malware detection."
tags:
  - "wazuh"
  - "malware"
  - "fim"
  - "virustotal"
  - "sysmon"
series:
  - "Wazuh Labs"
weight: 2
draft: false
ShowToc: true
TocOpen: false
---

# Lab2: Malware Detection Using Wazuh

Malware is malicious software that is installed on a computer without the user's permission. Malware can be used to encrypt (Ransomware), steal (info stealer), and spy on users. Malware detection is the process of detecting and analyzing suspicious software and files on systems and networks. Most security products detect malware by using previous malware signatures to match and detect it or analyze malicious behavior. There are sophisticated malwares that can evade detection systems by using multiple techniques when they enter the system. Wazuh uses different techniques and methods to detect malicious files. We will learn about those methods and integrate third-party tools to help Wazuh improve malware detection.

## Types of Malware

1. **Viruses** → Malware that attaches itself to files and programs, then spreads by infecting other files. Can cause damage by corrupting data (ILOVEYOU virus).

2. **Worms** → Malware that copies or replicates itself and spreads via networks by exploiting security holes to infect other connected systems (Blaster worm).

3. **Trojans** → Malicious software that looks like legitimate files or programs, lets cybercriminals enter without needing permissions. In other words, malicious code inside legitimate programs (ZEUS steals financial info).

4. **Ransomware** → Malware that encrypts all data existing on a system to get paid to decrypt them. One of the most high-severity malwares (WannaCry and Locky).

5. **Spyware** → Malware designed for spying by covertly monitoring and collecting info from infected systems, like sensitive info, passwords, and browsing habits (CoolWebSearch via pop-up ads, FinSpy).

6. **Rootkits** → Malware that gets privileged access to systems without being noticed, hides attacker presence and keeps control of the infected system (Alureon, BMG Rootkit).

Malware is spread via different ways like phishing emails, malicious downloads, infected websites, and physical devices like USBs. Cybercriminals are always developing their techniques to exploit new vulnerabilities using malware, which makes security solutions also keep developing to deal with sophisticated malware.

## Wazuh Malware Detection Methods

Wazuh offers several methods to detect malware through a combination of log analysis, intrusion detection, and threat intelligence. It also provides the ability to execute custom scripts for automated reaction activities. Here are some of Wazuh's methods for malware detection:

1. **Threat Detection Rules and File Integrity Monitoring (FIM)** → In this method, Wazuh uses its built-in capability to detect any critical file modification. Here are some of those capabilities:
   - Set of predefined continuously monitored threat detection principles (to identify suspicious activities, events, patterns that may lead to malware infections or security breaches)
   - FIM monitors modifications to files and directories. Wazuh generates an alert when unauthorized changes occur

2. **Rootkit Behavior Detection** → Using rootcheck function to detect anomalies that might indicate malware in an endpoint, such as:
   - Rootkits are a form of malware that can hide their presence and malicious actions on systems. Wazuh identifies rootkit-like activities using behavior-based detection techniques
   - Wazuh searches for any attempts of privilege escalation or hidden files and processes, then generates an alert

3. **Third Party: VirusTotal Integration** → Wazuh detects malicious files via integration with VirusTotal:
   - VirusTotal is a web-based service that scans files and URLs for potential malware using different antivirus engines and multiple threat intelligence sources
   - When Wazuh catches a file or URL that is suspected, it sends it to VirusTotal to scan it with multiple antivirus engines. Then Wazuh alerts the findings of VirusTotal. The confidence is increased if the file or URL is detected multiple times with multiple antivirus engines

4. **Third Party: YARA Integration** → Wazuh detects malware samples using YARA, which is an open-source tool that identifies and classifies malware artifacts based on their binary patterns:
   - YARA is a powerful tool that lets you write your own rules to find malware and certain patterns in files and processes
   - Can use YARA integration to create custom signatures that detect specific malware strains or behaviors that are not covered by the normal Wazuh rules

## Malware Detection Using FIM

When a system gets compromised by malware, it may create new files or edit existing files like:

1. Executable files (.exe, .dll, .bat, and .vbs)
2. Configuration files (.cfg and .ini)
3. Temporary files (.tmp)
4. Registry entries
5. Log files (.log)
6. Payload files
7. Hidden files and directories
8. Batch scripts (.bat)
9. PowerShell (.ps1)
10. Specially crafted documents with a malicious payload (.doc, .xls, and .pdf)

Using this information, we can create an FIM rule in Wazuh to detect any file changes. However, we will get a high number of false positive alerts. To solve this problem, we can focus on specific directories.

Now we will learn how to create Wazuh rules to detect some common malware patterns.

## First Case: Configuring and Testing FIM

FIM is technology that monitors the integrity of system and application files. It guards sensitive data, apps, and device files by monitoring, scanning, and confirming their integrity. It detects changes on critical files in the network. Because Wazuh is open source (OSSEC), it has open source FIM.

OSSEC (Open Source HIDS Security) is open source, free host-based intrusion detection system. When a user or process creates, modifies, or deletes a monitored file, the Wazuh FIM module generates an alert. By default, the FIM is enabled on the Wazuh agent. The following are the steps to test FIM:

1. We need Wazuh manager → Ubuntu
2. We need Wazuh agent → Purple
3. FIM module configuration file is present in the `<syscheck>` tag under the ossec.conf file located in `/var/ossec/etc/ossec.conf`
4. We only need to add the directories to be monitored under `<syscheck>` tag. The following configuration will monitor specified files and directories for any types of changes or modifications:
   - Inside `/var/ossec/etc/ossec.conf` we will search for `<syscheck>` tag
   - Inside `<syscheck>` tag we will find `<frequency>` tag which represents the frequency that `<syscheck>` tag is executed. By default, we will put inside this tag number of seconds. In our case is 43200s, which is every 12 hours
   - `<disabled>` tag to enable and disable FIM. In our case, we will put "no" to enable it
   - `<directories>` tag identifies the directories or files to be monitored. It takes different attributes, like:
     - **realtime** → to monitor the directory or file in real time
     - **whodata** → to monitor the directory or file in real time but add more data than realtime like:
       - The user who has edited the file
       - The file name that has been edited
     - **report_changes** → appears the changes that happened. It appears the content before and content after changes
   - `<directories whodata="yes" report_changes="yes">/home/purple</directories>` we monitor here the /home/purple directory
   - We can see:
     - decoder.name: syscheck_integrity_changed → This field represents a new entry related to system checks
     - full_log: File '/home/purple/FIMTEST' modified → represents that file FIMTEST has been modified
   - `<ignore>` tags indicate files or directories to ignore during the monitoring process

## Second case: Detecting suspicious files in the PHP server using the FIM module

PHP is known for its simplicity, speed, and flexibility. Currently, there are a very huge number of websites using PHP. We can find PHP files inside those directories (`/var/www/html/`, `/var/www/public_html/`, root directory). Now we will test malware using FIM module in PHP server, steps:

1. Wazuh manager --> ubuntu
2. Wazuh agent has PHP --> purple
3. We will create a Wazuh rule to detect file creation and modification on the PHP server
4. We will add different types of PHP file extensions under the `<field>` tag of the Wazuh rule
5. We will go to Server management in navigation bar of Wazuh dashboard
6. We will choose rules then choose add new rules file
7. We will name the rule (`custom_fim.xml`)
8. This is the rule:

```xml
<group name="linux, webshell, windows,">
    <!-- Detect suspicious web-shell file creation -->
    <rule id="100500" level="12">
        <if_sid>554,550</if_sid>
        <field name="file" type="pcre2">(?i)\.(php|php[3-8]
        |phtml|phps|phar|asp|aspx|jsp|cshtml|vbhtml)$</field>
        <description>[File creation]: Possible web shell scripting file ($(file)) created</description>
    </rule>
</group>
```

   - 8.1. `<if_sid>554</if_sid>`: This tag represents a list of rule IDs.
   - 8.2. `<field>` tag is used as a requisite (condition) to trigger the rule. In this case, the content is the list of all possible PHP file extensions.

9. To test our FIM rule, we will add a new file called `antivirusupdate.php` in `/home/purple`:
   - 9.1. `touch /home/purple/antivirusupdate.php`
   - 9.2. Alert: `[File creation]: Possible web shell scripting file (/home/purple/antivirusupdate.php) created`
     - 9.2.1. `rule.id`: 100500

This FIM rule may lead to a lot of false positive alerts on the Wazuh dashboard. To overcome this situation, you can fine-tune your `<syscheck>` block by adding more `<ignore>` tags.

## Third case: The CDB list

The CDB list is a repository that has distinct hashes or checksums of malicious/benign files. Wazuh makes comparison of any file hash and hashes in CDB list. The CDB list consists of lists of users, file hashes, IP addresses, domain names, and so on.

You can save a list of users, file hashes, IP addresses, and domain names in a text file called a CDB list. A CDB list can have entries added in a key:value pair or a key:only format. Lists in CDBs can function as allow or deny lists. Wazuh processes the CDB list like here:

1. **Hash generation**: Has both good and bad hashes like IP addresses, malware hashes and domain names. A hash is a unique fixed-length value generated based on the CDB list content.
2. **File comparison**: Wazuh computes files hashes during scanning and compares them with that inside CDB list.
3. **Identification**: Wazuh marks file as malicious if its hash found inside CDB list.
4. **Alerts and reactions**: Based on set policies, Wazuh has the ability to trigger alerts or responses upon detection.

Now we are setting the CDB list inside Wazuh server (ubuntu) with malware hashes and create the required rules to trigger alerts if hash match another in CDB comparison process:

1. **Create a file in the CDB list**: CDB lists are stored in (`/var/ossec/etc/lists`) on Wazuh server. Now we will add new CDB list with name `malware-hashes` using this command (`nano /var/ossec/etc/lists/malware-hashes`)

2. **Adding malware hashes**: Now we will enter known malware hashes in format (key:value pair) where key is actual malware hash and value is name or keyword. One of popular sources for malware hashes is a list published by Nextron Systems, download via (https://github.com/Neo23x0/signature-base/blob/master/iocs/hash-iocs.txt). For testing we will use a few popular malware hashes like Mirai and Fanny by putting inside `/var/ossec/etc/lists/malware-hashes` file:
   - 2.1. `e0ec2cd43f71c80d42cd7b0f17802c73:mirai`
   - 2.2. `55142f1d393c5ba7405239f232a6c059:Xbash`
   - 2.3. `F71539FDCA0C3D54D29DC3B6F8C30E0D:fanny`

3. **Adding the CDB list under default ruleset**: Inside the configuration file (`/var/ossec/etc/ossec.conf`) in `<ruleset>` tag we put the path of hashes files, by adding this line inside the tag (`<list>etc/lists/malware-hashes</list>`)

4. **Writing a rule to compare hashes**: Create custom rule in Wazuh server (ubuntu) inside (`/var/ossec/etc/rules/local_rules.xml`) or from the Wazuh dashboard by going to Server management tab then Rules tab then searching for `local_rules.xml` then press edit and add this:

```xml
<group name="malware">
    <rule id="110002" level="13">
        <if_sid>554, 550</if_sid>
        <list field="md5" lookup="match_key">etc/lists/malware-hashes</list>
        <description>
            Known Malware File Hash is detected: $(file)
        </description>
        <mitre>
            <id>T1204.002</id>
        </mitre>
    </rule>
</group>
```

   When Wazuh finds a match between the MD5 hash of a recently created or updated file and a malware hash in the CDB list, this rule triggers. When an event occurs that indicates a newly created or modified file exists, rules 554 and 550 will be triggered.

5. **Restart the manager**: We have to restart the Wazuh manager to apply the changes using (`systemctl restart wazuh-manager`)

We have successfully created a CDB list of malware hashes and security rules to compare it with the hash of each file in the Wazuh agent. Now in our Wazuh agent we will edit configuration file (`/var/ossec/etc/ossec.conf`) to set out agent detect file changes in specified directory like we have put in our configuration of FIM (`<directories whodata="yes" report_changes="yes" check_all="yes">/home/purple/malware-tests</directories>`). We will work on this directory (`/home/purple/malware-tests`) to test our cases, then we will restart Wazuh agent using (`systemctl restart wazuh-agent`):

1. `check_all="yes"`: This ensures that Wazuh verifies every aspect of the file, such as its size, permissions, owner, last modification date, inode, and hash sums.

Now we will test the CDB list we have put:

1. By creating fake malware called (`mal_detection`) in the place that we are monitoring using FIM (`/home/purple/malware-tests`)
2. By putting its hash (`d6bd8791357b59cf584b7f94080f8841`) in (`/var/ossec/etc/lists/malware-hashes`)
3. Restart Wazuh manager (`systemctl restart wazuh-manager`)
4. Going to threat hunting page we will find this alert: (`File with known malware hash detected: /home/purple/malware-tests/mal_detction`)
5. By expanding the alert we find some sections are:
   - 5.1. **rule.description**: `File with known malware hash detected: /home/purple/malware-tests/mal_detction` --> describes the activated rule 110002
   - 5.2. **rule.groups**: `malware` --> describes what is category of activated rule
   - 5.3. **rule.mitre.technique**: `Malicious File` --> describes how this file related to MITRE
   - 5.4. **full_log**: `File '/home/purple/malware-tests/mal_detction' added Mode: realtime`
6. We have detected file by its signature so the test is successful. There are some more use cases of the CDB list such as detecting unknown users and detecting blacklisted IP addresses.

## Fourth case: VirusTotal integration

VirusTotal is a free online service that analyzes files and URLs to detect malware and malicious content. It uses over 70 types of antivirus software and URL blocklisting engines to provide detailed information about the submitted file, URL, or IP address. VirusTotal allows users to contribute their own findings and submit comments on files and URLs. These contributions can help improve the service's accuracy and provide valuable insights to other users. VirusTotal provides an API with multiple paid plans. However, it also has a free plan where you can request four lookups per minute with a daily quota of 500 lookups.

In this use case of malware detection, we will use a FIM module to monitor the changes and then trigger VirusTotal to scan the files in that directory.

1. Set up VirusTotal account to get API key by making account on (https://www.virustotal.com/) by normal sign up operation, then copy API key

2. Now we will integrate VirusTotal with wazuh manager, wazuh has prebuilt integration for VirusTotal in (`/var/ossec/integrations/virustotal`)
   
   2.1. In the file (`/var/ossec/etc/ossec.conf`) we will add this inside `<ossec_config>` tag:
   ```xml
   <integration>
       <name>virustotal</name>
       <api_key><api-key></api_key>
       <rule_id>100200,100201</rule_id>
       <alert_format>json</alert_format>
   </integration>
   ```
   
   2.1.1. `<rule_id>100200,100201</rule_id>`: This represents the rule that triggers the VirusTotal inspection
   
   2.1.2. `<api_key>`: This represents the VirusTotal API key
   
   2.1.3. We have rule ID 100200 and 100201. We haven't created these rules yet; we will write these rules to detect file changes in a specific folder of the endpoint.

3. Now we will create wazuh rules in wazuh manager, we want to trigger VirusTotal when scanning only when file is changed, added, or deleted to avoid tons of false positive alerts (to avoid flagging normal act as malware act), we will create FIM rule with 100200 and 100201 as we have said before in local_rule.xml or from dashboard from rules section, write this:

   ```xml
   <group name="syscheck,pci_dss_11.5,nist_800_53_SI.7">
       
       <!-- Rule: File modified in /home/purple -->
       <rule id="100200" level="7">
           <if_sid>550</if_sid>
           <field name="file">/home/purple</field>
           <description>File modified in /home/purple directory.</description>
       </rule>

       <!-- Rule: File added to /home/purple -->
       <rule id="100201" level="7">
           <if_sid>554</if_sid>
           <field name="file">/home/purple</field>
           <description>File added to /home/purple directory.</description>
       </rule>

   </group>
   ```
   
   3.1. `<if_sid>550</if_sid>`: This specifies a condition that triggers this rule. It's triggered when the event ID (SID) 550 occurs. The Wazuh rule 550 indicates that the integrity checksum changed, metadata has been altered which represents the file is modified.
   
   3.2. `<if_sid>554</if_sid>`: This rule triggers when the event ID 554 occurs. The Wazuh rule indicates that a file has been added to the system.
   
   3.3. Restart wazuh manager (`sudo systemctl restart wazuh-manager`)

4. Now we will setup the FIM in our agent as we have done before we have already added it in previous sections:
   
   4.1. In file (`/var/ossec/etc/ossec.conf`)
   
   4.2. In tag `<syscheck>` we will ensure it is enabled and have the directory we want to monitor in our case is (`/home/purple`):
   ```xml
   <directories whodata="yes" report_changes="yes" check_all="yes">/home/purple</directories>
   ```
   
   4.3. Restart the Wazuh agent using (`sudo systemctl restart wazuh-agent`)

5. Now we will test malware detection, to test malware detection using VirusTotal we will use EICAR (European Institute for Computer Antivirus Research) test file. An EICAR test file is used to test the response of antivirus software and it is built by the European Institute for Computer Antivirus Research and the Computer Antivirus Research Organization (CARO). In other words it is malware dataset to test malware detection mechanism.
   
   5.1. We will use this link to install EICAR test file (https://www.eicar.org/download-anti-malware-testfile/)
   
   5.2. We will then move it to the monitored directory (`/home/purple`)
   
   5.3. Dec 9, 2025 @ 15:31:05.256 : purple : VirusTotal: Alert - /home/purple/eicar.com.txt - 61 engines detected this file : 12 : 87105
   
   5.3.1. This is virustotal alert which has detected the test file, let's expand this alert
   
   5.3.2. data.integration :: virustotal --> says that this alert using VirusTotal integration
   
   5.3.3. data.virustotal.permalink :: (https://www.virustotal.com/gui/file/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f/detection/f-275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f-1765286425) --> This represents the URL of the VirusTotal detection page, inside it we will find more information about the detection process on virustotal how it has been happened.

We have successfully detected an EICAR file using VirusTotal and Wazuh.

## Fifth case: Integrating Windows Defender logs

In this case we will use Windows 10 as our wazuh agent, to test our case on it, its setup is the same as the Linux agents with those steps:

1. Choose Deploy new agent

2. In windows section, we will choose MSI 32/64 bits

3. We will put wazuh manager IP address

4. Then run those two commands inside windows 10:
   
   4.1. `Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.1-1.msi -OutFile $env:tmp\wazuh-agent; msiexec.exe /i $env:tmp\wazuh-agent /q WAZUH_MANAGER='192.168.228.128'`
   
   4.2. `NET START Wazuh`

Windows Defender is an antivirus software module of Microsoft Windows. Windows Defender is the most common free antivirus product for PC users, since 2022 it was 29% of market uses it. By default, Wazuh cannot read the Windows Defender logs. Hence, it is important for us to put extra effort into making it possible. Now we will push windows defender logs into wazuh manager, so it appears in alerts. We will take a look about windows defender, windows defender logs helps the SOC analyst to understand the status of endpoints security and investigate any security incidents, windows defender logs include several pieces of information such as scan activities, threat detection, updates, quarantine, remediation, firewall and network activities, and real-time protection. To view the windows defender logs via those steps:

1. Go to Event Viewer

2. Choose Applications and services logs

3. Choose Microsoft

4. Choose Windows

5. Choose Windows Defender

6. Choose Operational

7. There will be logs

8. Choosing any log it will have two tabs General tab (give summarization info) and Details tab (give detailed info)

Now we will set Wazuh agent to collect the Windows Defender logs. We need to push the Defender logs in the (ossec.conf) file of the Wazuh agent. To collect Windows Defender logs, we have two ways to configure agent:

1. Locally using the ossec.conf agent file located at (C:\Program Files (x86)\ossec-agent\ossec.conf)
2. Globally using Wazuh manager, in large networks (we will use this in our case)
   1. Go to Wazuh dashboard
   2. Go to Agents Management
   3. Select Groups tab
   4. Click on add new group button to create new group called (Windows)
   5. We will go to agents then click on edit groups button and choose (Windows)
   6. Now we will return to Management then Groups tab
   7. Now we will go to Wazuh manager edit agent.conf file which is located in (/var/ossec/etc/shared/Windows/agent.conf) and open it
   8. We will add this code:
      ```xml
      <agent_config>
          <localfile>
              <location>Microsoft-Windows-Windows Defender/Operational</location>
              <log_format>eventchannel</log_format>
          </localfile>
      </agent_config>
      ```
      1. `<localfile>` tag --> define the local log file or file path that the Wazuh agent should monitor.
      2. `<location>` tag --> it is monitoring the Microsoft-Windows-Windows Defender/Operational log location.
      3. `<log_format>` tag --> This tag specifies the format.
   9. We will restart Wazuh manager using (sudo systemctl restart wazuh-manager)
   10. We will restart Wazuh agent which is on windows (NET STOP Wazuh && NET START Wazuh)

Manually going to each Wazuh agent and making the changes in each agent is a cumbersome task. Wazuh helps us with the (agent.conf) file, which pushes the configuration to specific agent groups, in other words for large network of agents it is preferred to configure via Wazuh manager.

Now we will test malware detection, by installing EICAR virus test file but first we need to do two things:

1. Disable security option inside Microsoft Edge
   1. Go to settings 
   2. Search for security in search bar
   3. Disable this option (Protect from harmful sites and downloads)
2. Disable Real time protection
   1. Search for Windows Security
   2. Choose Virus & Threat protection
   3. Search for Virus & Threat protection settings
   4. Click on manage settings
   5. Disable real time protection
   6. After installing EICAR we will enable real time protection again

After installing EICAR virus test file we will find that Windows Defender detect this file successfully and the alert has been appeared in Wazuh dashboard as following:

`Windows-10 :: Windows Defender: Antimalware platform detected potentially unwanted software () :: 12 :: 62123`

1. data.win.eventdata.threat Name --> Virus:DOS/EICAR_Test_File --> our test file
2. data.win.system.channel --> Microsoft-Windows-Windows Defender/Operational --> This indicates the channel or source where the alert originated
3. rule.description --> Windows Defender: Antimalware platform detected potentially unwanted software () description of the triggered rule
4. rule.groups --> windows, windows_defender --> specifies the groups or categories to which the rule or alert belongs
5. data.win.system.providerName --> Microsoft-Windows-Windows Defender --> This represents the name of the product that generated the alert

## Sixth case: Integrating Sysmon to detect fileless malware on Windows machine 

One of malware types is called fileless malware which operates directly within a computer's memory rather than the hard drive. Fileless means no file has been downloaded on hard drive when machine is infected. This makes it more difficult to detect using traditional antivirus or anti-malware tools, which primarily scan disk files.

Sysmon is a device driver and Windows system service that provides advanced monitoring and logging capabilities. It was created by Microsoft's Sysinternals team to monitor various aspects of system activity, such as processes, network connections, and file changes. While Sysmon does not specifically focus on detecting fileless malware, its comprehensive monitoring capabilities can undoubtedly assist in identifying and mitigating the impact of fileless malware attacks. To enhance Wazuh detection we will install Sysmon in Windows 10 machine. To test the fileless attack detection, we will use the APTSimulator tool to simulate the attack and visualize them on the Wazuh manager. In the next sections we will learn how to detect fileless malware using Sysmon and finally, we will visualize them on the Wazuh dashboard.

Fileless malware attack is fairly unique. Understanding how it works can help an organization protect against future fileless malware attacks. Fileless malware is a type of malicious activity that uses native, legitimate tools built into a system to execute a cyberattack. Unlike traditional malware, which typically requires a file to be downloaded and installed, fileless malware operates in memory or manipulates native tools, making it harder to detect and remove. The exploitation of legitimate tools is often referred to as living off the land (LOTL). There are 4 stages involved in fileless malware attack:

1. **Stage 1 - Gain Access**  
   Threat actors (Attackers) must first gain access to the target machine in order to carry out an attack:
   - Techniques: Remotely exploit a vulnerability and use web scripting for remote access (China Chopper) or SE using phishing emails.
   - Tools: ProLock and Bumblebee

2. **Stage 2 – Steal credentials**  
   Using the access gained in the previous step, the attacker now attempts to obtain credentials for the environment he has compromised which will allow him to easily move to other systems in that environment:
   - Techniques: Remotely exploit a vulnerability and gain remote access via web scripting (Mimikatz)
   - Tools: Mimikatz and Kessel

3. **Stage 3 – Maintain persistence**  
   Now, the attacker creates a backdoor that will allow him to return to this environment at any time without having to repeat the initial steps of the attack:
   - Techniques: Modify the registry to create a backdoor
   - Tools: Sticky Keys Bypass, Chinoxy, HALFBAKED, HiKit, and ShimRat

4. **Stage 4 – Exfiltrate data**  
   In the final step, the attacker collects the data he desires and prepares it for exfiltration by copying it to a single location and then compressing it with commonly available system tools such as Compact. The attacker then uploads the data via FTP to remove it from the victim's environment:
   - Techniques: Using DNS tunneling, traffic normalization, use of an encrypted channel
   - Tools: FTP, SoreFang, and SPACESHIP

Now we will test fileless attack, we need to setup Sysmon package on Windows 10. Sysmon offers comprehensive data about process creation, network connections, and file creation time changes. Sysmon generates events and stores them in Applications and Services (Logs/Microsoft/Windows/Sysmon/Operational), now we will install Sysmon:

1. Visit official website (https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) then click on download Sysmon

2. Extract Sysmon archive file that we have downloaded

3. Now we need to download SwiftOnSecurity Sysmon configuration (well-known and simple configuration file created by popular security professionals) we will use it to enhance our windows monitoring capabilities, using (https://github.com/SwiftOnSecurity/sysmon-config) and download sysmonconfig-export.xml file

4. Put the SwiftOnSecurity file and extracted Sysmon folder in same folder

5. Now we will install Sysmon using the SwiftOnSecurity:

   1. Open cmd or PowerShell with admin privileges
   
   2. Navigate the folder of the Sysmon folder and SwiftOnSecurity file
   
   3. Run this command `sysmon.exe -accepteula -i sysmonconfig-export.xml`
   
      * `-accepteula`: It represents the end user license agreement (EULA) for Sysmon. By including this flag, you are acknowledging and agreeing to the terms of use.
   
   4. Now it has been installed and started successfully to verify:
   
      1. Open Event Viewer
      
      2. Choose Applications and services
      
      3. Choose Microsoft
      
      4. Choose Windows
      
      5. Choose Sysmon
      
      6. Choose Operational --> here Sysmon-related events
      
      7. We see 5 headers:
      
         * **Level** --> This refers to the severity of an event
         
           * 0: Information
           * 1: Warning
           * 2: Error
           * 3: Critical
         
         * **Date and Time** --> time of this event alerted
         
         * **Source** --> it indicates the software or component that generated the event. In this case, it is Sysmon
         
         * **Event ID** --> It is a unique value assigned to each type of event
         
           * Event ID 1: Process creation
           * Event ID 2: File creation
           * Event ID 3: Network connection
           * Event ID 7: Image loaded
           * Event ID 10: Process access
           * Event ID 11: File creation
           * Event ID 12: Registry event (object create and delete)
           * Event ID 13: Registry event (value set)
           * Event ID 14: Registry event (key and value rename)
           * Event ID 15: File creation stream hash
           * Event ID 17: Pipe event (pipe created)
           * Event ID 18: Pipe event (pipe connected)
           * Event ID 22: DNS request
         
         * **Task Category** --> provides the classification for the events. It is the name of the event IDs as listed earlier.

6. Now we will configure wazuh agent to monitor Sysmon events

7. We will include the following block inside ossec.conf of wazuh agent:

   ```xml
   <localfile>
       <location>Microsoft-Windows-Sysmon/Operational</location>
       <log_format>eventchannel</log_format>
   </localfile>
   ```

8. Now we will configure the wazuh manager. We are required to create a custom rule in the Wazuh manager to match the Sysmon events generated by the Windows machine. This rule will ensure that the Wazuh manager triggers an alert every time it gets a Sysmon-related event:

   1. Open wazuh dashboard
   
   2. Choose Rules
   
   3. Choose Manage Rules
   
   4. Choose add new rules file and put name `custom_sysmon.xml` and put this:

      ```xml
      <!-- Log Sysmon Alerts -->
      <group name="sysmon">

          <rule id="101100" level="5">
              <if_sid>61650</if_sid>
              <description>Sysmon - Event 22: DNS Query.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101101" level="5">
              <if_sid>61603</if_sid>
              <description>Sysmon - Event 1: Process creation.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101102" level="5">
              <if_sid>61604</if_sid>
              <description>Sysmon - Event 2: Process changed file creation time.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101103" level="5">
              <if_sid>61605</if_sid>
              <description>Sysmon - Event 3: Network connection.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101104" level="5">
              <if_sid>61606</if_sid>
              <description>Sysmon - Event 4: Sysmon service state changed.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101105" level="5">
              <if_sid>61607</if_sid>
              <description>Sysmon - Event 5: Process terminated.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101106" level="5">
              <if_sid>61608</if_sid>
              <description>Sysmon - Event 6: Driver loaded.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101107" level="5">
              <if_sid>61609</if_sid>
              <description>Sysmon - Event 7: Image loaded.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101108" level="5">
              <if_sid>61610</if_sid>
              <description>Sysmon - Event 8: CreateRemoteThread.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101109" level="5">
              <if_sid>61611</if_sid>
              <description>Sysmon - Event 9: RawAccessRead.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101110" level="5">
              <if_sid>61612</if_sid>
              <description>Sysmon - Event 10: ProcessAccess.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101111" level="5">
              <if_sid>61613</if_sid>
              <description>Sysmon - Event 11: FileCreate.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101112" level="5">
              <if_sid>61614</if_sid>
              <description>Sysmon - Event 12: Registry create/delete.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101113" level="5">
              <if_sid>61615</if_sid>
              <description>Sysmon - Event 13: Registry value set.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101114" level="5">
              <if_sid>61616</if_sid>
              <description>Sysmon - Event 14: Registry rename.</description>
              <options>no_full_log</options>
          </rule>

          <rule id="101115" level="5">
              <if_sid>61617</if_sid>
              <description>Sysmon - Event 15: FileCreateStreamHash.</description>
              <options>no_full_log</options>
          </rule>
      

### 8.4. Key XML Elements

1. **`<group>`**: This tag is used to organize rules and helps in managing and categorizing rules based on their functionality.

2. **`<rule>`**: This defines the individual rule with the `id` and `level` attributes.

3. **`<if_sid>`**: This tag is used as a requisite to trigger any rule when a rule ID has previously matched.

### 8.5. Restart Wazuh Manager

Restart Wazuh manager using this command:
```bash
sudo systemctl restart wazuh-manager
```

## 9. Testing with APTSimulator

Now we will use APTSimulator to test the fileless attack. APTSimulator is a Windows batch script that employs several tools and output files to make a system appear to be compromised. We need to disable security option inside Microsoft Edge and disable Real-time protection as we have made before.

### 9.1. Installation Steps

1. Install APTSimulator in Windows 10 agent via: https://github.com/NextronSystems/APTSimulator

2. Extract the folder of APTSimulator

3. Run `APTSimulator.bat`

4. It will give us a table with the attacks

5. Enter `0` to test all attacks. This will run every test including Collection, Command and Control, Credential Access, Defense Evasion, Discovery, Execution, Lateral Movement, Persistence, and Privilege Escalation.

### 9.6. Alert Analysis

One of the alerts: `Windows-10 :: Sysmon - Event 22: DNS Query. :: 5 :: 101100`

- **`data.win.system.channel`** → `Microsoft-Windows-Sysmon/Operational` → This indicates the channel or source where the alert originated

- **`data.win.system.eventID`** → `22` → ID of Event of DNS Query

- **`rule.groups`** → `Sysmon` → Categories to which the rule or alert belongs

## Conclusion

This lab introduced us to the synergy between Wazuh and malware detection, covering its capabilities in FIM and using VirusTotal for enhanced threat intelligence and the CDB list to build a list of known malware hashes. The integration of Windows Defender logs with Wazuh provided us with a unified look at security events on a Windows machine. In the end, we talked about the integration of Sysmon with a Windows machine to detect fileless malware on the Windows machine.
