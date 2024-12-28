from flask import Flask, render_template, request
from threading import Thread


application = Flask(__name__)

userLog = ''
userPass = ''
output_file = 'martin_log.txt'


def parse_file():
    file = open(output_file, 'r')
    context = []
    for line in file:
        line = line.strip()
        l = list(line.split(sep=' ', maxsplit=6))
        if len(l) > 6:
            names = l.pop(-1)
            names = names.split(sep=',')
            names.pop(-1)
            l.append(names)
        else:
            for i in range(7 - len(l)):
                l.append('0')
        if len(l) > 5:
            int_num = int(l[5])
            l.pop(5)
            l.insert(5, int_num)
        tmp = l[1][:-3:]
        l.pop(1)
        l.insert(1, tmp)
        # print(l)
        tup = tuple(l)
        context.append(tup)
    file.close()
    context.reverse()
    return context


@application.route("/", methods=['POST', 'GET'])
def hello():

    context = parse_file()
    # if request.method == 'POST':
    #     ip = request.remote_addr
    #     file = open('messages', 'a')
    #     file.write(request.form.to_dict()['message'] + ', ' + ip + '\n')
    #     file.close()
    #     context = parse_file()
    return render_template('parser.html', context=context)


def run():
    # application.run(host='0.0.0.0')
    application.run(host='0.0.0.0', port=8000, debug=False)


if __name__ == '__main__':
    t = Thread(target=run)
    t.start()