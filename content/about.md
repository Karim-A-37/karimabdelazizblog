---
title: "About Me"
date: 2026-05-01
layout: "page"
---

<style>
/* ── Social icons ─────────────────────────────── */
.socials { display:flex; flex-wrap:wrap; gap:1rem; margin:1.5rem 0; }
.socials a {
  display:inline-flex; align-items:center; gap:0.55rem;
  padding:0.55rem 1.1rem; border-radius:8px;
  border:1.5px solid var(--primary);
  color:var(--primary); text-decoration:none;
  font-size:0.88rem; font-weight:600;
  transition:background 0.2s,color 0.2s;
}
.socials a:hover { background:var(--primary); color:var(--theme); }
.socials svg { width:18px; height:18px; fill:currentColor; flex-shrink:0; }

/* ── Timeline ─────────────────────────────────── */
.timeline { position:relative; padding-left:1.6rem; margin:1.5rem 0; }
.timeline::before {
  content:''; position:absolute; left:0; top:6px;
  width:2px; bottom:0; background:var(--primary); opacity:0.25;
}
.tl-item { position:relative; margin-bottom:2rem; }
.tl-item::before {
  content:''; position:absolute; left:-1.6rem; top:5px;
  width:10px; height:10px; border-radius:50%;
  background:var(--primary); border:2px solid var(--theme);
}
.tl-date {
  font-size:0.78rem; font-weight:600; letter-spacing:0.04em;
  opacity:0.55; margin-bottom:0.25rem; text-transform:uppercase;
}
.tl-title { font-size:1rem; font-weight:700; margin:0 0 0.1rem; }
.tl-org { font-size:0.88rem; opacity:0.65; margin-bottom:0.5rem; }
.tl-item ul { margin:0; padding-left:1.2rem; }
.tl-item li { font-size:0.9rem; margin-bottom:0.2rem; opacity:0.85; }

/* ── Skills table ─────────────────────────────── */
.skills-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:1.5rem 0; }
@media(max-width:600px){ .skills-grid { grid-template-columns:1fr; } }
.skill-card {
  border:1px solid var(--border); border-radius:10px;
  padding:1rem 1.2rem;
}
.skill-card h4 { margin:0 0 0.5rem; font-size:0.88rem; opacity:0.6; text-transform:uppercase; letter-spacing:0.05em; }
.skill-tags { display:flex; flex-wrap:wrap; gap:0.4rem; }
.skill-tag {
  font-size:0.78rem; padding:0.2rem 0.55rem; border-radius:20px;
  border:1px solid var(--primary); opacity:0.85;
}
</style>

<div style="text-align:center;padding:1.5rem 0 0.5rem">
  <h1 style="font-size:2rem;margin-bottom:0.2rem">Karim Abdelaziz</h1>
  <p style="opacity:0.6;margin:0">Cybersecurity Student &nbsp;·&nbsp; Penetration Testing &nbsp;·&nbsp; Red Team Aspirant</p>
  <p style="opacity:0.5;font-size:0.9rem;margin-top:0.3rem">📍 Alexandria, Egypt &nbsp;·&nbsp; karemabdelaziz082@gmail.com</p>
</div>

---

Final-year **B.Sc. Cybersecurity** student (GPA 3.8 / 4.0, graduating Jun 2026) with a focus on offensive security. I learn by doing — CTFs, SIEM labs, network internships, and pentesting tracks are how I build real skills. Currently pursuing the **eJPT** certification while finishing my graduation project on **Wazuh SIEM/XDR**.

---

## Find Me Online

<div class="socials">

<a href="https://github.com/Karim-A-37" target="_blank">
<svg viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
GitHub
</a>

<a href="https://linkedin.com/in/karim-abdelaziz-359b63360" target="_blank">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
LinkedIn
</a>

<a href="https://profile.hackthebox.com/profile/019daf59-087e-71ba-9ae1-58ab43a8a4c8" target="_blank">
<svg viewBox="0 0 24 24"><path d="M12 0L2 6.5v11L12 24l10-6.5v-11L12 0zm0 2.3l7.7 5v9.4L12 21.7l-7.7-5V7.3L12 2.3zm0 3.5L6 9.5v5l6 3.5 6-3.5v-5L12 5.8zm0 2.3l3.7 2.2v3.4L12 16l-3.7-2.3V10.3L12 8.1z"/></svg>
HackTheBox
</a>

<a href="https://tryhackme.com/p/JaGuar" target="_blank">
<svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 2.18l7 3.12v5.7c0 4.35-3.01 8.43-7 9.7-3.99-1.27-7-5.35-7-9.7V6.3l7-3.12z"/></svg>
TryHackMe
</a>

<a href="https://codeforces.com/profile/2_f4ces" target="_blank">
<svg viewBox="0 0 24 24"><path d="M4.5 7.5A1.5 1.5 0 0 1 6 9v10.5A1.5 1.5 0 0 1 4.5 21h-3A1.5 1.5 0 0 1 0 19.5V9A1.5 1.5 0 0 1 1.5 7.5h3zm9-4.5A1.5 1.5 0 0 1 15 4.5v15A1.5 1.5 0 0 1 13.5 21h-3A1.5 1.5 0 0 1 9 19.5v-15A1.5 1.5 0 0 1 10.5 3h3zm9 7.5A1.5 1.5 0 0 1 24 12v7.5A1.5 1.5 0 0 1 22.5 21h-3A1.5 1.5 0 0 1 18 19.5V12A1.5 1.5 0 0 1 19.5 10.5h3z"/></svg>
Codeforces
</a>

<a href="https://leetcode.com/u/Karim_A_1117/" target="_blank">
<svg viewBox="0 0 24 24"><path d="M13.483 0a1.374 1.374 0 0 0-.961.438L7.116 6.226l-3.854 4.126a5.266 5.266 0 0 0-1.209 2.104 5.35 5.35 0 0 0-.125.513 5.527 5.527 0 0 0 .062 2.362 5.83 5.83 0 0 0 .349 1.017 5.938 5.938 0 0 0 1.271 1.818l4.277 4.193.039.038c2.248 2.165 5.852 2.133 8.063-.074l2.396-2.392c.54-.54.54-1.414.003-1.955a1.378 1.378 0 0 0-1.951-.003l-2.396 2.392a3.021 3.021 0 0 1-4.205.038l-.02-.019-4.276-4.193c-.652-.64-.972-1.469-.948-2.263a2.68 2.68 0 0 1 .066-.523 2.545 2.545 0 0 1 .619-1.164L9.13 8.114c1.058-1.134 3.204-1.27 4.43-.278l3.501 2.831c.593.48 1.461.387 1.94-.207a1.384 1.384 0 0 0-.207-1.943l-3.5-2.831c-.8-.647-1.766-1.045-2.774-1.202l2.015-2.158A1.384 1.384 0 0 0 13.483 0zm-2.866 12.815a1.38 1.38 0 0 0-1.38 1.382 1.38 1.38 0 0 0 1.38 1.382H20.79a1.38 1.38 0 0 0 1.38-1.382 1.38 1.38 0 0 0-1.38-1.382z"/></svg>
LeetCode
</a>

</div>

---

## Education

**B.Sc. Computer and Data Science — Cybersecurity Major**
Alexandria National University · Alexandria, Egypt · `Oct 2022 – Jun 2026`
GPA **3.8 / 4.0** · Courses: Network Security · InfoSec Management · Blockchain & Data Integrity · DB Systems

---

## Experience

<div class="timeline">

<div class="tl-item">
<div class="tl-date">Oct 2025 – Jan 2026</div>
<div class="tl-title">Network Intern</div>
<div class="tl-org">NTI — National Telecommunication Institute · Remote</div>
<ul>
<li>Earned Cisco CCNA credential (Credly verified); 54 hands-on labs using Cisco hardware & Packet Tracer</li>
<li>Configured switches, routers, end devices; applied IP addressing & data-link layer protocols</li>
</ul>
</div>

<div class="tl-item">
<div class="tl-date">Jun 2025 – Sep 2025</div>
<div class="tl-title">Quantum Computing Intern</div>
<div class="tl-org">Alamein International University (AIU) · Remote</div>
<ul>
<li>12-week programme: 50 h of lectures + labs covering quantum gates, circuits, and algorithms</li>
<li>Delivered a final project applying quantum computing concepts</li>
</ul>
</div>

<div class="tl-item">
<div class="tl-date">Jul 2024 – Sep 2024</div>
<div class="tl-title">Linux System Administration L1 & L2</div>
<div class="tl-org">Information Technology Institute (ITI) · Alexandria, Egypt</div>
<ul>
<li>Administered RHEL systems: users, groups, services, networking, Bash automation</li>
<li>Applied SELinux policies, firewall rules, and access control hardening</li>
</ul>
</div>

<div class="tl-item">
<div class="tl-date">Jan 2024 – May 2024</div>
<div class="tl-title">Front-End Web Developer Training</div>
<div class="tl-org">SEF Academy · Remote</div>
<ul>
<li>Built responsive web apps with HTML5, CSS3, JavaScript; introductory Node.js & SQL</li>
</ul>
</div>

</div>

---

## Projects

<div class="timeline">

<div class="tl-item">
<div class="tl-date">2025 – 2026 · Graduation Project</div>
<div class="tl-title">Wazuh SIEM/XDR</div>
<div class="tl-org">Alexandria National University · <a href="https://github.com/Karim-A-37/Wazuh" target="_blank">github.com/Karim-A-37/Wazuh</a></div>
<ul>
<li>Deployed Wazuh across a multi-agent lab simulating an enterprise network</li>
<li>Designed detection rules for brute force, privilege escalation & lateral movement</li>
<li>Performed log ingestion, correlation, IOC analysis; documented findings on GitHub</li>
</ul>
</div>

<div class="tl-item">
<div class="tl-date">2026 – Present</div>
<div class="tl-title">INE Penetration Testing Lab Track</div>
<div class="tl-org">INE Security · TryHackMe · HackTheBox · Personal Labs</div>
<ul>
<li>Practising recon, scanning, exploitation & post-exploitation aligned with eJPT curriculum</li>
<li>Solving CTF challenges to build a practical offensive skill set</li>
</ul>
</div>

</div>

---

## Technical Skills

<div class="skills-grid">
<div class="skill-card">
<h4>Offensive Security</h4>
<div class="skill-tags">
<span class="skill-tag">Penetration Testing</span><span class="skill-tag">Nmap</span><span class="skill-tag">Metasploit</span><span class="skill-tag">Web App Testing</span><span class="skill-tag">Vuln Assessment</span>
</div>
</div>
<div class="skill-card">
<h4>Defensive Security</h4>
<div class="skill-tags">
<span class="skill-tag">Wazuh SIEM/XDR</span><span class="skill-tag">Threat Detection</span><span class="skill-tag">Incident Response</span><span class="skill-tag">Log Analysis</span><span class="skill-tag">IOC Analysis</span>
</div>
</div>
<div class="skill-card">
<h4>OS & Networking</h4>
<div class="skill-tags">
<span class="skill-tag">RHEL</span><span class="skill-tag">Ubuntu</span><span class="skill-tag">Bash</span><span class="skill-tag">SELinux</span><span class="skill-tag">TCP/IP</span><span class="skill-tag">Cisco CLI</span><span class="skill-tag">Wireshark</span>
</div>
</div>
<div class="skill-card">
<h4>Programming</h4>
<div class="skill-tags">
<span class="skill-tag">Python</span><span class="skill-tag">SQL</span><span class="skill-tag">JavaScript</span><span class="skill-tag">HTML5</span><span class="skill-tag">CSS3</span><span class="skill-tag">Git</span>
</div>
</div>
</div>

---

## Certifications

| Status | Certification |
|---|---|
| ✅ Earned | CCNA: Introduction to Networks — Cisco / NTI *(Jan 2026, Credly Verified)* |
| ✅ Earned | Quantum Computing Certificate — Alamein International University *(Sep 2025)* |
| 🔄 In Progress | eJPT — Junior Penetration Tester — INE Security *(2026)* |

---

## 📄 Curriculum Vitae

<div style="margin:1rem 0">
<a href="/files/karim-cv.pdf" target="_blank"
   style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.1rem;border-radius:8px;border:1.5px solid var(--primary);color:var(--primary);text-decoration:none;font-weight:600;font-size:0.9rem;transition:background 0.2s,color 0.2s"
   onmouseover="this.style.background='var(--primary)';this.style.color='var(--theme)'"
   onmouseout="this.style.background='';this.style.color='var(--primary)'">
  ⬇ Download CV (PDF)
</a>
</div>

<div style="width:100%;height:880px;border:1px solid var(--border);border-radius:10px;overflow:hidden">
  <iframe src="/files/karim-cv.pdf" style="width:100%;height:100%;border:none" title="Karim Abdelaziz CV"></iframe>
</div>
