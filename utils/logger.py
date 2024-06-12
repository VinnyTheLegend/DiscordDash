import os
import datetime 
import threading

now = datetime.datetime.now()
folder = os.path.dirname(__file__)
path = os.path.join(folder, f"logs\\{now.strftime('%Y-%m-%d')}.txt")

last_10 = []
if os.path.exists(path):
    with open(path) as file:
        for line in (file.readlines() [-10:]):
            line = line[:-1]
            last_10.append(line)

def logWrite(new_log: str):
    f = open(path, "a")
    f.write(new_log)
    f.close()

def new(new_log: str):
    now = datetime.datetime.now()
    new_string = f"{now.strftime('%Y/%m/%d %I:%M:%S%p')} {new_log}\n"
    last_10.append(new_string[:-1])

    if len(last_10) > 10:
        while len(last_10) > 10:
            del last_10[0]

    download_thread = threading.Thread(target=logWrite, name="logWrite", args=[new_string])
    download_thread.start()
    return new_string[:-1]