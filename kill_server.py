import os
import re

print("Running sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("rm -f stop.txt")
out = os.popen("ps -aux | grep raspimjpeg").read()
for line in out.split('\n'):
    try:
        process_id = re.split('\s+', line)[1]
    except:
        continue
    os.system("pkill %s" % process_id)
    print("pkill %s" % process_id)
print("\n")

out = os.popen("ps -aux | grep python").read()
for line in out.split('\n'):
    try:
        process_id = re.split('\s+', line)[1]
        fname = re.split('\s+', line)[11]
        if fname != 'server_main.py':
            continue
    except:
        continue
    os.system("kill -9 %s" % process_id)
    print("kill -9 %s" % process_id)