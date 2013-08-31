# This Python file uses the following encoding: utf-8
import os
import dbm
import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

from ns import *


class GoogleCalendar():

    def __init__(self):

        oauth_keyfile_path = (os.path.dirname(os.path.abspath(__file__)) +
                              '/google_oauth')
        FLAGS = gflags.FLAGS

        if os.path.exists(oauth_keyfile_path + '.db'):
            db = dbm.open(oauth_keyfile_path)
            client_id = db['client_id']
            client_secret = db['client_secret']
            developer_key = db['developer_key']
        else:
            print 'create Google OAuth file...'
            db = dbm.open(oauth_keyfile_path, 'n')
            client_id = raw_input('input client_id :')
            client_secret = raw_input('input client_secret :')
            developer_key = raw_input('input developer key :')
            db['client_id'] = client_id
            db['client_secret'] = client_secret
            db['developer_key'] = developer_key
        db.close()

        # Set up a Flow object to be used if we need to authenticate. This
        # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
        # the information it needs to authenticate. Note that it is called
        # the Web Server Flow, but it can also handle the flow for native
        # applications
        # The client_id and client_secret are copied from the API Access tab on
        # the Google APIs Console
        self.FLOW = OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope='https://www.googleapis.com/auth/calendar',
            user_agent='twitter2calnedar/1.0')

        # To disable the local server feature, uncomment the following line:
        FLAGS.auth_local_webserver = False

        # If the Credentials don't exist or are invalid,
        # run through the native client flow.
        # The Storage object will ensure that if successful the good
        # Credentials will get written back to a file.
        self.storage = Storage('calendar.dat')
        self.credentials = self.storage.get()
        if self.credentials is None or self.credentials.invalid is True:
            self.credentials = run(self.FLOW, self.storage)

        # Create an httplib2.Http object to handle our HTTP requests
        # and authorize it with our good Credentials.
        http = httplib2.Http()
        http = self.credentials.authorize(http)

        # Build a service object for interacting with the API. Visit
        # the Google APIs Console
        # to get a developerKey for your own application.
        self.service = build(
            serviceName='calendar', version='v3', http=http,
            developerKey=developer_key)

    def connect(self):
        print 'OK' if self.service else 'BAD'
        dbfile_path = os.path.dirname(os.path.abspath(__file__)) + '/gc'
        if os.path.exists(dbfile_path + '.db'):
            db = dbm.open(dbfile_path)
            self.calendar_id = db['id']
            print self.calendar_id
            cal = (self.service.calendars()
                   .get(calendarId=self.calendar_id).execute())
            print cal['summary']
        else:
            print 'process create'
            self.createCalendar()
        raw_input('continue...')

    def createCalendar(self):
        calendar = {
            'summary': 'Twitter2GoogleCalendar',
            'timeZone': timezone
        }
        created_calendar = (self.service.calendars()
                            .insert(body=calendar).execute())
        print created_calendar['id'], created_calendar['timeZone']
        dbfile_path = os.path.dirname(os.path.abspath(__file__)) + '/gc'
        db = dbm.open(dbfile_path, 'n')
        db['id'] = created_calendar['id']

    def createEvent(self, event_info):
        event = {
            'summary': event_info['title'],
            'location': event_info['location'],
            'start': {
                'dateTime': (event_info['start']
                             if 'start' in event_info else None),
                'date': event_info['date'] if 'date' in event_info else None,
                'timeZone': timezone
            },
            'end': {
                'dateTime': event_info['end'] if 'end' in event_info else None,
                'date': event_info['date'] if 'date' in event_info else None,
                'timeZone': timezone
            },
        }
        if (event_info['recurrence']['freq'] and
                event_info['recurrence']['count']):
            recurrence = ('RRULE:FREQ=' + event_info['recurrence']['freq'] +
                          ';COUNT=' + event_info['recurrence']['count'])
            event['recurrence'] = [recurrence]

        try:
            created_event = (self.service.events()
                             .insert(calendarId=self.calendar_id, body=event)
                             .execute())

            print created_event['id']
            print event
            return created_event['id']
        except Exception:
            print 'error: event insertion'
            self.credentials.refresh(httplib2.Http())
            return False
