import os
import re

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