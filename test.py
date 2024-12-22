import os
import sys
# from pprint import pprint as print
sys.path.append('/home/u/user/venv/lib/python3.10/site-packages/')
from flask import Flask, render_template, current_app


app = Flask(__name__)
application = app

userLog = ''
userPass = ''
output_file = 'save-fix.txt'


def parse_file():
    with current_app.open_resource(output_file) as file:
        f = file.read()
    log_string = f.decode('utf-8')
    parsed_data = []

    for line in log_string.strip().split('\r\n'):
        parts = line.split(' ')
        if len(parts) < 3:
            parsed_data.append(("", "", "", None, 0, []))
            continue  # Пропускаем строки, которые не имеют нужной структуры
        try:
            date = parts[0]
            time = parts[1]
            ip_port = parts[2]

            if "unavailable" in parts:
                parsed_data.append((date, time, ip_port, "unavailable", 0, None))
            elif "available" in parts and "players:" in parts:
                players_index = parts.index("players:")
                num_players_index = players_index + 1
                num_players = int(parts[num_players_index])

                if num_players > 0:
                    player_names_str = ' '.join(parts[num_players_index + 1:])
                    if player_names_str.endswith(','):
                        player_names_str = player_names_str[:-1]
                    player_names = player_names_str.split(',')
                    parsed_data.append((date, time, ip_port, "available", num_players, player_names))
                else:
                    parsed_data.append((date, time, ip_port, "available", 0, []))
        except (ValueError, IndexError):
            # Обработка случаев, когда формат не соответствует ожидаемому
            parsed_data.append(("", "", "", "unavailable", 0, []))

    parsed_data.reverse()
    return parsed_data


@application.route("/", methods=['POST', 'GET'])
def hello():
    context = parse_file()
    # print(context)
    return render_template('parser.html', context=context)

if __name__ == '__main__':
    app.run(port=99)