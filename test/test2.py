import datetime
import threading
from server_checker import RunAndReturn


inferno_host = '46.8.220.75'


def req(l_ind, r_ind, name):
    file_name = "log" + name + ".txt"
    file_open_flag = "a"
    file = open(file_name, file_open_flag)
    for port in range(l_ind, r_ind, 10):

        # print(name, port, RunAndReturn(martin_host, port))
        ret_arr = RunAndReturn(inferno_host, port)

        arr = ret_arr
        # now = datetime.datetime.utcnow()
        text = ''
        # text += now.__str__()
        text += ' ' + str(inferno_host) + ':' + str(port)
        if not len(arr):
            text += ' unavailable'
        else:
            text += ' available'
            players_num = arr.pop(0)
            players = arr
            text += f' players: {players_num} '
            for i in players:
                text += i + ','

        file = open(file_name, file_open_flag)
        file.write(text + '\n')
        file.close()


# file_name = "log.txt"
# file_open_flag = "a"
# file = open(self.file_name, self.file_open_flag)
# file.write(text + '\n')
# file.close()

for i in range(10):
    name = "req" + str(i)
    # req1 = threading.Thread(target=req, args=(1000+i, 100001, name), name=name)
    req1 = threading.Thread(target=req, args=(i, 101, name), name=name)
    req1.start()

# от 30к до 50к