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
    CardImage,
    Attachment,
    CardAction,
    ActionTypes,
    AttachmentLayoutTypes
)
from botbuilder.core import MessageFactory, UserState, CardFactory
from data_models.dao import UserDAO
from config import DefaultConfig
import requests

CONFIG = DefaultConfig()

class UpcomingDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(UpcomingDialog, self).__init__(UpcomingDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.show_step,
                    self.options_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        movies = self.upcomingFilms()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel

        for film in movies:
            if type(film["poster_path"]) is str:
                card = self.create_hero_card_with_image(film)
            else:
                card = self.create_hero_card_without_image(film)
            reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Per tornare al menu principale digita esci")),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result

        if option.__contains__("watchlist"):
            film = option[10:]
            user = UserDAO.searchUserById(step_context.context.activity.from_property.id)
            user.watchlist.append(film)
            UserDAO.updateUserById(user)

            await step_context.context.send_activity("Film aggiunto correttamente alla watchlist")
            return await step_context.end_dialog()

        elif option.__contains__("trailer"):
            id = option[8:]
            url = self.searchTrailer(id)

            if url == "Not found":
                await step_context.context.send_activity(MessageFactory.text('Non è disponibile nessun trailer per questo film'))
                return await step_context.end_dialog()
            else:
                card = HeroCard(
                    title="",
                    buttons=[
                        CardAction(
                            type = ActionTypes.play_video,
                            title = "Apri con youtube",
                            value = url,
                        )
                    ]
                )
                hero_card = CardFactory.hero_card(card)
                await step_context.context.send_activity(MessageFactory.attachment(hero_card))
                return await step_context.end_dialog()
        
        elif option.lower().__contains__("esci"):
            return await step_context.end_dialog()
            

    def create_hero_card_with_image(self, movie) -> Attachment:
        card = HeroCard(
            title = movie["title"],
            subtitle = movie["release_date"],
            text = movie["overview"],
            images = [
                CardImage(
                    url = "https://image.tmdb.org/t/p/original/" + str(movie["poster_path"])
                )
            ],
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Aggiungi alla watchlist",
                    value = "watchlist " + str(movie["id"])
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Guarda il trailer",
                    value = "trailer " + str(movie["id"]),
                )
            ],
        )
        return CardFactory.hero_card(card)

    def create_hero_card_without_image(self, movie) -> Attachment:
        card = HeroCard(
            title = movie["title"],
            subtitle = movie["release_date"].replace('-','\\-'),
            text = movie["overview"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Aggiungi alla watchlist",
                    value = "watchlist " + str(movie["id"])
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Guarda il trailer",
                    value = "trailer " + str(movie["id"]),
                )
            ],
        )
        return CardFactory.hero_card(card)

    #ricerca film in uscita tramite TMDB
    def upcomingFilms(self):
        query = 'https://api.themoviedb.org/3/movie/upcoming?api_key={CONFIG.TMDB_KEY}&language=it-IT&region=IT'
        result = requests.get(query).json()
        return result["results"]

    def searchTrailer(self, film):
        query = f'https://api.themoviedb.org/3/movie/{film}/videos?api_key={CONFIG.TMDB_KEY}&language=it-IT'
        result = requests.get(query).json()

        try:
            url = "https://www.youtube.com/watch?v=" + str(result["results"][0]["key"])
        except:
            url = "Not found"

        return url

        