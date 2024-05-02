from flask import Flask, render_template, request, jsonify
from ..dialogue_control import Dialogue
from ..control_center import ControlCenter
from .. import constants_slots

import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5
control_dialogue = ControlCenter()
dialogue = Dialogue()

@app.route("/")
def home_page():
    return render_template('index.html')

@app.route("/get", methods=['GET', 'POST'])
def getMessage():
    data = request.get_json()
    userMsg = data['usrMessage']
    dialogue.set_user_input(userMsg)
    response = control_dialogue(dialogue)
    return response

@app.route("/restart", methods=['GET', 'POST'])
def restart():
    control_dialogue.resetDialogue()
    dialogue.resetDialogue()
    return jsonify({'done': True})

@app.route("/travelersnum", methods=['GET', 'POST'])
def getTravelersNum():
    data = request.get_json()
    dialogue.set_travelers_number({constants_slots.ADULTS: data['adults_num'], constants_slots.CHILDREN: data['kids_num'], constants_slots.INFANTS: data['infants_num']})
    response = control_dialogue(dialogue)
    dialogue.travelers_number_inquiry = False

    return response

@app.route("/flight-itinerary", methods=['GET', 'POST'])
def itineraryPage():
    data = request.get_json()

    return dialogue.flight_data[data['key']]


if __name__ == '__main__':    
    app.run(debug=True)