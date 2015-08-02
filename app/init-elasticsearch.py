from elasticsearch import Elasticsearch, NotFoundError
from app import app


def create_or_clear_index():
    es = Elasticsearch()
    index_name = app.config.get('ELASTIC_INDEX')
    try:
        es.indices.delete(index=index_name)
    except NotFoundError:
        pass

    es.indices.create(index=index_name,
                      body={
                          "mappings": {
                              "user": {
                                  "_source": {"enabled": True},
                                  "properties": {
                                      "email": {
                                          "type": "string"
                                      },
                                      "password": {
                                          "type": "string",
                                      },
                                  }
                              },
                              "post": {
                                  "_source": {"enabled": True},
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
