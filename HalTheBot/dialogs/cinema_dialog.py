from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.schema import (
    HeroCard,
    Attachment,
    AttachmentLayoutTypes,
    CardAction,
    ActionTypes
)
from botbuilder.core import MessageFactory, UserState, CardFactory
from config import DefaultConfig

import requests

CONFIG = DefaultConfig()

#Dialog che permette la ricerca di cinema data una località
class CinemaDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(CinemaDialog, self).__init__(CinemaDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.location_step,
                    self.options_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def location_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci la città per scoprire se ci sono dei Cinema")),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result
        cinemas = self.searchCinemas(option)

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.list

        for cinema in cinemas:

            try:
                address = cinema["address"]["freeformAddress"]
            except:
                address = ""

            try:
                tel = cinema["poi"]["tel"]
            except:
                tel = ""

            try:
                url = cinema["poi"]["url"]
            except:
                url = ""

            try:
                name = cinema["poi"]["name"]
            except:
                name = "Cinema non disponibile"

            card = self.create_hero_card(
                name,
                address,
                tel,
                url
            )
            reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.end_dialog()

    def create_hero_card(self, name, address, tel, url) -> Attachment:
        card = HeroCard(
            title = name.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = tel.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.') + '    ' + url.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            text = 'Indirizzo: ' + address.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            buttons=[
                CardAction(
                    type = ActionTypes.open_url,
                    title = "Apri in Google Maps",
                    value = 'https://www.google.com/maps/dir/?api=1&destination=' + str(name).replace(' ','+') + '+' + str(address).replace(' ','+')
                )]
        )
        return CardFactory.hero_card(card)

    #metodo per la ricerca di cinema data una località tramite Azure Maps
    def searchCinemas(self, locality):
        url = f'https://atlas.microsoft.com/search/fuzzy/json?api-version=1.0&query=cinema%20in%20{locality}&subscription-key={CONFIG.MAPS_KEY}&language=it-IT&countrySet=IT'
        response = requests.get(url).json()

        return response["results"]