import time
import multiprocessing
from load_json import start_load_json
import os
from log_support import LogSupport

def start_pull(branch_name):
    ls.logging.info("start pull...")
    try:
        os.system("git add .")
        os.system("git commit -m 'update data'")
        os.system("git push -u origin {}".format(branch_name))
        ls.logging.info("pull finished")
    except BaseException as e:
        ls.logging.exception(e)
    time.sleep(60 * 10)

if __name__=='__main__':
    ls = LogSupport()
    p1 = multiprocessing.Process(target=start_load_json)
    p2 = multiprocessing.Process(target=start_pull, args=['maiciusData'])
    p2.start()