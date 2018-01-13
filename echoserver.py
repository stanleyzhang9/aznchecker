# -*- coding: utf-8 -*-
from flask import Flask, request
import json
import requests

app = Flask(__name__)

PAT = 'EAAZAIR80GOG0BAMgzM7l6W2PAvWOdee6vQZAe8CKM2kxlB6gPApRB2qGsQTj1YlZAeNTVunZCkdeuzr1pNAlKYI51SVfExZBGm8Tw5CIPTCpZBaXrdoR0D1vyI5ivXMo97GuRBHcs36zdilY9S21ph75JH4d86tzkZCRug7Qbsf8yjJUvJpkhA9'

@app.route('/', methods=['GET'])
def handle_verification():
  print ("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print ("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print ("Verification failed!")
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print ("Handling Messages")
  payload = request.get_data()
  print (payload)
  for sender, message in messaging_events(payload):
    x = message.decode("utf-8").split(",")
    if (len(x) == 2): 
      fh = open('new_list', "a")
      fh.write(x[0]+'\n')
      fh.write(x[1]+'\n')
      print(x[0] + '\n' + x[1] + '\n')
      fh.close()
      send_message(PAT, sender, 'I have added the item ' + x[0] + ' for the maximum price of ' + x[1])
  return "ok"

@app.route('/new_list')
def update():
  fh = open('new_list', "a")
  fh.write('')
  fh.close()
  file = open('new_list','r');
  str = ''
  for line in file:
     str += line + '\n'
  file.close()
  return str

def messaging_events(payload):
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


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

if __name__ == '__main__':
  app.run()
