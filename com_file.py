

file_name = "itogo.txt"
file_open_flag = "a"
res_file = open(file_name, file_open_flag)

for i in range(100):
    locfile = open("logreq" + str(i) + ".txt", "r")
    data = locfile.read()
    res_file.write(data)
    # res_file.write("\n")

