## What you need

* A laptop with **WinBox** installed ([download](https://mikrotik.com/download))
* A MikroTik **wAP LTE** (fully reset, without default configuration)
* A **SIM card** inserted into the wAP LTE, you can disable the PIN beforehand
* Your **APN info** (provider-specific)
* A **PoE injector or power supply** to power the wAP LTE

---

## Step-by-step setup via WinBox

**Make sure the router is fully reset before starting (no default config).**

### 1. **Connect to the Router**

* Plug in the router (via PoE or DC jack)
* Open **WinBox** on your computer
* Go to the **“Neighbors”** tab
* Connect via **MAC address** (IP doesn’t work yet)

  * Username: `admin`
  * Password: *(leave blank)*

---

### 2. **Set a system identity and password**

This step will make recognizing which device it is easier.

* Go to **System → Identity**

  * Set name to e.g. `wap-uganda`
    
* Go to **System → Users**

  * Double-click `admin` → Set **new password**

---

### 3. **Create a LAN bridge**

* Go to **Bridge**

  * Add new bridge → Set name to e.g. `bridge1`
   
* Go to **Bridge → Ports**

  * Add `ether1` and `wlan1` to `bridge1`

---

### 4. **Assign LAN IP**

* Go to **IP → Addresses**

  * Add:

    * Address: `192.168.88.1/24`
    * Interface: `bridge1`

---

### 5. **Set up DHCP Server**

* Go to **IP → DHCP Server**

  * Click **DHCP Setup**

    * Interface: `bridge1`
    * Default range is fine (`192.168.88.100-199`), or whatever your network requirements are
* Confirm **DNS: 192.168.88.1**
* Confirm **Gateway: 192.168.88.1**

---

### 6. **Set LTE APN**

* Go to **Interfaces → LTE → LTE APNs**

  * Add:

    * Name: `myapn`
    * APN: *(from your provider)*
    
* Back to **Interfaces → LTE**

  * Double-click `lte1`

    * Set **APN Profile** to `myapn`
    * Set **Network Mode** to `LTE only` or `auto`

---

### 7. **Set default route + DNS**

* Go to **IP → Routes**

  * Make sure there’s a default route (`0.0.0.0/0`) via `lte1`
    
* Go to **IP → DNS**

  * Set DNS servers: `8.8.8.8`, `1.1.1.1`
  * Check **“Allow Remote Requests”** if using as DNS server for LAN

---

### 8. **Set NAT**

* Go to **IP → Firewall → NAT**

  * Add rule:

    * Chain: `srcnat`
    * Out Interface: `lte1`
    * Action: `masquerade`

---

### 9. **Test internet**

* WinBox → **New Terminal**
  Run:

  ping 8.8.8.8
  ping google.com
