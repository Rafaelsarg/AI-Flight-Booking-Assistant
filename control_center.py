#!/usr/bin/env python3

from .nlu.rule_basedNLU import RuleBasedNLU
from .dst.state_tracker import StateTracker
from .nlu.statNLU import StatNLU
from .policy.policy import Policy
from .nlg.response_generation import TemplateNLG
from .dialogue_control import Dialogue
import json

class ControlCenter():
    def __init__(self):
        self.rl = RuleBasedNLU()
        self.st = StatNLU()
        self.dst = StateTracker()
        self.policy_ = Policy()
        self.nlg = TemplateNLG()
    
    def __call__(self, dialogue: Dialogue):
        if dialogue.dialogue_end == True:
            dialogue.set_response('Dialogue ended please press Restart button to start the search again! Thank you')
            data = {'system_response': dialogue.system_response, 
                'flight_data': dialogue.flight_data,
                'travelersNumberInquiry': dialogue.travelers_number_inquiry,
                'dialogueEnd': dialogue.dialogue_end }

            return json.dumps(data)
        
        if not dialogue.travelers_number_inquiry:  
            dialogue = self.rl(dialogue)
            dialogue = self.st(dialogue)
            dialogue = self.dst(dialogue)
        dialogue = self.policy_(dialogue)
        dialogue = self.nlg(dialogue)

        data = {'system_response': dialogue.system_response, 
                'flight_data': dialogue.flight_data,
                'travelersNumberInquiry': dialogue.travelers_number_inquiry,
                'dialogueEnd': dialogue.dialogue_end }

        return json.dumps(data)
            
    def resetDialogue(self):
        self.rl = RuleBasedNLU()
        self.dst = StateTracker()
        self.policy_ = Policy()
        self.nlg = TemplateNLG()

    