cellcius
========

CellCius is an automatic balance checking tool for the Cell-C mobile network in 
South Africa

Receive emails warning you when your one of your balances (Voice Minutes, 
Data MB or SMSes) drops below configurable thresholds.

View settings.py for more info on configuring

Why did I write this? 
Because it annoys me that an MNO doesn't send warnings for this kind thing. 
Not receiving warnings means that once your data bundle is up, you'll 
chew through your remaining "airtime" at 99c per mb instead of the 
in-bundle 15c.

It's also very annoying running out of airtime during an important call.

The script makes use of gmail to send warning emails so you'll need to 
configure that below.

Setup your "My Account" at https://www.cellc.co.za/my-account

You'll need to set this up on with cron (or whatever).
