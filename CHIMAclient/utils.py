import os

def ip2int(ip):
    h=list(map(int,ip.split(".")))
    return (h[0]<<24)+(h[1]<<16)+(h[2]<<8)+(h[3]<<0)

def set_route(device, subnet):
    print("New route to %s" % subnet)
    os.system("ip route add %s dev %s" % (subnet,device) )

def remove_route(subnet):
    print("Remove route to %s" % subnet)
    os.system("ip route del %s" % subnet )

def set_arp(device, ip, mac):
    print("New static arp: %s -> %s" % (ip, mac) )
    os.system("arp -i %s -s %s %s" % (device, ip, mac) )

def remove_arp(device, ip):
    print("Remove static arp: %s" % ip )
    os.system("arp -i %s -d %s" % (device, ip) )

def set_ip(device, ip):
    print("New ip: %s -> %s" % (device, ip) )
    os.system("ip address add %s dev %s" % (ip, device) )

def remove_ip(device, ip):
    print("Removed ip: %s -> %s" % (device, ip) )
    os.system("ip address del %s dev %s" % (ip, device) )


def clean_installed_rules(subnets, device, ips):
    for sub in subnets:
        remove_route(sub)
    for ip in ips:
        remove_arp(device, ip)