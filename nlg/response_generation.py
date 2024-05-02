from ..dialogue_control import Dialogue
import yaml
from pathlib import Path
import random
import os

class TemplateNLG():
    def __call__(self, dialogue: Dialogue):
        self.response = ''

        # Load the responses from the yaml file
        with open(os.path.join(Path(__file__).parent, 'response_template.yaml')) as file:
            responses = yaml.load(file, Loader=yaml.FullLoader)
        self.data = responses

        # Get the response
        for action in dialogue.policy:
            self.response += random.choice(self.data[action]) + ' '
        
        if self.response == '':
            self.response = 'Sorry, I did not understand that.'
        
        dialogue.set_response(self.response)
        return dialogue



