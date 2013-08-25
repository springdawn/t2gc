import os
import time


def nowtime():
    return time.strftime('%Y/%m/%dT%H:%M:%S%z')

# TODO: ログをloggingモジュールを使うように
logfile = os.path.dirname(os.path.abspath(__file__)) + '/t2gc.log'
timezone = 'Asia/Tokyo'
