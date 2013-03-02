CellCius
========

CellCius is an automatic balance checking and low-balance notification tool 
for the Cell-C mobile network in South Africa.

Receive email warnings when one of your balances (Voice Minutes, Data MB or 
SMSes) drops below configurable thresholds.

The script can make use of either gmail or a local MTA to send the 
warning emails.

View settings.py for more info on configuring.


WHY? 
----
Because knowledge is power.

Having this running in the background means that I never run out of airtime at 
an awkward momement, or end up without data needed to buy more data.

Also, not receiving warnings means that once your data bundle is up, you'll 
chew through your remaining "airtime" at 99c per mb instead of the 
in-bundle 15c.

Shouldn't Cell-C be sending these kinds of alerts? YES!


INSTALLATION:
------------
* Setup your Cell-C "My Account" at https://www.cellc.co.za/my-account
* Copy settings.py.sample to settings.py, configure accordingly and then 
run "python cellcius.py".
* You'll then need to set it up to run via cron (or something). I 
suggest running it hourly.


Dependencies:
* requests (pip install requests)
* lxml (apt-get install python-lxml)


HOW DOES IT WORK?
-----------------
The script jumps through some hurdles to complete the single sign on, then
calls a page that returns some badly formatted (unstructured) text, which is 
then parsed using regex. 

It is highly likely that Cell-C will change something and break this.

The script writes a datetime to /tmp/cellcius_last_sent.txt to keep track of 
when it last sent email.

ps. Pull requests welcome.
