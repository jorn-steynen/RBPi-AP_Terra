### 🛠 Troubleshooting – System Monitoring & Logs

All logs are saved to the **external SSD** at:

```bash
/mnt/ssd/logs/
```

> ⚠️ **Important:** If you can’t access logs, always verify that the SSD is properly mounted:
```bash
mount | grep /mnt/ssd
```
If it’s not mounted, try:
```bash
sudo mount -a
```

---

#### 🔍 Check the watchdog

The watchdog monitors the health of all core scripts and logs issues here:

```bash
tail /mnt/ssd/logs/watchdog.log
```

This log reports:
- Missing or stale `.status` files
- Reported `ERROR` states from scripts
- Timestamps and context for diagnosis

To monitor live:
```bash
tail -f /mnt/ssd/logs/watchdog.log
```

---

#### 🔎 Check individual component logs

Each major script has its own log file in `/mnt/ssd/logs/`:

```bash
tail /mnt/ssd/logs/mppt.log
tail /mnt/ssd/logs/dht11.log
tail /mnt/ssd/logs/router.log
tail /mnt/ssd/logs/video_capture.log
```

These contain MQTT messages, sensor data, camera feedback, and errors.

---

#### 🧹 Logs are automatically rotated

- Rotation occurs daily or when a log exceeds 100KB
- Logs are compressed (`.gz`) and kept for 14 days
- Old logs are cleaned automatically
- Managed by `logrotate` (config: `/etc/logrotate.d/uganda_logs`)

---

#### 🧠 Useful commands

Quickly spot the latest issue:
```bash
grep "WARNING" /mnt/ssd/logs/watchdog.log | tail
```

Check script heartbeat/status:
```bash
cat /mnt/ssd/status/*.status
```

