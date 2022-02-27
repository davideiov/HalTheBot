# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

#Bean utente
class UserProfile:

    def __init__(self, id: str, name: str = None, fav_genres: list = None, watchlist: list = None, watchedlist: list = None):
        self.id = id
        self.name = name
        self.fav_genres = [] if fav_genres is None else fav_genres
        self.watchlist = [] if watchlist is None else watchlist
        self.watchedlist = [] if watchedlist is None else watchedlist