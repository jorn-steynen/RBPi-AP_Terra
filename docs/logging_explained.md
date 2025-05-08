1️⃣ Een **verklaring van hoe het geheel momenteel werkt**
2️⃣ Een **korte lijst aanbevelingen** om het *nog iets te stroomlijnen of verbeteren*
---

## 1️⃣ Hoe het werkt – uitleg

**Wat doet het systeem precies?**

### Logbestanden en locatie

Alle logbestanden van het systeem (zoals `video_capture.log`, `watchdog.log`, `mppt.log`, enz.) worden opgeslagen in:

```
/mnt/ssd/logs/
```

Hierdoor blijven logbestanden weg van de SD-kaart van de Raspberry Pi, wat belangrijk is om slijtage van de SD-kaart te voorkomen en voldoende opslagcapaciteit te behouden.

### Logrotatie

Om te voorkomen dat de logbestanden te groot worden en de SSD vollopen, is automatische logrotatie ingesteld via een configuratiebestand:

```
/etc/logrotate.d/uganda_logs
```

Deze configuratie zorgt ervoor dat **alle .log-bestanden in `/mnt/ssd/logs/` automatisch worden geroteerd zodra ze groter worden dan 100 KB**. Tijdens rotatie gebeurt het volgende:

* Het huidige logbestand wordt gecomprimeerd (bijvoorbeeld naar `.gz`).
* Er worden maximaal 14 oude versies van elk logbestand bewaard.
* Het actieve logbestand wordt niet verwijderd of verplaatst, maar leeggemaakt zodat het script kan blijven schrijven (**copytruncate**).

### Automatische uitvoering

Logrotate wordt automatisch uitgevoerd via systemd dankzij de timer:

```
logrotate.timer
```

Deze timer draait op de achtergrond en controleert dagelijks of logbestanden moeten worden geroteerd.

---

### Voorbeeld van de logrotate-configuratie

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

Toelichting van de belangrijkste instellingen:

* `size 100k`: rotatie zodra een bestand groter wordt dan 100 KB.
* `rotate 14`: bewaart maximaal 14 oude logbestanden.
* `compress`: maakt oude logbestanden kleiner (gzip).
* `copytruncate`: houdt het originele bestand actief maar maakt het leeg zodat het script blijft schrijven.

---

### Watchdog-systeem

Het script `watchdog_checker.py` controleert of de statusbestanden in `/mnt/ssd/status/` correct en recent genoeg zijn bijgewerkt. Voorbeelden:

* `mppt.status` moet minstens elke 5 minuten worden bijgewerkt.
* `video.status` mag maximaal 130 minuten oud zijn.

Als een bestand ontbreekt, te oud is, of een foutmelding bevat (regel begint met `ERROR`), wordt een waarschuwing geschreven naar:

```
/mnt/ssd/logs/watchdog.log
```

Het script kan desgewenst een automatische herstart van het systeem uitvoeren wanneer een probleem wordt vastgesteld (momenteel staat deze functie uitgecommentarieerd in het script).

De watchdog voert dus voortdurend controles uit en zorgt ervoor dat problemen snel worden gesignaleerd via logging.

---

### Overzicht van de werking

* Elk script of proces schrijft zijn logbestanden weg naar `/mnt/ssd/logs/`.
* De watchdog controleert of alle statusbestanden up-to-date zijn en logt zijn bevindingen in `watchdog.log`.
* Logrotate zorgt ervoor dat alle logbestanden niet te groot worden en oude logs automatisch worden samengevoegd en bewaard.
* Dit proces draait volledig automatisch dankzij systemd (logrotate.timer).

---

## 2️⃣ Aanbevelingen om het te stroomlijnen

Eigenlijk is je setup al **goed geregeld** qua logbeheer, maar enkele suggesties voor **duidelijkheid en onderhoudbaarheid**:

---

**A. Maak een schema/diagram.**

Een **visueel overzicht** helpt enorm:

* pijltjes van scripts → logbestanden
* logbestanden → logrotate → compressie
* watchdog → statusbestanden → controle

Dat maakt het voor iedereen overzichtelijk.

---

**B. Zet alle logging naar één standaardlogger.**

Je scripts loggen los van elkaar. Het is netjes als ze **allemaal dezelfde logging-standaard gebruiken**. Je zou bijvoorbeeld:

* Een kleine **logging-lib** maken die altijd schrijft naar `/mnt/ssd/logs/` + datumstempel.
* Zo weet je zeker dat alle logs hetzelfde format hebben (maakt troubleshooten makkelijker).

---

**C. Controleer je logrotate-run.**

Kleine verbetering: logrotate **wordt getriggerd door een timer** maar als je echt wil weten of het goed werkt:

* Bekijk de status met:
  `systemctl status logrotate.timer`
* En **forceren kan altijd** met:
  `logrotate /etc/logrotate.conf`
  (handig om te testen).

---

**D. Service checks automatiseren.**

In je Troubleshooting.md zeg je:

```bash
systemctl list-units --type=service --state=running | grep mqtt
```

Misschien handiger om een **scriptje** te maken zoals `health_check.sh` dat alles samen checkt (VPN, MQTT, watchdog, ruimte SSD), zodat je maar 1 commando hoeft te doen.

---

**E. Logs scheiden per script.**

Je doet dit nu eigenlijk al prima! Maar: soms loggen scripts naar *dezelfde* logfile (bijvoorbeeld video + watchdog samen), en dat kan verwarrend zijn. Houd per script een eigen logfile aan → dat maakt het netjes.

---

**F. Overweeg rotating maxage.**

Je hebt nu:

```conf
maxage 14
```

Dat is goed, maar: stel dat je een tijd géén logging hebt, dan gooit logrotate oude logs na 14 dagen toch weg. Dat is prima maar wees je er bewust van: als je *permanent logs wilt bewaren*, zet `maxage` lager of weg.

---

## Conclusie

* Je huidige setup is goed geregeld: **logfiles op SSD**, **logrotate om te voorkomen dat het volloopt**, en een **watchdog** die checkt of alles nog werkt.
* Voor duidelijkheid:

  * Voeg een **diagram** toe aan je documentatie.
  * Misschien een **samenvattende tabel** van welke service naar welk logbestand schrijft.
* Kleine verbeteringen (optioneel):

  * Zorg dat alle scripts dezelfde logging-aanpak gebruiken.
  * Overweeg een enkel script om alle healthchecks samen te tonen.
  * Zorg dat je een keer handmatig test of logrotate werkt zoals verwacht.

Laat weten of je wilt dat ik een schema maak of dat ik bijvoorbeeld een stuk tekst aanpas in je Troubleshooting.md om het overzichtelijker te maken!
