# 2025-04-20 16:18:22 by RouterOS 7.18.2
# software id = Q684-P50F
#
# model = wAPGR-5HacD2HnD
# serial number = HGS0AEM8C59
/interface bridge
add name=bridge-local
/interface wireless
set [ find default-name=wlan2 ] band=5ghz-a/n/ac channel-width=20/40mhz-Ce \
    frequency=5620 ssid=""
/interface wireguard
add listen-port=13231 mtu=1420 name=wg0
/interface lte apn
add apn=mworld.be name=internet
/interface lte
set [ find default-name=lte1 ] allow-roaming=yes apn-profiles=internet band=3
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
add authentication-types=wpa2-psk mode=dynamic-keys name=bletchley \
    supplicant-identity=""
/interface wireless
set [ find default-name=wlan1 ] band=2ghz-b/g/n country=belgium disabled=no \
    frequency=auto mode=ap-bridge security-profile=bletchley ssid=wAP-local \
    wps-mode=disabled
/ip pool
add name=dhcp_pool0 ranges=192.168.100.50-192.168.100.254
/ip dhcp-server
add address-pool=dhcp_pool0 interface=bridge-local name=dhcp1
/snmp community
set [ find default=yes ] addresses=10.8.0.6/32 disabled=yes
add addresses=192.168.100.0/24 name=public1
/interface bridge port
add bridge=bridge-local interface=ether1
add bridge=bridge-local interface=ether2
add bridge=bridge-local interface=wlan1
/interface wireguard peers
add allowed-address=10.8.0.11/32,192.168.100.0/24,10.8.0.0/24 \
    endpoint-address=wgeasy.iot-ap.be endpoint-port=51820 interface=wg0 name=\
    peer1 persistent-keepalive=25s preshared-key=\
    "zN5EhD9bRjaRdQ4SG7ZOA6tG/zURZIyMrjrN/C9dQOc=" public-key=\
    "f5jC2dSqTYDpyWRuD+BgbbP8yYnt7JJ7MILZ6N3yxmI="
/ip address
add address=192.168.100.1/24 interface=bridge-local network=192.168.100.0
add address=10.8.0.11/24 interface=wg0 network=10.8.0.0
/ip dhcp-client
# DHCP client can not run on slave or passthrough interface!
add interface=ether1
/ip dhcp-server lease
add address=192.168.100.252 client-id=1:5c:34:5b:ae:65:45 comment=\
    "Camera bullet" mac-address=5C:34:5B:AE:65:45 server=dhcp1
add address=192.168.100.251 client-id=1:e4:d:36:5c:2d:b2 comment=\
    "Laptop Jorn Wifi" mac-address=E4:0D:36:5C:2D:B2 server=dhcp1
add address=192.168.100.250 client-id=1:0:0:0:0:0:e6 comment=\
    "Laptop Jorn Eth" mac-address=00:00:00:00:00:E6 server=dhcp1
add address=192.168.100.4 client-id=1:d8:3a:dd:78:ca:ea comment=\
    "Uganda 2 RPI" mac-address=D8:3A:DD:78:CA:EA server=dhcp1
add address=192.168.100.3 client-id=1:d8:3a:dd:78:ce:da comment="Test RPI" \
    mac-address=D8:3A:DD:78:CE:DA server=dhcp1
add address=192.168.100.2 client-id=1:18:fd:74:ca:20:cf comment=hAP \
    mac-address=18:FD:74:CA:20:CF server=dhcp1
/ip dhcp-server network
add address=192.168.100.0/24 dns-server=192.168.100.1,1.1.1.1,10.150.0.1 \
    gateway=192.168.100.1
/ip dns
set allow-remote-requests=yes servers=1.1.1.1
/ip firewall filter
add action=accept chain=input dst-port=161 protocol=udp src-address=\
    192.168.100.0/24
add action=accept chain=input src-address=10.8.0.0/24
add action=accept chain=forward dst-address=192.168.100.0/24 src-address=\
    10.8.0.0/24
add action=accept chain=forward dst-address=10.8.0.0/24 src-address=\
    192.168.100.0/24
/ip firewall nat
add action=masquerade chain=srcnat out-interface=lte1
add action=masquerade chain=srcnat out-interface=wg0 src-address=\
    192.168.100.0/24
/ip hotspot profile
set [ find default=yes ] html-directory=hotspot
/ip service
set telnet disabled=yes
set ftp disabled=yes
set api disabled=yes
set winbox address=0.0.0.0/0
set api-ssl disabled=yes
/snmp
set enabled=yes trap-community=public1
/system clock
set time-zone-name=Europe/Brussels
/system note
set show-at-login=no
/system scheduler
add interval=5s name=Log_LTE_Scheduler on-event=\
    "/system script run Log_LTE_Stats" policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon \
    start-date=2025-04-03 start-time=10:56:56
/system script
add dont-require-permissions=no name=Log_LTE_Stats owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":\
    local now ([/system clock get date] . \" \" . [/system clock get time])\
    \n:local lteInfo [/interface lte monitor lte1 once as-value]\
    \n\
    \n:local RSSI (\$lteInfo->\"rssi\")\
    \n:local RSRP (\$lteInfo->\"rsrp\")\
    \n:local SINR (\$lteInfo->\"sinr\")\
    \n:local RSRQ (\$lteInfo->\"rsrq\")\
    \n\
    \n:local logLine (\"\$now,RSSI:\$RSSI,RSRP:\$RSRP,SINR:\$SINR,RSRQ:\$RSRQ\
    \\r\\n\")\
    \n\
    \n:if ([/file find name=\"lte_log.txt\"] = \"\") do={\
    \n    /file print file=lte_log.txt\
    \n}\
    \n\
    \n:file set lte_log.txt contents=([/file get lte_log.txt contents] . \$log\
    Line)\
    \n"
add dont-require-permissions=no name=jornlogLTE owner=admin policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=\
    ""
