# MikroTik LTE Router Configuration (AP Terra Project)

This folder contains a sample MikroTik configuration export (`mikrotik_lte_export.rsc`) for the **MikroTik wAP LTE Kit** used in the AP Terra project. The configuration enables **remote access, local WiFi, DHCP, SNMP monitoring**, and is intended for deployment in rural field sites using solar-powered Raspberry Pi systems.

---

## ⚠️ Important Notes Before Use

This is a **template**. Before importing, always **customize or verify**:

- **LTE APN settings** — leave as-is until you know the SIM provider in Uganda  
- **Time zone** — this template sets it to `Africa/Kasese`
- **WireGuard VPN peer IP** — two options are provided below
- **SNMP community strings** — set a unique read-only community if needed
- **Router password** — replace defaults and secure your access
- ❌ Never commit passwords, keys, or secrets to version control

---

## 🌍 Field Deployment: Two Router Options

| Router | Device Model             | WireGuard VPN IP | Description              |
|--------|--------------------------|------------------|--------------------------|
| 1      | MikroTik wAP LTE Kit 1   | `10.8.0.11`      | Main AP Terra deployment |
| 2      | MikroTik wAP LTE Kit 2   | `10.8.0.14`      | Secondary deployment     |

Make sure to use the correct config for each router. You can either adjust the `.rsc` file manually before import or duplicate this README and config for each unit.

---

## ✅ What This Config Sets Up (Verified)

- **Local WiFi Access Point**
  - SSID: `wAP-local` (2.4 GHz)
  - WPA2-PSK security (`bletchley` profile)
  - Used to connect Raspberry Pi or debug in the field

- **Wired & Wireless LAN**
  - Bridge includes `ether1`, `ether2`, and `wlan1`
  - LAN subnet: `192.168.100.0/24`
  - Static DHCP leases for Pi, camera, and laptop

- **WireGuard VPN Tunnel**
  - Peer: `wgeasy.iot-ap.be:51820`
  - IP address set to either `10.8.0.11` or `10.8.0.14`
  - Full routing between VPN and LAN

- **SNMP Monitoring**
  - SNMP enabled for local reads (`192.168.100.0/24`)
  - Use this to poll LTE metrics remotely via VPN

- **Firewall & NAT**
  - Secure input rules for VPN and SNMP
  - NAT (masquerade) for LTE and VPN
  - Blocks unused services like Telnet, FTP, API

- **DNS & DHCP**
  - Local DNS: `192.168.100.1`, `1.1.1.1`
  - DHCP server for local devices

- **Time Zone**
  - Set to `Africa/Kasese`

---

## 🧭 Setup Instructions

### A. If VPN Is Already Working

1. SSH into the router via VPN:
   ```bash
   ssh admin@10.8.0.11    # or ssh admin@10.8.0.14

2. Upload the config file:

   ```bash
   scp configs/mikrotik_lte_export.rsc admin@10.8.0.11:/
   ```

3. Apply the config:

   ```bash
   /import mikrotik_lte_export.rsc
   ```

---

### B. If the Router Is New or Factory Reset

1. Download [Winbox](https://mikrotik.com/download)
2. Connect your PC to the router via Ethernet
3. Open Winbox and log in (default: `admin` with no password)
4. Set a new password via **System → Users**
5. Upload and import the config:

   * Go to **Files**, upload the `.rsc` file
   * Open Terminal and run:

     ```bash
     /import mikrotik_lte_export.rsc
     ```

---

## 🛠️ To-Do After Import

* [ ] Update the LTE APN based on local SIM provider
* [ ] Confirm VPN connectivity from remote (ping `10.8.0.11` or `.14`)
* [ ] Test SNMP access from Pi or VPN server
* [ ] Verify WiFi signal and SSID broadcast
* [ ] Check DHCP leases and connectivity to camera / Pi
* [ ] Secure all credentials

---

## 🧾 Reference: VPN Setup ([from guidebook](../docs/guidebook.md))

Each device connects to a WireGuard VPN server. Example configuration:

```ini
[Interface]
PrivateKey = <REDACTED>
Address = 10.8.0.11/24  # Or 10.8.0.14/24 for second router

[Peer]
PublicKey = f5jC2dSqTYDpyWRuD+BgbbP8yYnt7JJ7MILZ6N3yxmI=
PresharedKey = <REDACTED>
AllowedIPs = 10.8.0.0/24
PersistentKeepalive = 25
Endpoint = wgeasy.iot-ap.be:51820
```
