import datetime
import requests

import azure.functions as func

#main triggerato dall'espressione CRON
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    send_news()

#ricerca delle notizie tramite bing search ed invio al bot su /api/notify
def send_news():
    subscription_key = ""
    search_term = "cinema"
    search_url = "https://api.bing.microsoft.com/v7.0/news/search"

    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML", "mkt": "it-IT"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    list = []
    i = 0
    for article in search_results["value"]:
        if i > 7:
            break
        list.append({
            "name": article["name"].replace('<b>', '').replace('</b>', '').replace('&quot;', '').replace('&#39;', "'"),
            "url": article["url"],
            "desc": article["description"].replace('<b>', '').replace('</b>', '').replace('&quot;', '').replace('&#39;', "'") + '...',
            "date": article["datePublished"][0:10],
            "poster_path": article["image"]["thumbnail"]["contentUrl"] if 'image' in article else ''
        })
        i += 1

    myJson = {
        "news": list
    }

    url = 'https://WebAppHalBot.azurewebsites.net/api/notify'
    headers = {'Content-Type': 'application/json'}

    requests.get(url, headers=headers, json=myJson)