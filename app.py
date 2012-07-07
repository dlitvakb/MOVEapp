from flask import Flask, render_template
from mongomodels.models import EventedValidatingStruct
from mongomodels.db import DocumentDatabase
from juggernaut import Juggernaut


app = Flask(__name__)


class JuggernautEventedStruct(EventedValidatingStruct):
    def __init__(self, **kwargs):
        self.__JUGGERNAUT__ = Juggernaut()

    def on(self, signal_name, callback):
        super(JuggernautEventedStruct, self).on(signal_name, callback)
        self.__JUGGERNAUT__.subscribe(signal_name, callback)

    def emit(self, signal_name, **kwargs):
        super(JuggernautEventedStruct, self).emit(signal_name, **kwargs)
        self.__JUGGERNAUT__.publish(signal_name, kwargs)


class Persona(JuggernautEventedStruct):
    __DOCUMENT_DB__ = DocumentDatabase('localhost', 'test')

    def post_save(self, is_new):
        self.emit("persona:saved", self.to_struct())

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html',
                model={'name':'pepe', 'surname':'surname'})

if __name__ == '__main__':
    app.run(debug=True)
