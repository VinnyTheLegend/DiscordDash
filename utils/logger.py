import os
import datetime 
import threading

folder = os.path.dirname(__file__)
now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-4.0)))
if (not os.path.exists(os.path.join(folder, "logs"))):
    os.mkdir(os.path.join(folder, "logs"))
path = os.path.join(folder, f"logs\\{now.strftime('%Y-%m')}.txt")

last_25 = []
if os.path.exists(path):
    with open(path) as file:
        for line in (file.readlines() [-25:]):
            line = line[:-1]
            last_25.append(line)

def logWrite(new_log: str):
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-4.0)))
    path = os.path.join(folder, f"logs\\{now.strftime('%Y-%m')}.txt")
    f = open(path, "a")
    f.write(new_log)
    f.close()

def new(new_log: str):
    now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-4.0)))
    new_string = f"{now.strftime('%m/%d/%Y %I:%M:%S%p')} {new_log}\n"
    last_25.append(new_string[:-1])

    if len(last_25) > 25:
        while len(last_25) > 25:
            del last_25[0]

    download_thread = threading.Thread(target=logWrite, name="logWrite", args=[new_string])
    download_thread.start()
    return new_string[:-1]