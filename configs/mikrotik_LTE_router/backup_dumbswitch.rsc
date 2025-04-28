# jan/27/1970 22:09:14 by RouterOS 6.48.6
# software id = KEJ8-U8P1
#
# model = RB952Ui-5ac2nD
# serial number = HD908CBK0A3
/interface bridge
add name=bridge-local
/interface ethernet
set [ find default-name=ether5 ] poe-out=off
/interface wireless
set [ find default-name=wlan1 ] ssid=MikroTik
set [ find default-name=wlan2 ] ssid=MikroTik
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip hotspot profile
set [ find default=yes ] html-directory=hotspot
/interface bridge port
add bridge=bridge-local interface=ether1
add bridge=bridge-local interface=ether2
add bridge=bridge-local interface=ether3
add bridge=bridge-local interface=ether4
add bridge=bridge-local interface=ether5
/ip dhcp-client
add interface=bridge-local
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set www-ssl disabled=no
/system identity
set name=dumb-switch
