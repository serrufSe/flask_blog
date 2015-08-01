from elasticsearch import Elasticsearch, NotFoundError
from models import Model

es = Elasticsearch()
index_name = Model.index

def create_or_clear_index():

   try:
       es.indices.delete(index = index_name)
   except NotFoundError:
       pass

   es.indices.create(index = index_name,
                     body = {
                         "mappings": {
                             "users": {
                                 "_source": { "enabled": True },
                                 "properties": {
                                     "email": {
                                         "type": "string"
                                     },
                                     "password": {
                                         "type": "string",
                                     },
                                 }
                             },
                             "posts": {
                                "_source": { "enabled": True },
                                 "properties": {
                                     "content": {
                                         "type": "string"
                                     },
                                     "user_pk": {
                                         "type": "string",
                                     },
                                 }
                             }
                         }})

if __name__ == '__main__':
    create_or_clear_index()