from ..dialogue_control import Dialogue
from .. import constants_slots
from ..API.search import SearchAPI

UNCLEAR = 'Unclear'


class Policy:
    def __init__(self) -> None:
        self.greeted = False
        self.api = SearchAPI(constants_slots.client_id, constants_slots.client_secret)
        self.additional_asked = False

    def __call__(self, dialogue: Dialogue):
        self.complete = True
        self.policy_results = []
        self.probable_slots = {}

        # Iterate over all slots and find the most probable value for each slot
        for slot in dialogue.state_tracker.keys():
            self.probable_slots[slot] = self.find_most_probable_key(dialogue.state_tracker[slot])
        

        # 1) Check for greetings
        if self.probable_slots[constants_slots.GREET] != 'None' and self.greeted != True:
            self.greeted = True
            self.policy_results.append(dialogue.convert_policy_format('greet')) 
        

        # 2) Check for the mandatory slots `origin`, `destination` 
        if self.probable_slots[constants_slots.ORIGIN] != 'None' and dialogue.required_slots != True:
            city_code = self.api.verify_city(self.probable_slots[constants_slots.ORIGIN])
            if city_code == None:
                if  self.probable_slots[constants_slots.ORIGIN] == UNCLEAR:
                    self.policy_results.append(dialogue.convert_policy_format('request2', constants_slots.ORIGIN))
                else:
                    self.policy_results.append(dialogue.convert_policy_format('inform', 'origin', 'None'))
                self.complete = False
            else:
                if constants_slots.DESTINATION in dialogue.completed_slots:
                    dialogue.required_slots = True
                if constants_slots.ORIGIN not in dialogue.completed_slots:
                    dialogue.completed_slots.append(constants_slots.ORIGIN)
        else:
            if self.probable_slots[constants_slots.ORIGIN] == 'None':
                self.policy_results.append(dialogue.convert_policy_format('request', constants_slots.ORIGIN))
                self.complete = False
    
        if self.probable_slots[constants_slots.DESTINATION] != 'None' and dialogue.required_slots != True:
            city_code = self.api.verify_city(self.probable_slots[constants_slots.DESTINATION])
            if city_code == None:
                if  self.probable_slots[constants_slots.DESTINATION] == UNCLEAR:
                    self.policy_results.append(dialogue.convert_policy_format('request2', constants_slots.DESTINATION))
                else:
                    self.policy_results.append(dialogue.convert_policy_format('inform', 'destination', 'None'))
                self.complete = False
            else:
                if constants_slots.ORIGIN in dialogue.completed_slots:
                    dialogue.required_slots = True
                if constants_slots.DESTINATION not in dialogue.completed_slots:
                    dialogue.completed_slots.append(constants_slots.DESTINATION)
        else:
            if self.probable_slots[constants_slots.DESTINATION] == 'None':
                self.policy_results.append(dialogue.convert_policy_format('request', constants_slots.DESTINATION))
                self.complete = False

     
        # 3) Check for the mandatory slot `date`
        if self.probable_slots[constants_slots.DATE] == 'None' and self.complete == True:
            self.complete = False
            self.policy_results.append(dialogue.convert_policy_format('request', constants_slots.DATE))
        elif self.probable_slots[constants_slots.DATE] == UNCLEAR and self.complete == True:
            self.complete = False
            self.policy_results.append(dialogue.convert_policy_format('request2', constants_slots.DATE))
        elif self.complete == True:
            if constants_slots.DATE not in dialogue.completed_slots:
                dialogue.completed_slots.append(constants_slots.DATE)

        # Ask for additional information
        if self.complete == True and self.additional_asked == False:
            self.policy_results.append(dialogue.convert_policy_format('request', 'return'))
            self.additional_asked = True
            self.complete = False
        elif self.complete == True and constants_slots.TICKET_CLASS not in dialogue.completed_slots:
            self.policy_results.append(dialogue.convert_policy_format('request', 'ticket_class'))
            dialogue.completed_slots.append(constants_slots.RETURN_DATE)
            dialogue.completed_slots.append(constants_slots.TICKET_CLASS)
            self.complete = False

        # Check if the dialogue is complete and if travelers number is set 
        if self.complete:
            if constants_slots.ADULTS in dialogue.state_tracker.keys() or constants_slots.CHILDREN in dialogue.state_tracker.keys():
                # Initiate API search
                flight_info = self.api(self.probable_slots) 
                if len(flight_info) == 0:   
                    self.policy_results.append(dialogue.convert_policy_format('inform', 'flight', 'None'))
                    dialogue.dialogue_end = True
                else:
                    dialogue.flight_data = flight_info

                    # Send confirmation message
                    self.policy_results.append(dialogue.convert_policy_format('confirm'))
                    dialogue.travelers_number_inquiry = False
            else:
                self.policy_results.append(dialogue.convert_policy_format('request', constants_slots.TRAVELERS_NUMBER))
                dialogue.travelers_number_inquiry = True

        # 4) Check for goodbye
        if self.probable_slots[constants_slots.GOODBYE] != 'None':
            self.policy_results = []
            self.policy_results.append(dialogue.convert_policy_format('goodbye'))
            dialogue.dialogue_end = True

        dialogue.policy = self.policy_results
        return dialogue

    def find_most_probable_key(self, dictionary):
        most_probable_key = None
        most_probable_value = 0

        for key_value, probability in dictionary.items():
            if probability > most_probable_value:
                most_probable_key = key_value
                most_probable_value = probability

        if most_probable_value < 0.6 and most_probable_value > 0.4:
            most_probable_key = 'Unclear'
        
        elif most_probable_value < 0.45: 
            most_probable_key = 'None'
        
        return most_probable_key