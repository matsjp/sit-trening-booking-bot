import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime, timedelta


def addBooking(booking, token):
    addBookingUrl = 'https://ibooking.sit.no/webapp/api//Schedule/addBooking'
    payload = {'token': token, 'classId': booking['id']}
    requests.post(addBookingUrl, data=payload)


load_dotenv()
password = os.getenv('password')
name = os.getenv('name')
if password is None:
    print('env var password is None, exiting script')
    exit()

if name is None:
    print('env var name is None, exiting')
    exit()

logInUrl = 'https://www.sit.no/trening'
selfWorkoutUrl = 'https://www.sit.no/gjovik/trening/egentrening'
loginPayload = {'name': name, 'pass': password, 'form_id': 'user_login'}
try:
    session = requests.Session()
    session.post(logInUrl, data=loginPayload, cookies={'test': 'test'})
    if len(session.cookies.get_dict().values()) == 0:
        print("Unable to get session token, exiting")
        exit()

    selfWorkoutPage = session.get(selfWorkoutUrl)
    soup = BeautifulSoup(selfWorkoutPage.text, 'html.parser')
    ibooking_iframe = soup.find(id='ibooking-iframe')
    ibooking_token = parse_qs(urlparse.urlparse(ibooking_iframe.attrs['src']).query)['token'][0]

    getScheduleUrl = 'https://ibooking.sit.no/webapp/api/Schedule/getSchedule'
    schedulesStudio = '968'
    schedulePayload = {'token': ibooking_token, 'studios': 968}
    scheduleResponse = requests.post(getScheduleUrl, data=schedulePayload)
    schedule = scheduleResponse.json()
    bookingDay = None
    for day in schedule['days']:
        d = datetime.now() + timedelta(days=2)
        if day['date'] == (d.strftime('%Y-%m-%d')):
            bookingDay = day
            break
    if bookingDay == None:
        print('Cannot find the day in 2 days, exiting')
        exit()
    print(bookingDay['classes'])
    booking1 = None
    booking2 = None
    for singleClass in bookingDay['classes']:
        if singleClass['studio']['name'] == 'Gjøvik':
            if '20:45:00' in singleClass['from']:
                booking1 = singleClass
            elif '21:30:00' in singleClass['from']:
                booking2 = singleClass
    if booking1 is None or booking2 is None:
        print("Cannot find booking, exiting")
        exit()
    print('Booking classes')
    addBooking(booking1, ibooking_token)
    addBooking(booking2, ibooking_token)


except Exception as e:
    print(e)
    exit()