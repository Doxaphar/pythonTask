import datetime

with open('creteLyricsData/text.txt') as f:
    lines = f.readlines()

reformed = []
prev = datetime.datetime.now().timestamp().real
for line in lines[5:20]:
    line = line[:-1].split(' ')
    reform_line = ""
    for word in line:
        a = input()
        print(word)
        reform_line += word + ":" + str(round(float(datetime.datetime.now().timestamp().real - prev), 1) / 4) + "; "
        prev = datetime.datetime.now().timestamp().real
    reformed.append(reform_line)

for i in reformed:
    print(i)