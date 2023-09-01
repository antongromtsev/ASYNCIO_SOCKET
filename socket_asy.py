import asyncio
import socket
import time
from enum import Enum
from datetime import datetime as dt


class typeSocket(Enum):
    TCP = (socket.AF_INET, socket.SOCK_STREAM)
    UDP = (socket.AF_INET, socket.SOCK_DGRAM)
    UDP_multicast = (socket.AF_INET, socket.SOCK_DGRAM)


class Socket_asy():

    async def recv(self, loop, s):
        try:
            data = loop.sock_recv(s, 1024)
            result = await data
            return result
        except socket.error as msg:
            print(f'исключение {msg}')
            task = asyncio.current_task()
            task.cancel()
        except Exception as msg:
            print(f'Аларм {msg}')
            task = asyncio.current_task()
            task.cancel()

    async def write(self, loop, s, byte: bytes):
        try:
            await loop.sock_sendall(s, byte)
        except socket.error as msg:
            print(f'исключение {msg}')
            task = asyncio.current_task()
            task.cancel()
        except Exception as msg:
            print(f'Аларм {msg}')
            task = asyncio.current_task()
            task.cancel()

    async def new_connect(self, type_socket: typeSocket,
                          ip: str, port: int, ip_interface: str = None):
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
            merg = socket.inet_aton(ip) + socket.inet_aton(ip_interface)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, merg)
        else:
            i = 0
            while 1:
                try:
                    await asyncio.wait_for(loop.sock_connect(s, (ip, port)), 5)
                except TimeoutError:
                    i += 1
                    if i > 10:
                        print(f'Не удалось подключиться к серверу ip: {ip}. '
                              f'Проверьте подключение к сети')
                        task = asyncio.current_task()
                        task.cancel()
                        break
                    print(f'Нет ответа от сервера {ip}: попыток {i}')
                    continue
                break

        async def wrapper_recv():
            i = 0
            start = None
            while 1:
                try:
                    data = await asyncio.wait_for(self.recv(loop, s), 6)
                except TimeoutError:
                    i += 1
                    if not start:
                        start = time.time()
                    if i > 10:
                        stop = time.time()
                        print(f'Нет данных от сервера {ip} в течении '
                              f'{stop - start} сек.\n'
                              f'Соеденение разорвано!')
                        task = asyncio.current_task()
                        task.cancel()
                        break
                    print(f'Нет данных от сервера {ip}: попыток {i}')
                    continue
                return data

        async def wrapper_write(comm: bytes):
            return await self.write(loop, s, comm)

        async def wrapper_write_recv(comm: bytes, verification: bytes):
            await self.write(loop, s, comm)
            result = b''
            while verification not in result:
                if data := await wrapper_recv():  # self.recv(loop, s)
                    result += data
            return result

        return (wrapper_recv if type_socket == typeSocket.UDP_multicast
                else wrapper_recv, wrapper_write, wrapper_write_recv)


async def main():
    sock = Socket_asy()
    t1 = asyncio.create_task(sock.new_connect(typeSocket.UDP_multicast,
                                              '227.0.1.1',
                                              39090, '192.168.0.34'))
    t2 = asyncio.create_task(sock.new_connect(typeSocket.TCP,
                                              '192.168.1.115',
                                              9760))

    r_m, _, _ = await t1
    r, w, wr = await t2

    async def cycle(func: asyncio.Future, *args):
        while 1:
            try:
                print(dt.now(), await func(*args))
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    t1 = asyncio.create_task(cycle(r_m))
    t2 = asyncio.create_task(cycle(wr, b'$t#', b'$t'))
    await t1
    await t2


if __name__ == '__main__':
    asyncio.run(main())
