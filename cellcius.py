"""CellCius is an automatic balance checking tool for the Cell-C mobile network
in South Africa.

View README.md and settings.py(.sample) for more info on configuration.

"""

import requests
import re
from lxml.html import fromstring
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import time
import sys
import settings
from datetime import datetime
from retrying import retry


sso_url = 'https://sso.cellc.co.za/ca/loginbox.do?service=https%3A%2F%2Fecare.cellc.co.za%2Fecare&continue=%2Flogin%2Fverification%2F&loginType=CT'
post_url = 'https://sso.cellc.co.za/ca/POST.do'
post_url2 = 'https://ecare.cellc.co.za/ecare/post.do'
stats_url = 'https://ecare.cellc.co.za/ecare/common/landingPage.do?method=getAjaxUsageTraffic'
rand_balance_url = 'https://ecare.cellc.co.za/ecare/mycellc/mobile/invoice/balance/'



@retry(wait='exponential_sleep', wait_exponential_multiplier=1000, wait_exponential_max=1000000)
def session_setup():
    if not settings.quiet:
        print 'Setting Up Session'

    inline_session = requests.session()
    r = inline_session.get(sso_url)

    doc = fromstring(r.text)
    for val in doc.xpath("//input[@name='SAMLRequest']/@value"):
        saml = val

    post_data = {'mobile': settings.msisdn,
            'password': settings.cellc_password,
            'loginType': 'CT',
            'RelayState': '/login/verification/',
            'SAMLRequest': saml}

    r = inline_session.post(post_url, post_data)

    doc = fromstring(r.text)
    samlart = None
    for val in doc.xpath("//input[@name='SAMLart']/@value"):
        samlart = val

    if not samlart:
        error = ""
        for val in doc.xpath("//p[@class='errormessage']"):
            error = val.text

        sys.exit("Authentication Failed - Reason Given: " + error)

    post2_data = {'loginType': 'CT',
                  'RelayState': '/login/verification/',
                  'SAMLart': samlart}

    inline_session.post(post_url2, post2_data)

    if not settings.quiet:
        print 'Logged In'

    return inline_session

@retry(wait='exponential_sleep', wait_exponential_multiplier=1000, wait_exponential_max=1000000)
def check_balance(session):

    if not settings.quiet:
        print 'Checking Balance'

    stats_response = session.get(stats_url)
    summary = " ".join(stats_response.text.split())

    # Check the Session is still active
    if "Inclusive voice minutes remaining" not in summary:
        # Session has died, recreate it.

        if not settings.quiet:
            print 'Session is no longer active, recreating'

        session = session_setup()

        # Redo the two lines that were done on the inactive session.
        stats_response = session.get(stats_url)
        summary = " ".join(stats_response.text.split())

    response = session.get(rand_balance_url)
    summary2 = " ".join(response.text.split())

    data = re.match(".*Inclusive data remaining: (.*?)&nbsp;.*", summary)
    sms = re.match(".*Inclusive SMS's remaining: (.*?)&nbsp;.*", summary)
    voice = re.match(".*voice minutes remaining:&nbsp; (.*?)&nbsp;.*", summary)
    rand_balance = re.match('''.*\<th\>Balance\:\<\/th\> \<td\>R(.*?)\<\/td\>.*''', summary2)

    if data:
        data = float(data.groups()[0])

    if sms:
        sms = float(sms.groups()[0])

    if voice:
        voice = float(voice.groups()[0])
    else:
        voice = 0

    if rand_balance:
        rand_balance = float(rand_balance.groups()[0])
    else:
        rand_balance = 0

    combined_voice = int(voice + (rand_balance/settings.cellc_voice_per_minute))

    if not settings.quiet:
        print "Data: " + str(data) + ' mb'
        print "SMS: " + str(sms)
        print "Voice: " + str(voice) + ' minutes'
        print "Balance: R" + str(rand_balance)
        print "Combined Voice: " + str(combined_voice) + " minutes"

    ### SENDING EMAIL

    if ((settings.threshold_sms and sms < settings.threshold_sms) or \
        (settings.threshold_data and data < settings.threshold_data) or \
        (settings.threshold_voice and combined_voice < settings.threshold_voice)):
        if not settings.quiet:
            print "Under Threshold"

        try:
            last_sent = open('/tmp/cellcius_last_sent.txt','r')
            y = last_sent.read().strip()
            last_sent.close()
            last_date = datetime.strptime(y, '%Y-%m-%d %H:%M:%S.%f')
            delta = datetime.now() - last_date
            no_last = False
        except IOError:
            no_last = True

        # The +5 on the following line is to make up for oddities with the
        # service running every hour but not having an hour pass according
        # to the delta.
        if no_last or ((delta.seconds / 60)+5 >= settings.send_email_every * 60):
            if not settings.quiet:
                print 'Sending Warning Email'

            msg = MIMEMultipart()
            msg['From'] = settings.send_from
            msg['To'] = settings.send_to
            msg['Subject'] = 'Cell-C balance warning for ' + settings.msisdn

            body = ("Voice: %s Minutes (%s)\nData: %s MB (%s)\nSMSes: %s (%s)\n\n\nFor MSISDN: %s\nThreshold shown in brackets. Voice is a combined total of %s minutes and R%s." % (combined_voice, settings.threshold_voice, data, settings.threshold_data, sms, settings.threshold_sms, settings.msisdn, voice, rand_balance))

            msg.attach(MIMEText(body))

            if settings.send_email_via == "localhost":
                smtp = smtplib.SMTP('localhost')
                smtp.sendmail(settings.send_from, [settings.send_to], msg.as_string())
                smtp.quit()

            else:
                smtp = smtplib.SMTP("smtp.gmail.com", 587)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.gmail_username, settings.gmail_password)
                smtp.sendmail(settings.send_from, [settings.send_to], msg.as_string())
                smtp.close()

            last_sent = open('/tmp/cellcius_last_sent.txt','w')
            last_sent.write(str(datetime.now()))
            last_sent.close()

        else:
            if not settings.quiet:
                print 'Skipping email because it has only been %s minutes since we sent the last one. Currently set to %s hours.' % (delta.seconds/60, settings.send_email_every)
    else:
        if not settings.quiet:
            print "Nothing under threshold"


session = None
sleeping = False

while True:
    if not session:
        session = session_setup()

    if not settings.quiet and sleeping:
        print "Waking Up"

    check_balance(session)

    # pwn the session
    #session = requests.session()

    if not settings.quiet:
        print 'Sleeping for 9 minutes\n'

    time.sleep(9*60)
    sleeping = True



