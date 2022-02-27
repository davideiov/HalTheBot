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
import random

CONFIG = DefaultConfig()

json_genres = {
    "genres": [
        {
        "id": 28,
        "name": "Azione"
        },
        {
        "id": 12,
        "name": "Avventura"
        },
        {
        "id": 16,
        "name": "Animazione"
        },
        {
        "id": 35,
        "name": "Commedia"
        },
        {
        "id": 80,
        "name": "Crime"
        },
        {
        "id": 99,
        "name": "Documentario"
        },
        {
        "id": 18,
        "name": "Dramma"
        },
        {
        "id": 10751,
        "name": "Famiglia"
        },
        {
        "id": 14,
        "name": "Fantasy"
        },
        {
        "id": 36,
        "name": "Storia"
        },
        {
        "id": 27,
        "name": "Horror"
        },
        {
        "id": 10402,
        "name": "Musica"
        },
        {
        "id": 9648,
        "name": "Mistero"
        },
        {
        "id": 10749,
        "name": "Romance"
        },
        {
        "id": 878,
        "name": "Fantascienza"
        },
        {
        "id": 10770,
        "name": "televisione film"
        },
        {
        "id": 53,
        "name": "Thriller"
        },
        {
        "id": 10752,
        "name": "Guerra"
        },
        {
        "id": 37,
        "name": "Western"
        }
    ]
}

class ReccomendationDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(ReccomendationDialog, self).__init__(ReccomendationDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                "WFReccomendation",
                [
                    self.show_step,
                    self.options_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = "WFReccomendation"

    async def show_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #recupero generi preferiti dell'utente
        self.user = UserDAO.searchUserById(step_context.context.activity.from_property.id)
        genres_id = []

        for genre in self.user.fav_genres:
            for json_genre in json_genres["genres"]:
                if genre == json_genre["name"]:
                    genres_id.append(json_genre["id"])
        #ricerca per genere
        movies = self.searchFilmsByGenres(genres_id)
        
        reply = MessageFactory.list([])
        reply.attachment_layout = AttachmentLayoutTypes.carousel

        for i in range(4):
            num = random.randrange(0, len(movies))
            card = self.create_hero_card(movies[num])
            reply.attachments.append(card)

        await step_context.context.send_activity(reply)
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Per il suggerimento di altri film digita shuffle, mentre per tornare al menu principale digita esci")),
        )

    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result

        if option.__contains__("watchlist"):
            film = option[10:]
            self.user.watchlist.append(film)
            UserDAO.updateUserById(self.user)

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

        elif option.lower().__contains__("shuffle"):
            return await step_context.replace_dialog("WFReccomendation")

        elif option.lower().__contains__("esci"):
            return await step_context.end_dialog()

    def create_hero_card(self, movie) -> Attachment:
        card = HeroCard(
            title = movie["title"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
            subtitle = movie["release_date"].replace('(','\\(').replace(')','\\)').replace('-','\\-').replace('.','\\.'),
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

    #ricerca di film dato un genere attraverso TMDB
    def searchFilmsByGenres(self, genres):
        id_genre = genres[random.randrange(0,len(genres))]

        query = f'https://api.themoviedb.org/3/discover/movie?api_key={CONFIG.TMDB_KEY}&language=it-IT&region=IT&sort_by=popularity.desc&with_genres={id_genre}'
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

        