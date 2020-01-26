import logging, logging.handlers
import os
from constant import BASE_DIR, LOGGING_FORMAT
import datetime

class LogSupport(object):

    debug = False

    def __init__(self):
        self.logging = self.init_log()
        self.logging_info("-init logging module success")

    def init_log(self):
        logging_dir = os.path.join(BASE_DIR, "log/")
        if self.debug:
            print("logging_dir:", logging_dir)
        check_dir_exist(logging_dir)
        logger = logging.getLogger('log')
        logger.setLevel(logging.INFO)
        log_path = logging_dir + get_now_time() + ".log"
        # 存在bug，无法按天分割
        # 参考博客：https://blog.csdn.net/weixin_38107388/article/details/90639151
        # fh = logging.handlers.TimedRotatingFileHandler(logging_dir + 'support', when='S', backupCount=5, encoding='utf-8')
        # fh.suffix = "%Y%m%d.log"
        fh = logging.FileHandler(log_path, encoding='utf-8', mode='a')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(LOGGING_FORMAT)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def logging_info(self, info):
        if self.debug:
            print(info)
        self.logging.info(info)

def check_dir_exist(dir):
    if os.path.exists(dir) == False:
        os.makedirs(dir)

def get_now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d')

if __name__ =='__main__':
    ls = LogSupport()
    ls.logging_info("test")
    try:
        raise IndexError
    except IndexError as e:
        ls.logging.exception(e)
    ls.logging.warning("警告")

