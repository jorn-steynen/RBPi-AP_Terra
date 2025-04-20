# MikroTik LTE Router Configuration (Template)

This folder contains a sample MikroTik configuration export for the LTE router used in the AP Terra project. It is meant to be imported on the router to enable SNMP, LTE monitoring, and remote access capabilities.

## ⚠️ Warning
This is a **template**. Be sure to review and customize the following before importing:
- **APN and LTE interface settings**
- **SNMP community strings and access settings**
- **VPN or firewall rules**
- **User credentials or passwords**

Never commit actual passwords, keys, or sensitive credentials to version control.

---

## 📥 How to import
1. Ensure you are connected to the router via VPN (WireGuard).
2. Open a terminal and SSH into the router:
```bash
ssh admin@10.8.0.11
```
3. Upload the config file using SCP from your local machine:
```bash
scp configs/mikrotik_lte_export.rsc admin@10.8.0.11:/
```
(This assumes you're in the root of your project repository and have the config file in the `configs/` folder.)

4. Once connected via SSH, run:
```bash
/import mikrotik_lte_export.rsc
```
This will apply the configuration stored in the file.

---

## 🔧 What this config sets up (template features)
- Basic SNMP setup for LTE metrics
- System identity and comments for field identification
- Optionally, WireGuard or firewall rules (if needed)

---
