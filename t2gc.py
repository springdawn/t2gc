from googleCalendar import GoogleCalendar
from twitterConnect import TwitterConnect
from ns import *

if __name__ == '__main__':
    with open(logfile, 'a') as f:
        now = nowtime()
        f.write(now + ' t2gc launched.\n')
    gc = GoogleCalendar()
    gc.connect()
    t = TwitterConnect()

    def loop():
        for dic in t.connectStream():
            if dic == 'error':
                return loop()
            print dic
            res = gc.createEvent(dic)
            if not res:
                with open(logfile, 'a') as f:
                    now = nowtime()
                    f.write(now + ' failed event insert. reconnect.\n')
                gc.createEvent(dic)
            else:
                with open(logfile, 'a') as f:
                    now = nowtime()
                    f.write(now + ' event insert.\n')

    loop()
#while True:
#    if t.analyzeTweet(unicode(raw_input(), 'utf-8')):
#        break
