
import time
import threading
import requests
import os
import json
from bs4 import BeautifulSoup

baseurl = "https://aznchecker.herokuapp.com/"

thresholds = []
curr_prices = []
URLs = []
checked = []
token = "EAAZAIR80GOG0BAMgzM7l6W2PAvWOdee6vQZAe8CKM2kxlB6gPApRB2qGsQTj1YlZAeNTVunZCkdeuzr1pNAlKYI51SVfExZBGm8Tw5CIPTCpZBaXrdoR0D1vyI5ivXMo97GuRBHcs36zdilY9S21ph75JH4d86tzkZCRug7Qbsf8yjJUvJpkhA9"

# get new items from new_list file
# add to database
def getNewItems(id):
    isURL = True
    url = ""
    threshold = ""

    r = requests.get(baseurl+id)
    arr = r.text.split("\n")
    arr = arr[:-1]

    for line in arr:
        if(isURL):
            url = line
            isURL = False
        else:
            threshold = line
            isURL = True
            URLs.append(url)
            thresholds.append(threshold)
            checked.append(0)
            curr_prices.append(0)
            new_watch_thread = threading.Thread(target=watchItem, args=(url, threshold, id))
            new_watch_thread.start()


# check current price of certain item given url
def checkPrice(url):
    r = requests.get(url)
    html_proc = BeautifulSoup(r.text, "lxml")
    span = html_proc.find("span", {"id": "priceblock_ourprice"})
    curr_price = float(span.text[1:])

    return curr_price


# print current watchlist
def printWatchlist():
    print("Current Watchlist: ")
    for i in range(len(URLs)):
        if(checked[i] == 1):
            print("Item link: " + URLs[i] + "\nThreshold price: " + thresholds[i] + "\nCurrent Price: " + str(curr_prices[i]) + "")
    print("\n")


# watch item until price is lower than threshold
# delete item data from databases if below threshold
def watchItem(url, threshold, id):
    index = URLs.index(url)
    curr_prices[index] = checkPrice(url)
    checked[index] = 1

    while curr_prices[index] > float(threshold):
        print(str(curr_prices[index]) + " " + threshold)
        curr_prices[index] = checkPrice(url)
        time.sleep(5)
    send_message(id, url)
    del URLs[index]
    del thresholds[index]


#sends message through graph facebook api
def send_message(recipient, url):
    text = "Hi, this item you were looking at is now below the price you wanted to buy it at! Here's the link to the item: " + url
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token}, data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text}
    }), headers={'Content-type': 'application/json'})


# check "new_list" file size (5 second intervals)
# if nonzero read in new URLs/threshold prices
def start(id):
    while(1):
        if(os.stat("new_list").st_size != 0):
            getNewItems(id)
        printWatchlist()
        time.sleep(5)

# testing
def main():
    id = "2023220174360192"
    main_thread = threading.Thread(target=start, args=(id,))
    main_thread.start()


if __name__ == "__main__":
    main()

