# Simple Layer 4 DoS Tool 

> ⚠️ For **educational** and **testing purposes** only. Do NOT use this tool for illegal activities.  

---

## Overview

This is a powerful and customizable **Layer 4 DoS testing tool** built with Python and it supports a variety of attack modes such as:

- TCP SYN Flood
- UDP Flood
- ICMP Flood
- DNS Flood 
- Randomized packet injection with spoofing
- Multi-threaded and multi-processed firepower

---

## 🛠️ Requirements

- Python 3.8+
- Root/admin privileges (for raw socket usage)
- Linux/macOS (Windows limited support for raw sockets)

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
python3 scrape.py (for scraping proxies)
python3 nuke.py <mode> <ip> <port> <duration> <proxy_list>(optional)
