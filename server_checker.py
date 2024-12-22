#!/usr/bin/env python3
"""Checks the status (availability, logged-in players) on a Minecraft server.

Example:
    $ %(prog)s host [port]
    available, 3 online: mf, dignity, viking

    or

    # >>> McServer('my.mcserver.com').Update().player_names_sample
    frozenset(['mf', 'dignity', 'viking'])

Based on:
    https://gist.github.com/barneygale/1209061
Protocol reference:
    http://wiki.vg/Server_List_Ping
"""
# 217.9.89.177:25565 маевский был
import argparse
import json
import logging
import socket
import struct
from pprint import pprint

DEFAULT_PORT = 25565
TIMEOUT_SEC = 5.0


class McServer:

    def __init__(self, host, port=DEFAULT_PORT):
        self._host = host
        self._port = int(port)
        self._Reinit()

    def _Reinit(self):
        self._available = False
        self._num_players_online = 0
        self._player_names_sample = frozenset()

    def Update(self):
        self._Reinit()
        try:
            json_dict = GetJson(self._host, port=self._port)
        except (socket.error, ValueError) as e:
            logging.debug(e)
            return self
        try:
            # pprint(json_dict)
            self._num_players_online = json_dict['players']['online']
            try:
                if self._num_players_online:
                    self._player_names_sample = frozenset(
                        player_data['name']
                        for player_data in json_dict['players']['sample'])
            except :
                self._player_names_sample = frozenset()
            self._available = True
            return self
        except KeyError as e:
            # happens during Minecraft server startup
            logging.error('incomplete status: %s %s', e, json_dict)
            logging.error('incomplete status: %s', self._port)
            return self

    @property
    def available(self):
        return self._available

    @property
    def num_players_online(self):
        return self._num_players_online

    @property
    def player_names_sample(self):
        return self._player_names_sample


def GetJson(host, port=DEFAULT_PORT):
    """
  Example response:

  json_dict = {
    u'players': {
      u'sample': [
        {u'id': u'6a0c2570-274f-36b8-97b0-898868ba6827', u'name': u'mf'}
      ],
      u'max': 20,
      u'online': 1,
    },
    u'version': {u'protocol': 5, u'name': u'1.7.8'},
    u'description': u'1.7.8',
    u'favicon': u'data:image/png;base64,iVBORw0K...YII=',
  }
  """
    # Open the socket and connect.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT_SEC)
    s.connect((host, port))

    # Send the handshake + status request.
    s.send(_PackData(b'\x00\x00' + _PackData(host.encode('utf8')) + _PackPort(port) + b'\x01'))
    s.send(_PackData(b'\x00'))

    # Read the response.
    unused_packet_len = _UnpackVarint(s)
    unused_packet_id = _UnpackVarint(s)
    expected_response_len = _UnpackVarint(s)

    data = b''
    while len(data) < expected_response_len:
        data += s.recv(1024)

    s.close()

    return json.loads(data.decode('utf8'))


def _UnpackVarint(s):
    num = 0
    for i in range(5):
        next_byte = ord(s.recv(1))
        num |= (next_byte & 0x7F) << 7 * i
        if not next_byte & 0x80:
            break
    return num


def _PackVarint(num):
    remainder = num
    packed = b''
    while True:
        next_byte = remainder & 0x7F
        remainder >>= 7
        packed += struct.pack('B', next_byte | (0x80 if remainder > 0 else 0))
        if remainder == 0:
            break
    return packed


def _PackData(data_str):
    return _PackVarint(len(data_str)) + data_str


def _PackPort(port_num):
    return struct.pack('>H', port_num)


def RunAndReturn(host, port=DEFAULT_PORT):
    server = McServer(host, port)
    server.Update()

    if server.available:
        lst = [server.num_players_online]
        lst.extend(list(server.player_names_sample))
        return lst
    else:
        return list()


if __name__ == '__main__':
    """задаются настройки логгера вывода"""
    logging.basicConfig(
                        format='%(levelname)s %(asctime)s %(filename)s:%(lineno)s: %(message)s',
                        # format='%(levelname)s %(asctime)s %(message)s',
                        level=logging.DEBUG
    )
    """тут берутся доки сверху"""
    summary_line, _, main_doc = __doc__.partition('\n\n')
    # print(f'{summary_line=}, {_=}, {main_doc=}')
    """ тут описывается сама прога, зачем я хй знает. """
    parser = argparse.ArgumentParser(
                                    description=summary_line,
                                    # description='prog name',
                                    epilog=main_doc,
                                    # epilog='what it does',
                                    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    """ добавляется флаг для аргумента для порта необязательный """
    parser.add_argument(
                        '--port', type=int, default=DEFAULT_PORT,
                        help='defaults to %d' % DEFAULT_PORT
    )
    """ добавляется флаг для аргумента для хоста обязательный """
    parser.add_argument('host')
    """ забираем аргументы """
    args = parser.parse_args()
    # print(f'{args=}', type(args))
    """ выводит строку информации что читаем такого типа:
        INFO 2023-07-05 15:51:39,927 querying 217.9.89.177:25565
    """
    logging.info('querying %s:%d', args.host, args.port)
    # создаем и читаем сервер
    server = McServer(args.host, port=args.port)
    server.Update()
    # проверяем
    if server.available:
        logging.info(
                    'available, %d online: %s',
                    server.num_players_online,
                    ', '.join(server.player_names_sample)
        )
    else:
        logging.info('unavailable')
