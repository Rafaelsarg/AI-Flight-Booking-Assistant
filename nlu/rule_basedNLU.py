from ..dialogue_control import Dialogue
from .. import constants_slots
from ..date_converter import date_converter
import regex as re

class RuleBasedNLU:
    def __call__(self, dialogue: Dialogue):
        self.slot_values = {}
        self.greet = self.extract_greet(dialogue.user_input)
        self.goodbye = self.extract_goodbye(dialogue.user_input)
        self.ticket_class = self.extract_ticket_class(dialogue.user_input)
        self.date =  date_converter.convert_date_1(self.extract_date(dialogue.user_input))
        self.return_date =  date_converter.convert_date_1(self.extract_date(dialogue.user_input))

        
        self.update_slot_values(dialogue)

        dialogue.nlu_result = self.slot_values
        return dialogue

    def update_slot_values(self, dialogue):
        for attribute in [constants_slots.GREET, constants_slots.GOODBYE, constants_slots.TICKET_CLASS]:
            if getattr(self, attribute):
                # In a rule based NLU, the confidence is always 1
                self.slot_values.update({attribute: {getattr(self, attribute): 1}})
            else:
                self.slot_values.update({attribute: {}})

        if constants_slots.DATE not in dialogue.completed_slots and self.date != None:
            self.slot_values.update({constants_slots.DATE: {self.date : 1}})
        elif constants_slots.RETURN_DATE not in dialogue.completed_slots and self.return_date != None:
            self.slot_values.update({constants_slots.RETURN_DATE: { self.return_date : 1}})
        

    def extract_greet(self, sentence):
        if any([word in sentence.lower().split() for word in ['hello', 'hi', 'hey']]):
            return True
        return False

    def extract_goodbye(self, sentence):
        if any([word in sentence.split() for word in ['bye', 'goodbye', 'see you soon', 'see ya', 'see you later']]):
            return True
        return False

    def extract_ticket_class(self, sentence):
        ticket_class_pattern1 = r'(?i)(economy|business|first)'
        ticket_class_pattern2 = r'(?i)(economy class|business class|first class|any class)'
        ticket_class_pattern3 = r'(?i)(economy ticket|business ticket|first ticket|any ticket)'
        ticket_class_pattern4 = r'(?i)(economy tickets|business tickets|first tickets|any tickets)'
        ticket_class_pattern5 = r'(?i)(economy flight|business flight|first flight|any flight)'
        ticket_class_pattern6 = r'(?i)(economy flights|business flights|first flights|any flights)'

        combined_pattern = f'{ticket_class_pattern2}|{ticket_class_pattern3}|{ticket_class_pattern4}|{ticket_class_pattern5}|{ticket_class_pattern6}'
        matches = re.findall(
            combined_pattern, sentence, re.IGNORECASE
        )
        if matches:
            for match in matches[0]:
                if match:
                    if 'economy' in match:
                        return 'ECONOMY'
                    elif 'business' in match:
                        return 'BUSINESS'
                    elif 'first' in match:
                        return 'FIRST'
        else:
            matches = re.findall(ticket_class_pattern1, sentence)
            if matches:
                return matches[0]
        return None
    
    def extract_date(self, sentence):
        date_pattern1 = r'(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$'
        date_pattern2 = r'(0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).(\d{4})$'
        date_pattern3 = r'(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4})$'
        date_pattern4 = r'(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])'
        date_pattern5 = r'(\d{4}).(0[1-9]|1[0-2]).(0[1-9]|[12][0-9]|3[01])$'
        date_pattern6 = r'(\d{4})/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$'

        combined_pattern = f'{date_pattern1}|{date_pattern2}|{date_pattern3}|{date_pattern4}|{date_pattern5}|{date_pattern6}'
        
        matches = re.findall(combined_pattern, sentence, re.IGNORECASE)

        res = []
        if matches:
            for match in matches:
                for const in match:
                    if const != '':
                        res.append(const)
        return "/".join(res)

