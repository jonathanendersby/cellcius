"""CellCius is an automatic balance checking tool for the Cell-C mobile network
in South Africa. 

The script makes use of gmail to send warning emails so you'll need to 
configure that below.

Setup your "My Account" at https://www.cellc.co.za/my-account

You'll need to set this up on with cron (or whatever).
"""
# Don't output anything unless something goes wrong.
quiet = True 

# Must either be "localhost" or "gmail"
send_email_via = "gmail" 

# If send_email_via is "gmail" this must be a gmail (or google apps) address
send_from = "foo@gmail.com" 

# If send_email_via is "gmail" then you need to provide your password. 
gmail_password = "foobar"

# Which address to send the warning to.
send_to = "foo@gmail.com" 

# Your MSISDN in the format 0841234567
msisdn = '0841234567'

# Your https://www.cell.co.za/my-account password
# Be careful with this because they lock you out for an hour after 3 incorrects.
cellc_password = 'supersecret' 

# Below these numbers you will receive an email. None means you don't care.
threshold_sms = None
threshold_voice = 40 # minutes
threshold_data = 500 # megabytes

# How many hours between warning emails.
send_email_every = 2 
