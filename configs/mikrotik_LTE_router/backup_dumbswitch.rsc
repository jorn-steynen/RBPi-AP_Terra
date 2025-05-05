/interface bridge
add name=bridge1

/interface ethernet
set [ find default-name=ether1 ] poe-out=off
set [ find default-name=ether2 ] poe-out=off
set [ find default-name=ether3 ] poe-out=off
set [ find default-name=ether4 ] poe-out=off
set [ find default-name=ether5 ] poe-out=off

/interface wireless
set [ find default-name=wlan1 ] ssid=B-SaFFeR-2.4Gz
set [ find default-name=wlan2 ] ssid=B-SaFFeR-5Gz
set wlan1 disabled=yes
set wlan2 disabled=yes

/interface bridge port
add bridge=bridge1 interface=ether1
add bridge=bridge1 interface=ether2
add bridge=bridge1 interface=ether3
add bridge=bridge1 interface=ether4
add bridge=bridge1 interface=ether5

/ip dhcp-client
add interface=bridge1

/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set www-ssl disabled=no

/system identity
set name=dumb-switch
