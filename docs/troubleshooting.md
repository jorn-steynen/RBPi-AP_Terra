# 📚 Troubleshooting Guide

This document helps you diagnose and resolve issues in the RBPi-AP_Terra project.

---

## 🛠️ General Debug Tips

- Use `journalctl -u <service>` to view service logs
- Use `tail -f /mnt/ssd/logs/watchdog.log` to monitor system health
- Use `df -h` or `mount` to verify the SSD mount
- All logs are saved on the SSD to preserve SD card lifespan

---

## ⚠️🔌 SSD Mounting: CRITICAL FOR SYSTEM FUNCTIONALITY

All scripts and services in this project rely on the SSD being correctly mounted at:

```
/mnt/ssd
```

If the SSD is **not mounted**, nothing will work:
- ❌ Logging will fail (`Input/output error`)
- ❌ Services will restart endlessly
- ❌ Watchdog will report missing status files

---

### ✅ Check if it's mounted:
```bash
mount | grep /mnt/ssd
```

Should return:
```
/dev/sda1 on /mnt/ssd type ext4 ...
```

---

### 🛠 Auto-mount with `/etc/fstab`

Ensure this line is in `/etc/fstab`:

```fstab
UUID=7abe1ab6-fec7-4970-bd78-ec4fa478ab4b  /mnt/ssd  ext4  defaults,nofail,x-systemd.device-timeout=10  0  2
```

Replace the UUID with yours:
```bash
sudo blkid
```

Then:
```bash
sudo systemctl daemon-reexec
sudo mount -a
```

---

### 🔄 Replacing the SSD or USB device?

1. Plug in the new device
2. Find its UUID:
   ```bash
   sudo blkid
   ```
3. Replace the old UUID in `/etc/fstab`
4. Reload systemd and remount:
   ```bash
   sudo systemctl daemon-reexec
   sudo mount -a
   ```

---

## 🐛 Common Service Failures

### `mppt-mqtt.service` or `dht11-mqtt.service` fails?

- Check `/mnt/ssd/status/` exists and is writable
- Watch for logs in:
  ```bash
  tail -f /mnt/ssd/logs/mppt.log
  tail -f /mnt/ssd/logs/dht11.log
  ```

### `watchdog_checker.py` reports errors?

- Look in `/mnt/ssd/logs/watchdog.log`
- Check that all status files are updated by their respective services
- If the SSD is not mounted, **nothing works**

---

## 🧪 Verifying system health

- Confirm all services are active:
  ```bash
  systemctl list-units --type=service --state=running | grep mqtt
  ```
- Check `/mnt/ssd/status/*.status` files are updating every few seconds/minutes
- Use Grafana dashboards to validate live data

---
