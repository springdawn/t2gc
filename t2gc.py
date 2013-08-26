from googleCalendar import GoogleCalendar
from twitterConnect import TwitterConnect
from t2gcAccount import T2gcAccount
from ns import *

if __name__ == '__main__':
    with open(logfile, 'a') as f:
        now = nowtime()
        f.write(now + ' t2gc launched.\n')
    gc = GoogleCalendar()
    gc.connect()
    t = TwitterConnect()
    t2gc_account = T2gcAccount()

    def loop():
        for info in t.connectStream():
            if info == 'error':
                return loop()
            res = gc.createEvent(info[1])
            if not res:
                with open(logfile, 'a') as f:
                    now = nowtime()
                    f.write(now + ' failed event insert. reconnect.\n')
                res = gc.createEvent(info[1])
            else:
                with open(logfile, 'a') as f:
                    now = nowtime()
                    f.write(now + ' event insert.\n')
                t2gc_account.tweet(str(res), info[0])

    loop()
#while True:
#    if t.analyzeTweet(unicode(raw_input(), 'utf-8')):
#        break
