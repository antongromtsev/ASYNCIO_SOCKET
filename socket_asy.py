import asyncio
import socket
from enum import Enum
from datetime import datetime as dt
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
                          ip: str, port: int, m_group: str = None):
        '''
        TCP/UDP \n
            ip - адрес сервера \n
            port - порт сервера \n
        ===================================================== \n
        UDP multicast \n
            ip - адрес сетевого интерфейса (своего) \n
            port - порт мультикаст рассылки \n
            m_group - адрес мультикаст рассылки (227.0.1.1) \n
        ===================================================== \n
        Возвращает функции: \n
        read - для чтения данных из scoket \n
        write - для отправки данных из socket (data) \n
        write_read - для отправки и последущего чтения из socket
        (data, verification) \n
            verification - для проверки содержит ли ответ данную
            последовательность \n
            планирую заменить на регулярное выражение
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

        async def wrapper_write_recv(comm: bytes, verification: bytes):
            await self.write(loop, s, comm)
            result = b''
            while verification not in result:
                data = await self.recv(loop, s)
                result += data
            return result

        return (wrapper_recv if type_socket == typeSocket.UDP_multicast
                else wrapper_recv, wrapper_write, wrapper_write_recv)


async def main(arg):
    sock = Socket_asy()
    # arg = 3
    # if arg == 3:
    #     r, w, wr = await sock.new_connect(typeSocket.UDP_multicast,
    #                                             '192.168.0.34',
    #                                             39090, '227.0.1.1')
    #     while 1:
    #         x = await r()
    #         print(x)
    # arg = 1
    # if arg == 1:
    #     r, w, wr = await sock.new_connect(typeSocket.TCP,
    #                                             '192.168.1.115',
    #                                             9760)
    #     # await w(b'$t#')
    #     # await w(b'$t#')
    #     # while 1:
    #     #     x = await r()
    #     #     print(x)
    #     x = await wr(b'$t#', b'$t')
    #     print(x)
    r_m, _, _ = await sock.new_connect(typeSocket.UDP_multicast,
                                       '192.168.0.34',
                                       39090, '227.0.1.1')
    _, w, wr = await sock.new_connect(typeSocket.TCP,
                                      '192.168.1.115',
                                      9760)

    async def cycle(func, *args):
        while 1:
            print(dt.now(), await func(*args))
            await asyncio.sleep(5)

    t1 = asyncio.create_task(cycle(r_m))
    t2 = asyncio.create_task(cycle(wr, b'$t#', b'$t'))
    await t1
    await t2


TCP = 1
UDP = 2
UDP_multicast = 3

if __name__ == '__main__':
    asyncio.run(main(UDP_multicast))
