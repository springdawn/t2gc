import os
import dbm
import twitter


class T2gcAccount:
    oauth_keyfile_path = (os.path.abspath(os.curdir) +
                          '/t2gc_oauth')

    def __init__(self):
        oauth = {}
        if os.path.exists(self.oauth_keyfile_path + '.db'):
            db = dbm.open(self.oauth_keyfile_path)
            for key in db.keys():
                oauth[key] = db[key]
            db.close()
        else:
            db = dbm.open(self.oauth_keyfile_path, 'n')
            oauth['consumer_key'] = raw_input('input consumer_key :')
            oauth['consumer_secret'] = raw_input('input consumer_secret :')
            oauth['oauth_token'], oauth['oauth_secret'] = twitter.oauth_dance(
                'T2GoogleCalendar',
                oauth['consumer_key'], oauth['consumer_secret'])
            for key in oauth:
                db[key] = oauth[key]
            db.close()
        self.twitter = twitter.Twitter(
            auth=twitter.OAuth(
                oauth['oauth_token'], oauth['oauth_secret'],
                oauth['consumer_key'], oauth['consumer_secret']))

    def tweet(self, event_id, user_info):
        status = '@' + user_info['user'] + ' event insert ' + event_id
        self.twitter.statuses.update(status=status,
                                     in_reply_to_status_id=user_info['id'])
