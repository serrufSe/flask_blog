from elasticsearch import Elasticsearch


class User(object):

    def __init__(self):
        super(User, self).__init__()
        self.email = None
        self.password = None

    def __str__(self):
        return self.email


class UserManager(object):

    index = 'user'

    def __init__(self):
        super(UserManager, self).__init__()
        self.es = Elasticsearch()
        self.mapper = UserMapper()

    def get_user_by_email(self, email):
        source_dict = self.es.search(self.index, q='email:'+email)
        return self.mapper.from_dict_to_model(source_dict['hits']['hits'][0]['_source'])


class UserMapper(object):

    @staticmethod
    def from_dict_to_model(source_dict):
        model = User()
        for model_attribute, attriute_value in source_dict.items():
            if hasattr(model, model_attribute):
                model.__setattr__(model_attribute, attriute_value)
        return model

    def from_model_to_dict(self):
        pass
