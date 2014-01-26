CellCius
========

CellCius is an automatic balance checking and low-balance notification tool
for the Cell-C mobile network in South Africa.

Receive email warnings when one of your balances (Voice Minutes, Data MB or
SMSes) drops below configurable thresholds.

The script can make use of either gmail or a local MTA to send the
warning emails. You can configure how frequently you want to receive the
warning emails (ie. Every 5 hours) in the settings file.

View settings.py for more info on configuring.

CellCius is a robust, retrying (with exponential backoff), long running
process.


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
* Copy settings.py.sample to settings.py and configure accordingly.
* Run "python cellcius.py" to confirm it's running correctly.
* Run it inside a Screen session or get fancy with startupd etc.


Dependencies:
Use VirtualEnv and `pip install -r requirements.txt`

* requests (HTTP for Humans)
* lxml (for parsing HTML)
* retrying (Elegant retrying with exponential backoffs)


HOW DOES IT WORK?
-----------------
The script jumps through some hurdles to complete the single sign on, then
calls a page that returns some badly formatted (unstructured) text, which is
then parsed using regex.

It keeps the session open so you'll only receive an SMS from Cell C confirming
your login when the application first starts up, CellCius then
polls the site (using the existing session) every 9 minutes.

If the sesssion dies (ie. Cell-C reboot their servers?) it will detect the
lost session and recreate it, at which point you will receive another SMS from
the Cell-C site.

It is highly likely that Cell-C will change something and break this.

The script writes a datetime to /tmp/cellcius_last_sent.txt to keep track of
when it last sent email.

ps. Pull requests welcome.
