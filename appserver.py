from flask import Flask, render_template, request
from app import Persona
app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/save", methods=["POST"])
def save_persona():
    p = Persona.get()
    print p.name
    p.name = request.form.get("name")
    p.surname = request.form.get("surname")
    p.save()

    return 200


if __name__ == '__main__':
    app.run()

