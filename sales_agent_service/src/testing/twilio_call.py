# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure


# TWILIO_ACCOUNT_SID="AC27ce5804db2a7a27466731bd08727e53"
# TWILIO_AUTH_TOKEN="bc4608f3a89ba2a0e4e2b0f4bb393cf1"


account_sid = "AC27ce5804db2a7a27466731bd08727e53"
auth_token = "bc4608f3a89ba2a0e4e2b0f4bb393cf1"

client = Client(account_sid, auth_token)

call = client.calls.create(
    url="http://demo.twilio.com/docs/classic.mp3",
    to="+92 320 0435945",
    from_="+1 814 250 4572",
)

print(call.sid)







