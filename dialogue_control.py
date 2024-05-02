#!/usr/bin/env python3

from . import constants_slots

class Dialogue():
    def __init__(self):
        self.nlu_result = {} # dictionary of slot value confidence pairs
        self.stat_nlu_result = {} # dictionary of slot value confidence pairs
        self.state_tracker = {} # dictionary of slot value pairs
        self.policy = [] # list of actions

        self.user_input = ''
        self.system_response = ''
        self.travelers_number_inquiry = False
        self.flight_data = {}
        self.dialogue_end = False

        self.required_slots = False
        self.completed_slots = []

    def set_response(self, response):
        self.system_response = response

    def set_user_input(self, sentence):
        self.user_input = sentence

    def set_travelers_number(self, data):
        self.state_tracker[constants_slots.ADULTS] = { int(data[constants_slots.ADULTS]) : 1.0 }
        self.state_tracker[constants_slots.CHILDREN] = { int(data[constants_slots.CHILDREN]) : 1.0 }
        self.state_tracker[constants_slots.INFANTS] = { int(data[constants_slots.INFANTS]) : 1.0 }


    # Given the action, slot and value, convert it to the format of the policy
    # i.e. {'action': 'ask', 'slot': 'origin', 'value': None} will be
    # converted to request(origin)
    def convert_policy_format(self, action, slot = '', value = ''):
        if slot and value:
            return action + '(' + slot + '=' + '{' + value + '}' + ')'
        elif slot:
            return action + '(' + slot + ')'
        else:
          return action + '()'

    def resetDialogue(self):
        self.nlu_result = {}
        self.stat_nlu_result = {}
        self.state_tracker = {}
        self.policy = []
        self.user_input = ''
        self.system_response = ''
        self.travelers_number_inquiry = False
        self.flight_data = {}
        self.dialogue_end = False
        self.required_slots = False
        self.completed_slots = []

