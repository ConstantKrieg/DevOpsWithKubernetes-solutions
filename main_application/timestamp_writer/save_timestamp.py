import time
import datetime


while True:
    with open('/files/timestamp.txt', 'w') as f:
        f.write(str(datetime.datetime.utcnow()))
    
    time.sleep(5)