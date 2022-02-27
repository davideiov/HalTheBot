from azure.cosmos import CosmosClient
from data_models import UserProfile
from config import DefaultConfig

CONFIG = DefaultConfig()

uri = CONFIG.ACCOUNT_URI
key = CONFIG.COSMOSDB_PKEY
database_name = 'UtentiBot'
container_name = 'UtentiBot'

#classe che permette operazioni CRUD per il database
class UserDAO:

    @staticmethod
    def insertUser(user: UserProfile):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        container.upsert_item({
            'id': user.id,
            'name': user.name,
            'fav_genres': user.fav_genres,
            'watchlist': user.watchlist,
            'watchedlist': user.watchedlist
        })

    @staticmethod
    def searchUserById(id_user: str):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        for item in container.query_items(query = f'SELECT * FROM {container_name} u WHERE u.id LIKE "{id_user}"', 
        enable_cross_partition_query=True):
            
            user = UserProfile(item['id'], item['name'], item['fav_genres'], item['watchlist'], item['watchedlist'])
            
            return user

    @staticmethod
    def updateUserById(user: UserProfile):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        for item in container.query_items(query = f'SELECT * FROM {container_name} u WHERE u.id LIKE "{user.id}"', 
        enable_cross_partition_query=True):
            
            container.replace_item(item, {
                'id': user.id,
                'name': user.name,
                'fav_genres': user.fav_genres,
                'watchlist': user.watchlist,
                'watchedlist': user.watchedlist
            }, populate_query_metrics=None, pre_trigger_include=None, post_trigger_include=None)
            return