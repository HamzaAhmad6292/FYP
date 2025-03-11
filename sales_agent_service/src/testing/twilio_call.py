# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure


# client = Client(account_sid, auth_token)

call = client.calls.create(
    url="http://demo.twilio.com/docs/classic.mp3",
    to="+92 320 0435945",
    from_="+1 814 250 4572",
)

print(call.sid)







