# from socket import *
import socket

multicast_port = 39090
multicast_group = "227.0.1.1"
interface_ip = "192.168.0.34"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", multicast_port))
s.setblocking(0)
mreq = socket.inet_aton(multicast_group) + socket.inet_aton(interface_ip)
s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


while 1:
    try:
        print(s.recv(1500))
    except Exception as msg:
        # print(f'Ошибка {msg}')
        continue
