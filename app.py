from mongomodels.models import EventedValidatingStruct
from mongomodels.models import ValidatingStruct
from mongomodels.models.exceptions import NotFoundException
from mongomodels.db import MongoDatabaseBackend
from juggernaut import Juggernaut


class Callback(ValidatingStruct):
    __DOCUMENT_DB__ = MongoDatabaseBackend('localhost', 'test')

    def validate(self):
        self.validate_not_empty('caller_id')
        self.validate_not_empty('caller_class')
        self.validate_not_empty('callback')


class SignalStorage(ValidatingStruct):
    __DOCUMENT_DB__ = MongoDatabaseBackend('localhost', 'test')

    def validate(self):
        self.validate_not_empty('signal_name')
        self.validate_not_empty('callback_list')

    @classmethod
    def callbacks(cls, signal_name):
        signal_model = cls.get(signal_name=signal_name)
        cbs = []
        for cb_id in signal_model.callback_list:
            try:
                cbs.append(Callback.get(_id=cb_id))
            except NotFoundException:
                continue # explicitly silenced
        return cbs


class EventDispatcher(object):
    __SIGNALS__ = SignalStorage

    def __init__(self):
        self.__JUGGERNAUT__ = Juggernaut()

    @classmethod
    def subscribe(cls, signal_name, callback, caller):
        try:
            signal_model = cls.__SIGNALS__.get(signal_name=signal_name)
        except NotFoundException:
            signal_model = cls.__SIGNALS__(signal_name=signal_name)
            signal_model.callback_list = []
        callback_model = Callback(
                           caller_id=caller._id,
                           caller_class=caller.__class__.__name__,
                           callback=callback.__name__
                         )
        callback_model.save()
        signal_model.callback_list.append(callback_model._id)
        signal_model.save()

    def main_loop(self):
        for signal_name, data in self.__JUGGERNAUT__.subscribe_listen():
            for callback_model in self.__SIGNALS__.callbacks(signal_name):
                caller_class = globals().get(callback_model.caller_class)
                caller_object = caller_class.get(_id=callback_model.caller_id)
                getattr(caller_object, callback_model.callback)(**data)


class JuggernautEventedStruct(EventedValidatingStruct):
    __EVENT_DISPATCHER__ = EventDispatcher

    def __init__(self, **kwargs):
        super(JuggernautEventedStruct, self).__init__(**kwargs)
        self.__JUGGERNAUT__ = Juggernaut()

    def on(self, signal_name, callback):
        self.__EVENT_DISPATCHER__.subscribe(signal_name, callback, self)

    def emit(self, signal_name, **kwargs):
        self.__JUGGERNAUT__.publish(signal_name, kwargs)


class Persona(JuggernautEventedStruct):
    __DOCUMENT_DB__ = MongoDatabaseBackend('localhost', 'test')

    def post_save(self, is_new):
        self.emit("persona:saved", model=self.to_struct())

    def do_something(self, **kwargs):
        print "hola"


if __name__ == '__main__':

    Persona.teardown()
    SignalStorage.teardown()
    Callback.teardown()

    persona = Persona(name='pepe', surname='pirulo')
    persona.save()

    EventDispatcher().main_loop()
