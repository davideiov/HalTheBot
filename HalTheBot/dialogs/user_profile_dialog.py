# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState, CardFactory
from botbuilder.schema import HeroCard


from config import DefaultConfig

from data_models.dao import UserDAO
from data_models.user_profile import UserProfile
GENRES = ["Azione", "Avventura", "Animazione", "Commedia", "Crime", "Documentario", 
"Dramma", "Famiglia", "Fantasy", "Storia", "Horror", "Musica", "Mistero", "Romance", 
"Fantascienza", "Thriller", "Guerra", "Western"]
CONFIG = DefaultConfig

#Dialog per il primo accesso dell'utente al bot
class UserProfileDialog(ComponentDialog):

    def __init__(self, user_state: UserState):
        super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.name_step,
                    self.genres_step_one,
                    self.genres_step_two,
                    self.genres_step_three,
                    self.summary_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Innanzitutto, inserisci il tuo nome!")),
        )

    async def genres_step_one(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["name"] = step_context.result
        step_context.values["genres"] = GENRES

        await step_context.context.send_activity(
            MessageFactory.text(f"Benvenuto {step_context.result}")
        )

        card = self.create_card(step_context)

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.attachment(card),
                retry_prompt= MessageFactory.text("Inserisci il tuo genere preferito\\."),
            ),
        )

    async def genres_step_two(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        list = []
        genres_list = step_context.values["genres"]
        result = step_context.result

        for i in range(len(genres_list)):
            if result.lower() == genres_list[i].lower():
                list.append(genres_list[i])
                genres_list.pop(i)
                break

        step_context.values["favGenres"] = list

        await step_context.context.send_activity(
            MessageFactory.text(f"Hai scelto {step_context.result}")
        )
        
        card = self.create_card(step_context)

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.attachment(card),
                retry_prompt= MessageFactory.text("Inserisci il tuo genere preferito\\."),
            ),
        )

    async def genres_step_three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        list = step_context.values["favGenres"]
        genres_list = step_context.values["genres"]
        result = step_context.result

        for i in range(len(genres_list)):
            if result.lower() == genres_list[i].lower():
                list.append(genres_list[i])
                genres_list.pop(i)
                break

        step_context.values["favGenres"] = list

        await step_context.context.send_activity(
            MessageFactory.text(f"Hai scelto {step_context.result}")
        )

        card = self.create_card(step_context)

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.attachment(card),
                retry_prompt= MessageFactory.text("Inserisci il tuo genere preferito\\."),
            ),
        )

    async def summary_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        list = step_context.values["favGenres"]
        genres_list = step_context.values["genres"]
        result = step_context.result

        for i in range(len(genres_list)):
            if result.lower() == genres_list[i].lower():
                list.append(genres_list[i])
                genres_list.pop(i)
                break

        step_context.values["favGenres"] = list

        msg = "Ecco i tuoi generi preferiti: "
        for genre in list:
            msg = msg + genre + " "
        await step_context.context.send_activity(MessageFactory.text(msg))
        
        message = ("Grazie per le informazioni, inizia a scoprire le funzionalità")
        await step_context.context.send_activity(message)
       

        id_user = step_context.context.activity.from_property.id

        user = UserProfile(str(id_user), step_context.values["name"], step_context.values["favGenres"], [], [])
        UserDAO.insertUser(user)

        return await step_context.end_dialog()

    def create_card(self, step_context):
        title = "Scegli un genere tra quelli proposti:"
        text= ""
        for g in step_context.values["genres"]:
            text += "\- " + g
            text += "\n"
        card = HeroCard(title=title, text=text)


        return CardFactory.hero_card(card)