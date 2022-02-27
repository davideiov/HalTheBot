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

class WatchlistDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(WatchlistDialog, self).__init__(WatchlistDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.show_watchlist_step,
                    self.final_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def show_watchlist_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.user = UserDAO.searchUserById(step_context.context.activity.from_property.id)
        watchlist = self.user.watchlist
        if len(watchlist) == 0:
            await step_context.context.send_activity(MessageFactory.text("Non hai film nella watchlist, ritorno al menu principale"))
            return await step_context.end_dialog()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.list

        for film_id in watchlist:
            film = self.searchFilmById(film_id)
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

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result
        if option.__contains__("info"):
            option = option[5:]
            movie = self.searchFilmById(option)
            card = HeroCard(
                title = movie["title"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
                subtitle = str(movie["release_date"]).replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.') + "  " + str(movie["tagline"]).replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
                text = movie["overview"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
                images = [
                    CardImage(
                        url = "https://image.tmdb.org/t/p/original/" + str(movie["poster_path"])
                    )
                ] if type(movie["poster_path"]) is str else []
            )
            hero_card = CardFactory.hero_card(card)
            await step_context.context.send_activity(MessageFactory.attachment(hero_card))
            return await step_context.end_dialog()


        elif option.__contains__("remove"):
            option = option[7:]
            self.user.watchlist.remove(option)
            UserDAO.updateUserById(self.user)
            await step_context.context.send_activity(MessageFactory.text("Film rimosso correttamente, ritorno al menu principale"))
            return await step_context.end_dialog()

        elif option.lower().__contains__("esci"):
            return await step_context.end_dialog()
            

    def create_hero_card_with_image(self, movie) -> Attachment:
        film_name = movie["title"]

        card = HeroCard(
            title = film_name.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = movie["release_date"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            images = [
                CardImage(
                    url = "https://image.tmdb.org/t/p/original/" + str(movie["poster_path"])
                )
            ],
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Vai alla scheda del film",
                    value = "info " + str(movie["id"])
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Rimuovi dalla watchlist",
                    value = "remove " + str(movie["id"])
                ),
            ],
        )
        return CardFactory.hero_card(card)

    def create_hero_card_without_image(self, movie) -> Attachment:
        film_name = movie["title"]

        card = HeroCard(
            title = film_name.replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = movie["release_date"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Vai alla scheda del film",
                    value = "info " + str(movie["id"])
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Rimuovi dalla watchlist",
                    value = "remove " + str(movie["id"])
                ),
            ],
        )
        return CardFactory.hero_card(card)

    #ricerca film tramite TMDB
    def searchFilmById(self, id):
        query = f'https://api.themoviedb.org/3/movie/{id}?api_key={CONFIG.TMDB_KEY}&language=it-IT'
        result = requests.get(query).json()
        return result

        