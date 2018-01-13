# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import os
import requests
import threading
import price_check

app = Flask(__name__)

visited = []

PAT = 'EAAZAIR80GOG0BAMgzM7l6W2PAvWOdee6vQZAe8CKM2kxlB6gPApRB2qGsQTj1YlZAeNTVunZCkdeuzr1pNAlKYI51SVfExZBGm8Tw5CIPTCpZBaXrdoR0D1vyI5ivXMo97GuRBHcs36zdilY9S21ph75JH4d86tzkZCRug7Qbsf8yjJUvJpkhA9'

# facebook webhook verification
@app.route('/', methods=['GET'])
def handle_verification():
  print ("verifying")
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print ("verify succ")
    return request.args.get('hub.challenge', '')
  else:
    print ("verify fail")
    return 'verify token fail'

# when receiving message
@app.route('/', methods=['POST'])
def handle_messages():
  print ("Handling Messages")
  payload = request.get_data()
  print (payload)
  for sender, message in messaging_events(payload):
    # write to file to be handled by seperate script
    x = message.decode("utf-8").split(",")
    if (len(x) == 2): 
      fh = open(sender, "a")
      fh.write(x[0]+'\n')
      fh.write(x[1]+'\n')
      print(x[0] + '\n' + x[1] + '\n')
      fh.close()
      print(sender)
      send_message(PAT, sender, 'I have added the item ' + x[0] + ' for the maximum price of ' + x[1])
      if sender not in visited:
        visited.append(sender)
        threading.Thread(target=price_check.start, args=(sender,)).start()     
  return "sent"

# html to be scraped by script
@app.route('/<id>')
def update(id):
  fh = open(id, "a")
  fh.write('')
  fh.close()
  file = open(id,'r');
  str = ''
  for line in file:
     str += line
  file.close()
  return str

def delete_file(id):
  fh = open(id, "w")
  os.remove(fh)

# handles messaging events
def messaging_events(payload):
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"

# sends message through graph facebook api
def send_message(token, recipient, text):

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print (r.text)

# initializing
if __name__ == '__main__':
  app.run()
