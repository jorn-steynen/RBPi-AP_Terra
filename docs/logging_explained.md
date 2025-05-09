## 1️⃣ How it works – explanation

**What does the system do exactly?**

### Log files and location

All system logs (such as `video_capture.log`, `watchdog.log`, `mppt.log`, etc.) are stored in:

```
/mnt/ssd/logs/
```

This keeps log files off the Raspberry Pi's SD card, which is important to prevent SD card wear and ensure enough storage space.

### Log rotation

To prevent log files from growing too large and filling up the SSD, automatic log rotation is configured using the following file:

```
/etc/logrotate.d/uganda_logs
```

This setup ensures that **all `.log` files in `/mnt/ssd/logs/` are rotated automatically as soon as they exceed 100 KB**. When a rotation occurs:

* The current log file is compressed (e.g., into `.gz`).
* Up to 14 old versions of each log file are kept.
* The active log file is not deleted or moved but truncated in place so the script can keep writing (**copytruncate**).

### Automatic execution

Log rotation is handled automatically via systemd using the timer:

```
logrotate.timer
```

This timer runs in the background and checks daily if any logs need to be rotated.

---

### Example of the logrotate configuration

```conf
/mnt/ssd/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    size 100k
    maxage 14
    dateext
    copytruncate
}
```

Key settings explained:

* `size 100k`: rotates when a log exceeds 100 KB.
* `rotate 14`: keeps a maximum of 14 rotated log files.
* `compress`: compresses old logs (gzip).
* `copytruncate`: truncates the active file in place so the script keeps writing smoothly.

---

### Watchdog system

The `watchdog_checker.py` script monitors whether the status files in `/mnt/ssd/status/` are updated and fresh. For example:

* `mppt.status` must be updated at least every 5 minutes.
* `video.status` can be up to 130 minutes old.

If a file is missing, too old, or contains an error (the line starts with `ERROR`), a warning is logged to:

```
/mnt/ssd/logs/watchdog.log
```

Optionally, the script can trigger a system reboot if something goes wrong (this feature is currently commented out in the script).

The watchdog continuously checks and logs any issues, ensuring that problems are spotted quickly.

---

### System overview

* Each script or service writes its logs to `/mnt/ssd/logs/`.
* The watchdog monitors the status files and writes its findings to `watchdog.log`.
* Logrotate ensures logs don’t grow too large and keeps them compressed and tidy.
* Everything runs automatically thanks to systemd (`logrotate.timer`).

---

### Table: logging and status overview

| **Script/Service**   | **Log file**                     | **Status file**               | **Purpose**                              |
| -------------------- | -------------------------------- | ----------------------------- | ---------------------------------------- |
| router.py            | /mnt/ssd/logs/router.log         | /mnt/ssd/status/router.status | Reads LTE signal & publishes via MQTT    |
| read\_mppt.py        | /mnt/ssd/logs/mppt.log           | /mnt/ssd/status/mppt.status   | Reads MPPT data & publishes via MQTT     |
| dht11.py             | /mnt/ssd/logs/dht11.log          | /mnt/ssd/status/dht11.status  | Reads temp/humidity & publishes via MQTT |
| videoscript.sh       | /mnt/ssd/logs/video\_capture.log | /mnt/ssd/status/video.status  | Captures video & uploads to the server   |
| toggle\_device.py    | /mnt/ssd/logs/toggle\_device.log | /mnt/ssd/status/toggle.status | Toggles GPIO power (e.g., camera on/off) |
| watchdog\_checker.py | /mnt/ssd/logs/watchdog.log       | reads all status files        | Checks system health & logs status       |

*Note: I assumed you now also write a `toggle.status` or similar status file since it’s no longer empty. If that’s not the case, let me know!*

---
## Diagram

![diagram](https://github.com/user-attachments/assets/8beee755-ed5f-4c70-aa3a-1bf7864e4b1b)

---

## 2️⃣ Recommendations to streamline things

The setup is already well-organized, but here are some suggestions to improve **clarity and maintainability:**

---

**A. Create a diagram.**

A **visual overview** helps a lot:

* Arrows from scripts → log files
* Log files → logrotate → compression
* Watchdog → reads status files → checks system health

This makes it easier for anyone to understand the flow.

---

**B. Use a standard logging module everywhere.**

Right now, each script sets up logging individually. It’s best practice to **centralize the logging setup** (e.g., a simple helper module that sets the log format and file). That ensures consistency across all scripts.

---

**C. Check the logrotate operation.**

Even though logrotate runs automatically via systemd, it’s good to occasionally check:

* View status:

  ```bash
  systemctl status logrotate.timer
  ```
* Manually trigger a rotation to test:

  ```bash
  logrotate /etc/logrotate.conf --debug
  ```

---

**D. Automate service health checks.**

In your `Troubleshooting.md`, you have:

```bash
systemctl list-units --type=service --state=running | grep mqtt
```

It might be more user-friendly to create a `health_check.sh` script that checks **VPN, MQTT, watchdog status, disk space**, etc., so you only need to run one command.

---

**E. Keep logs separated per script.**

You're already doing this well: each script has its own log file (like `mppt.log`, `router.log`...), which keeps everything clear and easy to debug.

---

**F. Consider the `maxage` setting.**

Right now:

```conf
maxage 14
```

This means that even small logs older than 14 days will be rotated out. If you want to **keep all logs regardless of age** (especially since you have a 1TB SSD), you could remove `maxage` entirely and rely only on the file size to trigger rotation.

---

## Conclusion

* The current setup is solid: **log files to SSD**, **logrotate prevents overflow**, and the **watchdog ensures system health.**
* To make it even clearer:

  * Add a **diagram** and keep the overview table up to date.
  * Optional improvements:

    * Standardize logging setup across scripts.
    * Build a single health-check script.
    * Regularly test logrotate works as expected.


