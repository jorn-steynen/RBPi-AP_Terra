/system identity
set name=B-SaFFeR-LTE-Router

/interface bridge
add name=bridge1

/interface ethernet
set [ find default-name=ether1 ] poe-out=off

/interface bridge port
add bridge=bridge1 interface=ether1
add bridge=bridge1 interface=wlan1

/interface wireless
set [ find default-name=wlan1 ] ssid=B-SaFFeR-LTE-WiFi disabled=yes

/interface lte apn
add name=APN apn="apn.here" passthrough=no

/interface lte
set [ find name=lte1 ] apn-profiles=APN network-mode=lte

/ip address
add address=192.168.88.1/24 interface=bridge1 comment=LAN

/ip pool
add name=dhcp-pool ranges=192.168.88.50-192.168.88.254

/ip dhcp-server
add name=dhcp1 interface=bridge1 address-pool=dhcp_pool lease-time=1h

/ip dhcp-server network
add address=192.168.88.0/24 gateway=192.168.88.1 dns-server=8.8.8.8,1.1.1.1

/ip dns
set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes

/ip dhcp-client
add interface=lte1 use-peer-dns=no use-peer-ntp=no add-default-route=yes

/ip firewall nat
add chain=srcnat out-interface=lte1 action=masquerade comment="NAT LAN → LTE"

/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set www-ssl disabled=no
set api disabled=yes
set api-ssl disabled=yes

/system clock
set time-zone-name=Africa/Kampala
