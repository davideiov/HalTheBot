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

class SearchFilmDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(SearchFilmDialog, self).__init__(SearchFilmDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.search_film_step,
                    self.show_result_step,
                    self.options_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def search_film_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci il titolo del film che vuoi cercare")),
        )

    async def show_result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        film = step_context.result
        list_movie = self.searchMovie(film)
        if len(list_movie) == 0:
            await step_context.context.send_activity(MessageFactory.text("Non è presente nessun film per la tua ricerca, prova ad essere più preciso\n ritorno al menu principale"))
            return await step_context.end_dialog()

        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel

        for i in range(len(list_movie)):
            if type(list_movie[i]["poster_path"]) is str:
                card = self.create_hero_card_with_image(list_movie[i])
            else:
                card = self.create_hero_card_without_image(list_movie[i])
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

    #ricerca di film dato il titolo attraverso TMDB
    def searchMovie(self, film):
        query = 'https://api.themoviedb.org/3/search/movie?api_key={CONFIG.TMDB_KEY}&language=it-IT&page=1&query=' + film
        result = requests.get(query).json()
        list = []

        i = 0
        for film in result['results']:
            if i > 4:
                break
            list.append(film)
            i+=1
        
        return list


    def searchTrailer(self, film):
        query = f'https://api.themoviedb.org/3/movie/{film}/videos?api_key={CONFIG.TMDB_KEY}&language=it-IT'
        result = requests.get(query).json()

        try:
            url = "https://www.youtube.com/watch?v=" + str(result["results"][0]["key"])
        except:
            url = "Not found"

        return url


    def create_hero_card_with_image(self, movie) -> Attachment:
        card = HeroCard(
            title = movie["title"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = movie["release_date"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.') if "release_date" in movie else '',
            text = movie["overview"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            images = [
                CardImage(
                    url = "https://image.tmdb.org/t/p/original/" + str(movie["poster_path"])
                )
            ],
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Aggiungi alla watchlist",
                    value = "watchlist " + str(movie["id"]),
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
            title = movie["title"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = movie["release_date"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.') if "release_date" in movie else '',
            text = movie["overview"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            buttons=[
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Aggiungi alla watchlist",
                    value = "watchlist " + str(movie["id"]),
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Guarda il trailer",
                    value = "trailer " + str(movie["id"]),
                )
            ],
        )
        return CardFactory.hero_card(card)