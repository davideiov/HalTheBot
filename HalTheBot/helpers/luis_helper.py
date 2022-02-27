# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

#Intent definiti all'interno del portale LUIS
class Intent(Enum):
    SEARCH_FILM = "SearchFilm"
    WATCHLIST = "ShowWatchlist"
    FIND_CINEMA = "FindCinema"
    UPCOMING_FILMS = "UpcomingFilms"
    TIP_FILM = "ReccomendationFilm"
    NONE_INTENT = "None"

#definito da LUIS
def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0
    
    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value) 


class LuisHelper:
    #metodo per riconoscere l'intenzione dell'utente
    @staticmethod
    async def execute_luis_query(luis_recognizer: LuisRecognizer, turn_context: TurnContext) -> (Intent):
        intent = None
        
        recognizer_result = await luis_recognizer.recognize(turn_context)

        intent = (
            sorted(
                recognizer_result.intents,
                key = recognizer_result.intents.get,
                reverse = True,
            )[:1][0]
            if recognizer_result.intents
            else None
        )
        
        if intent == Intent.SEARCH_FILM.value:
            return Intent.SEARCH_FILM.value
        if intent == Intent.WATCHLIST.value:
            return Intent.WATCHLIST.value
        if intent == Intent.FIND_CINEMA.value:
            return Intent.FIND_CINEMA.value
        if intent == Intent.UPCOMING_FILMS.value:
            return Intent.UPCOMING_FILMS.value
        if intent == Intent.TIP_FILM.value:
            return Intent.TIP_FILM.value

        return intent