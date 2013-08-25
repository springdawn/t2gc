# This Python file uses the following encoding: utf-8

from twitter import *
from ns import *
import dbm
import re
import datetime
import pytz
import sys
import socket
jst = pytz.timezone(timezone)


class TwitterConnect():
    date_format = re.compile(
        u'''d:(?:(\d{4})-)?(\d{2})-(\d{2})|(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日
        |(?:今|明後?)日''', re.X)
    start_time_format = re.compile(
        u'''s:(\d{2}):(\d{2})|(?:(\d{1,2})時(?:(\d{1,2})分)?
        |(\d{1,2}):(\d{2}))から''', re.X)
    end_time_format = re.compile(u'''e:(\d{2}):(\d{2})
                                 |(?:(\d{1,2})時(?:(\d{1,2})分)?
                                 |(\d{1,2}):(\d{2}))まで''', re.X)
    title_format = re.compile(u'''(?:t:)?
                              [\"\“\”\'\‘\’](.*?)[\"\“\”\'\‘\’]''', re.X)
    location_format = re.compile(u'l:(\S+)|(\S+)で')
    recurring_format = re.compile(u'(毎[日週])(\d{1,2})[回度]?繰り返し')
    # TODO: 繰り返しイベントフォーマット対応
#    recurring_format = re.compile(u'(毎(?:日|週(?:[月火水木金土日]曜?)?)|平日)(\d{1,2})[回度]?繰り返し')

    def __init__(self):
        self.oauth_keyfile_path = (os.path.dirname(os.path.abspath(__file__)) +
                                   '/twitter_oauth')
        if os.path.exists(self.oauth_keyfile_path + '.db'):
            # TODO: できればメソッドに移して消す
            db = dbm.open(self.oauth_keyfile_path)
            self.consumer_key = db['consumer_key']
            self.consumer_secret = db['consumer_secret']
            self.oauth_token = db['oauth_token']
            self.oauth_secret = db['oauth_secret']
            db.close()
        else:
            self.createTokenFile()
        self.twitter = Twitter(
            auth=OAuth(self.oauth_token, self.oauth_secret,
                       self.consumer_key, self.consumer_secret))
        try:
            self.cred = self.twitter.account.verify_credentials()
        except:
            print 'failed to connect Twitter\nrecreate token file'
            self.createTokenFile()
        print self.cred['id']
        self.twitter_stream = TwitterStream(
            domain='userstream.twitter.com',
            auth=OAuth(
                self.oauth_token, self.oauth_secret,
                self.consumer_key, self.consumer_secret))

    def createTokenFile(self):
        print 'create Twitter OAuth token file...'
        db = dbm.open(oauth_keyfile_path, 'n')
        self.consumer_key = db['consumer_key'] = raw_input('input consumer key :')
        self.consumer_secret = db['consumer_secret'] = raw_input('input consumer secret :')
        self.oauth_token, self.oauth_secret = oauth_dance('T2GoogleCalendar', self.consumer_key, self.consumer_secret)
        db['oauth_token'] = self.oauth_token
        db['oauth_secret'] = self.oauth_secret
        db.close()

    def connectStream(self):
        try:
            iterator = self.twitter_stream.user()
            for tweet in iterator:
                if u'text' in tweet:
                    print tweet[u'user'][u'id'], tweet[u'text']
                    if (tweet[u'user'][u'id'] == self.cred['id'] and
                            tweet[u'text'].find('@tw2gc') >= 0):
                        event_info = self.analyzeTweet(tweet[u'text'])
                        if event_info:
                            yield event_info
        except KeyboardInterrupt:
            now = nowtime()
            with open(logfile, 'a') as f:
                f.write(now + ' KeyboardInterrupt. exit.\n')
            sys.exit()
        except socket.error as e:
            now = nowtime()
            with open(logfile, 'a') as f:
                f.write(now + ' socket.error' +
                        ('' + e.message if e.message else '') + '\n')
            yield 'error'

    def analyzeTweet(self, tweet):
        tweet_buf = tweet
        #日付
        date_mat = self.date_format.search(tweet_buf)
        if not date_mat:
            return False
        dl = []
        for d in date_mat.groups():
            if d:
                dl.append(int(d))
        date = self.pickDate(
            dl, date_mat.group()).replace(second=0, microsecond=0)
        tweet_buf = tweet_buf[:date_mat.start()] + tweet_buf[date_mat.end():]
        #開始時間
        start_mat = self.start_time_format.search(tweet_buf)
        stl = []
        if start_mat:
            for st in start_mat.groups():
                if st:
                    stl.append(int(st))
            start_time = self.pickTime(stl, date)
            if start_time:
                tweet_buf = tweet_buf[:start_mat.start()] + tweet_buf[start_mat.end():]
        else:
            start_time = None
        #終了時間
        end_mat = self.end_time_format.search(tweet_buf)
        etl = []
        if start_time and not end_mat:
            end_time = start_time + datetime.timedelta(hours=1)
        elif not start_time:
            end_time = None
        else:
            for et in end_mat.groups():
                if et:
                    etl.append(int(et))
            end_time = self.pickTime(etl, date)
            if not end_time:
                return False
            tweet_buf = tweet_buf[:end_mat.start()] + tweet_buf[end_mat.end():]
        #タイトル
        title_mat = self.title_format.search(tweet_buf)
        title = None
        if title_mat:
            title = title_mat.group(1)
            tweet_buf = (tweet_buf[:title_mat.start()] +
                         tweet_buf[title_mat.end():])
        #場所
        location_mat = self.location_format.search(tweet_buf)
        location = None
        if location_mat:
            location = location_mat.group(1) or location_mat.group(2)
            tweet_buf = (tweet_buf[:location_mat.start()] +
                         tweet_buf[location_mat.end():])
        #繰り返し
        recur_mat = self.recurring_format.search(tweet_buf)
        recurrence_freq, recurrence_count = (self.pickRecurrence(recur_mat)
                                             if recur_mat
                                             else (None, None))
        return {
            'title': title,
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S%z') if start_time else None,
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S%z') if end_time else None,
            'date': date.strftime('%Y-%m-%d') if not start_time and not end_time else None,
            'location': location,
            'recurrence': {'freq': recurrence_freq, 'count': recurrence_count}
        }

    def pickDate(self, date_ar, date_mat):
        try:
            today = datetime.datetime.now(jst)
            if not len(date_ar):
                if date_mat == u'今日':
                    return today
                elif date_mat == u'明日':
                    return today + datetime.timedelta(days=1)
                elif date_mat == u'明後日':
                    return today + datetime.timedelta(days=2)
            elif len(date_ar) == 3:
                return (today.replace(year=date_ar[0],
                                      month=date_ar[1], day=date_ar[2]))
            elif len(date_ar) == 2:
                return today.replace(month=date_ar[0], day=date_ar[1])
        except:
            return None

    def pickTime(self, time_ar, date_obj):
        try:
            if len(time_ar) == 2:
                return date_obj.replace(hour=time_ar[0], minute=time_ar[1])
            else:
                return date_obj.replace(hour=time_ar[0], minute=0)
        except:
            return None

    def pickRecurrence(self, rec_mat):
        try:
            if rec_mat.group(1) == u'毎日':
                freq = 'DAILY'
            elif rec_mat.group(1) == u'毎週':
                freq = 'WEEKLY'
            return freq, rec_mat.group(2)
        except:
            return None, None
