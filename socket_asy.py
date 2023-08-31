import asyncio
import socket
from enum import Enum
from multipledispatch import dispatch
# from socket import *
# import Liter


class typeSocket(Enum):
    TCP = (socket.AF_INET, socket.SOCK_STREAM)
    UDP = (socket.AF_INET, socket.SOCK_DGRAM)
    UDP_multicast = (socket.AF_INET, socket.SOCK_DGRAM)

# type_socket = {'TCP': (socket.AF_INET, socket.SOCK_STREAM),
#                'UDP': (socket.AF_INET, socket.SOCK_DGRAM),
#                'UDP_multicast': (socket.AF_INET, socket.SOCK_DGRAM),
# }


class Socket_asy():

    async def new_connect(self, type_socket: typeSocket,
                          ip, port):
        '''TCP
                ip - адрес сервера \n
                port - порт сервера \n
            UDP
                ip - адрес сервера \n
                port - порт сервера \n
            UDP multicast
                ip - адрес сетевого интерфейса (своего) \n
                port - порт мультикаст рассылки \n
                m_group - адрес мультикаст рассылки (227.0.1.1)
            '''
        s = socket.socket(*type_socket.value)
        s.bind(('', port))
        s.setblocking(0)
        loop = asyncio.get_event_loop()
        await loop.sock_connect(s, (ip, port))

        async def recv():
            try:
                data = loop.sock_recv(s, 1024)
                result = await data
                return result
            except socket.error as msg:
                print(f'исключение {msg}')
            except Exception as msg:
                print(f'Аларм {msg}')

        async def write(byte: bytes):
            return await loop.sock_sendall(s, byte)
        return recv, write

    async def new_connect_m(self, type_socket: typeSocket,
                            interface_ip, multicast_port, m_group):
        '''UDP multicast \n
                ip - адрес сетевого интерфейса (своего) \n
                port - порт мультикаст рассылки \n
                m_group - адрес мультикаст рассылки (227.0.1.1)

            '''

        s = socket.socket(*type_socket.value)
        s.bind(('', multicast_port))
        s.setblocking(0)
        merg = socket.inet_aton(m_group) + socket.inet_aton(interface_ip)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, merg)
        loop = asyncio.get_event_loop()
        loop.sock_connect(s, (m_group, multicast_port))

        async def recv():
            try:
                data = loop.sock_recv(s, 1024)
                result = await data
                return result
            except socket.error as msg:
                print(f'исключение {msg}')
            except Exception as msg:
                print(f'Аларм {msg}')

        async def write(byte: bytes):
            return await loop.sock_sendall(s, byte)
        return recv, write


async def main():
    sock = Socket_asy()
    # reader, writer = await sock.new_connect_m(typeSocket.UDP_multicast,
    #                                           '192.168.0.34',
    #                                           39090, '227.0.1.1')
    # while 1:
    #     x = reader()
    #     print(await x)

    reader, writer = await sock.new_connect(typeSocket.TCP,
                                            '192.168.1.115',
                                            9760)
    await writer(b'$t#')
    await writer(b'$t#')
    while 1:
        x = reader()
        print(await x)

asyncio.run(main())
