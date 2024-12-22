import os
import threading
import time
import datetime
from server_checker import RunAndReturn
from flask_server import run


# 217.9.89.177:25565
# INFO 2023-07-05 18:45:40,060 available, 1 online: izipin_

# "45.153.69.196:25565" сервер мартина

# TODO: разделить на два класса
class Checker:
    thread_listener = None
    thread_scaner = None

    def __init__(self, host, port=25565):
        self.file_name = "martin_log.txt"
        self.file_open_flag = "a"
        self.file_clear_flag = "w"
        self.timeout = 60  # seconds to wait between requests
        self.host = host
        self.port = port
        self.scan_flag_event = threading.Event()
        self.listen_flag_event = threading.Event()
        self.is_scaner_on = None
        self.is_listener_on = None

    def start(self):
        self.turn_scaner_on()
        self.turn_listener_on()

    def listener(self):
        while not self.listen_flag_event.is_set():
            inp = input().split(" ")
            # print(inp)
            # continue
            if inp[0] == "exit":
                self.turn_scaner_off()
                self.turn_listener_off()
            elif inp[0] == "off":  #TODO: пофиксить зависание на минуту
                self.turn_scaner_off()
            elif inp[0] == "on":
                self.turn_scaner_on()
            # elif inp[0] == "log clear":
            #     self.clear_file()
            elif inp[0] == "is" and inp[1] == "on":
                print(self.is_scaner_online())
            # elif inp[0] == "help":
            #     self.clear_file()
            # elif inp[0] == "log":
            #     self.clear_file()
            elif inp[0] == "get":
                print(self.request())
            else:
                print("хуита")

    def is_scaner_online(self):
        return self.is_scaner_on

    def is_listener_online(self):
        return self.is_listener_on

    def turn_scaner_on(self):
        if not self.is_scaner_on:
            self.scan_flag_event.clear()
            self.thread_scaner = threading.Thread(
                target=self.scaner,
                args=(),
                name="scaner"
            )
            self.thread_scaner.start()
            self.is_scaner_on = True

    def turn_scaner_off(self):
        if self.is_scaner_on:
            self.scan_flag_event.set()
            self.thread_scaner.join()
            self.thread_scaner = None
            self.is_scaner_on = False

    def turn_listener_on(self):
        if not self.is_listener_on:
            self.listen_flag_event.clear()
            self.thread_listener = threading.Thread(
                target=self.listener,
                args=(),
                name="listener"
            )
            self.thread_listener.start()
            self.is_listener_on = True

    def turn_listener_off(self):
        if self.is_listener_on:
            self.listen_flag_event.set()
            # self.thread_listener.join()
            self.thread_listener = None
            self.is_listener_on = False

    def scaner(self):
        while not self.scan_flag_event.is_set():
            ret_arr = self.request()
            self.make_record(ret_arr)
            time.sleep(self.timeout)
            # time.sleep(1)

    def request(self):
        return RunAndReturn(self.host, self.port)

    def make_record(self, inp_arr):
        arr = inp_arr.copy()
        now = datetime.datetime.now()
        text = ''
        text += now.__str__()
        text += ' ' + str(self.host) + ':' + str(self.port)
        if not len(arr):
            text += ' unavailable'
        else:
            text += ' available'
            players_num = arr.pop(0)
            players = arr
            text += f' players: {players_num} '
            for i in players:
                text += i + ','
        self.write_to_file(text)

    def write_to_file(self, text):
        file = open(self.file_name, self.file_open_flag)
        file.write(text + '\n')
        file.close()

    # TODO fill this functions
    def read_from_file(self):
        pass

    def downoad_file(self):
        pass

    def print_help(self):
        pass

    # def clear_file(self):
    #     file = open(self.file_name, self.file_clear_flag)
    #     file.close()


if __name__ == '__main__':
    # 45.153.69.196:25565 - сервер мартина
    # host = '217.9.89.177'
    # wrong_host = '217.90.89.177'
    # port = 25565
    #
    # izi_host = '168.119.145.214'
    # izi_port = 25638
    #
    # inferno_host = '46.8.220.75'
    # inferno_port = 25565

    martin_host = '45.153.69.196'
    martin_port = 25565

    # os.system(f"python server_checker.py {host}")
    ret_arr = RunAndReturn(martin_host)
    if len(ret_arr):
        print(ret_arr)
    else:
        print("сервер наебнулся")
    t = threading.Thread(target=run)
    t.start()

    check_inferno = Checker(martin_host, martin_port)
    check_inferno.start()