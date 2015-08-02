from elasticsearch import Elasticsearch, NotFoundError
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from abc import ABCMeta, abstractmethod


class Model(object):
    __metaclass__ = ABCMeta

    index = 'flask'

    def __init__(self):
        super(Model, self).__init__()
        self.pk = None

    def get_public_attribute(self):
        return [attribute for attribute in self.__dict__ if attribute != 'pk']

    @abstractmethod
    def get_identity(self):
        pass

class User(Model):

    doc_type = 'user'

    def __init__(self):
        super(User, self).__init__()
        self.email = None
        self.user_password = None
        self.personal_information = None

    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def __str__(self):
        return self.email

    def get_identity(self):
        if not self.email:
            raise Exception("Identity not define")
        return self.email

    def verify_password(self, password):
        return check_password_hash(self.user_password, password)

class Post(Model):

    doc_type='post'

    def __init__(self):
        super(Post, self).__init__()
        self.user_pk = None
        self.content = None

    def get_identity(self):
        return uuid.uuid1().int


class ObjectManager(object):

    def __init__(self, index, doc_type, model_class):
        super(ObjectManager, self).__init__()
        self.index = index
        self.doc_type = doc_type
        self.model_class = model_class
        self.es = Elasticsearch()
        self.mapper = ObjectMapper()

    def find_one(self, pk):
        source_dict = self.es.get(index=self.index, doc_type=self.doc_type, id=pk)
        return self.mapper.from_dict_to_model(source_dict, self.model_class)

    def save(self, model):
        model_dict = self.mapper.from_model_to_dict(model)
        res = self.es.index(index=self.index, doc_type=self.doc_type, id=model.get_identity(), body=model_dict)
        return res['created']

    def find_all(self):
        res = self.es.search(index=self.index, body={"query": {"match_all": {}}})
        return [self.mapper.from_dict_to_model(model, self.model_class) for model in res['hits']['hits']]

    def update(self, model):
        model_dict = self.mapper.from_model_to_dict(model)
        res = self.es.update(index=self.index, doc_type=self.doc_type, id=model.pk, body={"doc": model_dict})
        return res

class ObjectMapper(object):

    @staticmethod
    def from_dict_to_model(source_dict, model_class):
        model_instance = model_class()
        for model_attribute, attriute_value in source_dict['_source'].items():
            if hasattr(model_instance, model_attribute):
                model_instance.__setattr__(model_attribute, attriute_value)
        model_instance.pk = source_dict['_id']
        return model_instance

    @staticmethod
    def from_model_to_dict(model):
        model_dict = {}
        for attribute in model.get_public_attribute():
            model_dict[attribute] = getattr(model, attribute)
        return model_dict



