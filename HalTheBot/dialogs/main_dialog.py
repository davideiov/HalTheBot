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
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)
from botbuilder.core import MessageFactory, UserState, CardFactory

from helpers.luis_helper import LuisHelper, Intent
from .user_profile_dialog import UserProfileDialog
from .search_film_dialog import SearchFilmDialog
from .watchlist_dialog import WatchlistDialog
from .upcoming_dialog import UpcomingDialog
from .reccomendation_dialog import ReccomendationDialog
from .cinema_dialog import CinemaDialog
from data_models.dao import UserDAO
from bot_recognizer import BotRecognizer



#Dialog principale del bot che mostra il menù
class MainDialog(ComponentDialog):

    def __init__(self, user_state: UserState, luis_recognizer: BotRecognizer):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer

        user_profile_dialog = UserProfileDialog(user_state)
        search_film_dialog = SearchFilmDialog(user_state)
        watchlist_dialog = WatchlistDialog(user_state)
        upcoming_dialog = UpcomingDialog(user_state)
        reccomendation_dialog = ReccomendationDialog(user_state)
        cinema_dialog = CinemaDialog(user_state)
        #self.user_profile_accessor = user_state.create_property("MainDialog")
        self.user_profile_dialog_id = user_profile_dialog.id
        self.search_film_dialog_id = search_film_dialog.id
        self.watchlist_dialog_id = watchlist_dialog.id
        self.upcoming_dialog_id = upcoming_dialog.id
        self.reccomendation_dialog_id = reccomendation_dialog.id
        self.cinema_dialog_id = cinema_dialog.id

        self.add_dialog(
            WaterfallDialog(
                'WFMenu',
                [
                    self.is_logged_step,
                    self.menu_step,
                    self.options_step,
                    self.loop_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(user_profile_dialog)
        self.add_dialog(search_film_dialog)
        self.add_dialog(watchlist_dialog)
        self.add_dialog(upcoming_dialog)
        self.add_dialog(reccomendation_dialog)
        self.add_dialog(cinema_dialog)

        self.initial_dialog_id = 'WFMenu'

    async def is_logged_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = step_context.context.activity.from_property.id
        user = UserDAO.searchUserById(str(id_user))

        if user is None:
            await step_context.context.send_activity(MessageFactory.text('Non sei registrato, ti farò selezionare tre generi di interesse'))
            return await step_context.begin_dialog(self.user_profile_dialog_id)
        else:
            await step_context.context.send_activity(MessageFactory.text(f"Bentornato {user.name}"))
            return await step_context.next([])

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        card = HeroCard(
            text = "Come posso aiutarti? Premi su un bottone o scrivi normalmente ciò che vuoi fare\. Per uscire digita quit o esci\.",
            buttons = [
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Cerca informazioni di un film",
                    value = "info"
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Visualizza watchlist",
                    value = "watchlist"
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Film in uscita",
                    value = "uscita"
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Suggerisci film",
                    value = "suggerisci"
                ),
                CardAction(
                    type = ActionTypes.im_back,
                    title = "Cerca cinema vicino a te",
                    value = "cinemavicini"
                )
            ],   
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        


    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option = step_context.result
        option = option.lower()
        
        #chiamata a LUIS per interpretazione del testo
        intent = await LuisHelper.execute_luis_query(self._luis_recognizer, step_context.context)

        if option == "quit" or option == "esci":
            await step_context.context.send_activity("In uscita")
            return await step_context.cancel_all_dialogs()

        elif option == "info" or intent == Intent.SEARCH_FILM.value:
            await step_context.context.send_activity("Hai scelto la ricerca di un film")
            return await step_context.begin_dialog(self.search_film_dialog_id)

        elif option == "uscita" or intent == Intent.UPCOMING_FILMS.value:
            await step_context.context.send_activity("Hai scelto di vedere i film in uscita")
            return await step_context.begin_dialog(self.upcoming_dialog_id)

        elif option == "watchlist" or intent == Intent.WATCHLIST.value:
            await step_context.context.send_activity("Hai scelto la visualizzazione della tua watchlist")
            return await step_context.begin_dialog(self.watchlist_dialog_id)

        elif option == "cinemavicini": 
            await step_context.context.send_activity("Hai scelto la ricerca dei cinema vicini a te")
            return await step_context.begin_dialog(self.cinema_dialog_id)
        
        elif intent == Intent.FIND_CINEMA.value:
            await step_context.context.send_activity("Hai scelto la ricerca dei cinema vicini a te")
            return await step_context.begin_dialog(self.cinema_dialog_id)
        
        elif option == "suggerisci" or Intent.TIP_FILM.value:
            await step_context.context.send_activity("Hai scelto il suggerimento dei film")
            return await step_context.begin_dialog(self.reccomendation_dialog_id)

        else: 
            await step_context.context.send_activity("Non ho capito, ripeti per favore")
            return await step_context.replace_dialog("WFMenu")

    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.replace_dialog("WFMenu")