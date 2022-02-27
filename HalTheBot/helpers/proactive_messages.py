from botbuilder.core import TurnContext, MessageFactory, CardFactory
from botbuilder.schema import AttachmentLayoutTypes, ActionTypes, Attachment, HeroCard, CardAction, CardImage
from botbuilder.dialogs import Dialog

from typing import Any, Callable

#schema dell'oggetto json ricevuto dalla function app
class ProactiveRequest:
    def __init__(self, body: dict) -> None: 

        self.name = body["name"]
        self.url = body["url"]
        self.description = body["desc"]
        self.image = body["poster_path"]
        self.date = body["date"]

#parsing (json -> obj) della lista di news e creazione di una list per la chat
def parse_proactive_message(body: Any) -> Callable:

    reply = MessageFactory.list([])
    reply.attachment_layout = AttachmentLayoutTypes.carousel

    for article in body["news"]:
        single_news = ProactiveRequest(article)
        if single_news.image != '':
            card = create_hero_card_with_image(single_news)
        else:
            card = create_hero_card_without_image(single_news)
        reply.attachments.append(card)
    
    return send_news(reply)
    
#ritorna una funzione (di callback) a _send_procative_messages (app.py)
def send_news(reply):
    
    async def func(turn_context: TurnContext):
        await turn_context.send_activity(reply)
    
    return func

def create_hero_card_with_image(news: ProactiveRequest) -> Attachment:
        card = HeroCard(
            title = news.name.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.').replace('"','\\"'),
            subtitle = news.date.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.').replace('"','\\"'),
            text = news.description.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.').replace('"','\\"'),
            images = [
                CardImage(
                    url = news.image
                )
            ],
            buttons=[
                CardAction(
                    type = ActionTypes.open_url,
                    title = "Continua a leggere",
                    value = news.url
                ),
            ],
        )
        return CardFactory.hero_card(card)

def create_hero_card_without_image(news: ProactiveRequest) -> Attachment:
        card = HeroCard(
            title = news.name.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = news.date.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            text = news.description.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            buttons=[
                CardAction(
                    type = ActionTypes.open_url,
                    title = "Continua a leggere",
                    value = news.url
                ),
            ],
        )
        return CardFactory.hero_card(card)