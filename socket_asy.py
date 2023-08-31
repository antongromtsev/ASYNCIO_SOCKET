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

    async def recv(self, loop, s):
        try:
            data = loop.sock_recv(s, 1024)
            result = await data
            return result
        except socket.error as msg:
            print(f'исключение {msg}')
        except Exception as msg:
            print(f'Аларм {msg}')

    async def write(self, loop, s, byte: bytes):
        return await loop.sock_sendall(s, byte)

    async def new_connect(self, type_socket: typeSocket,
                          ip, port, m_group=None):
        '''UDP multicast \n
            ip - адрес сетевого интерфейса (своего) \n
            port - порт мультикаст рассылки \n
            m_group - адрес мультикаст рассылки (227.0.1.1)
        '''

        s = socket.socket(*type_socket.value)
        s.bind(('', port))
        s.setblocking(0)
        loop = asyncio.get_event_loop()
        if type_socket == typeSocket.UDP_multicast:
            merg = socket.inet_aton(m_group) + socket.inet_aton(ip)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, merg)
        else:
            await loop.sock_connect(s, (ip, port))

        async def wrapper_recv():
            return await self.recv(loop, s)

        async def wrapper_write(comm: bytes):
            return await self.write(loop, s, comm)

        return wrapper_recv, wrapper_write


async def main(arg):
    sock = Socket_asy()

    if arg == 3:
        reader, writer = await sock.new_connect(typeSocket.UDP_multicast,
                                                '192.168.0.34',
                                                39090, '227.0.1.1')
        while 1:
            x = await reader()
            print(x)

    if arg == 1:
        reader, writer = await sock.new_connect(typeSocket.TCP,
                                                '192.168.1.115',
                                                9760)
        await writer(b'$t#')
        await writer(b'$t#')
        while 1:
            x = await reader()
            print(x)

TCP = 1
UDP = 2
UDP_multicast = 3

if __name__ == '__main__':
    asyncio.run(main(UDP_multicast))
