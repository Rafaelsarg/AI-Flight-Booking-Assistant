import numpy as np
from ..dialogue_control import Dialogue
from ..date_converter import date_converter
from .. import constants_slots
import tensorflow as tf
from transformers import BertTokenizer, TFBertModel
import pickle
import lzma
import string
from pathlib import Path
import os

MAX_SEQUENCE_LENGTH = 30


class StatNLU:    
    def __init__(self) -> None:
        self.orig_dest_model = tf.keras.models.load_model(os.path.join(Path(__file__).parent,'model_city','city_model'))
        self.orig_dest_tokenizer = BertTokenizer.from_pretrained(os.path.join(Path(__file__).parent,'model_city','tokenizer'))
        with lzma.open(os.path.join(Path(__file__).parent,'model_city','y_tokenizer'),  'rb') as f:
            self.orig_dest_y_tokenizer = pickle.load(f)
         
        self.date_model = tf.keras.models.load_model(os.path.join(Path(__file__).parent,'model_date','date_model'))
        self.date_tokenizer = BertTokenizer.from_pretrained(os.path.join(Path(__file__).parent,'model_date','tokenizer'))
        with lzma.open(os.path.join(Path(__file__).parent,'model_date','y_tokenizer'),  'rb') as f:
            self.date_y_tokenizer = pickle.load(f)
            
    def __call__(self, dialogue: Dialogue):
        """Processes the given dialogue and returns the updated dialogue."""

        # If the origin and destination slots are present, predict the date or return date from the user input.
        if dialogue.required_slots:
            self.date, self.return_date = self.predict_date_return(dialogue.user_input)
            converted_date = date_converter.convert_date_2(next(iter(self.date.keys())))
            converted_return_date = date_converter.convert_date_2(next(iter(self.return_date.keys())))

            # If the date is already completed or cannot be converted, set it to None.
            if constants_slots.DATE in dialogue.completed_slots or converted_date is None:
                self.date = None
            else:
                self.date = {converted_date: next(iter(self.date.values()))}

            # If the return date is already completed or cannot be converted, set it to None.
            if constants_slots.RETURN_DATE in dialogue.completed_slots or converted_return_date is None or constants_slots.DATE not in dialogue.completed_slots:
                self.return_date = None
            else:
                self.return_date = {converted_return_date: next(iter(self.return_date.values()))}

            # Update the slot values.
            self.slot_values = {'origin': None, 'destination': None, 'date': self.date, 'return_date': self.return_date}

        # Otherwise, predict the origin and destination from the user input.
        else:
            self.origin, self.destination = self.predict_orig_dest(dialogue.user_input)
            self.slot_values = {'origin': self.origin, 'destination': self.destination, 'date': None, 'return_date':None}

        # Set the NLU result.
        dialogue.stat_nlu_result = self.slot_values

        # Return the updated dialogue.
        return dialogue

    def predict_orig_dest(self, sentence):
        # Preprocess the new sentences
        sentence = self.remove_punctuation(sentence)

        inputs = self.orig_dest_tokenizer(sentence, padding='max_length', max_length=MAX_SEQUENCE_LENGTH, truncation=True, return_tensors="tf")
        input_ids = inputs['input_ids'][0]  
        attention_mask = inputs['attention_mask'][0]  

        input_ids_tensor = tf.keras.preprocessing.sequence.pad_sequences([input_ids], padding='post', maxlen=MAX_SEQUENCE_LENGTH)
        attention_mask_tensor = tf.keras.preprocessing.sequence.pad_sequences([attention_mask], padding='post', maxlen=MAX_SEQUENCE_LENGTH)

        # Make predictions
        predictions = self.orig_dest_model.predict([input_ids_tensor, attention_mask_tensor])

        # Decode the predictions
        predicted_slots = [self.orig_dest_y_tokenizer.index_word[i] for i in [np.argmax(x) for x in predictions[0][:]] if i != 0]

        # Predicted best two percentages for each slot
        predicted_percentages = [np.max(x) for x in predictions[0][:] if np.max(x) != 0]
        predicted_percentages = predicted_percentages[:len(predicted_slots)]
        
        # Get the origin and destination
        origin = ''
        destination = ''
        origin_confidence = []
        destination_confidence = []
        for i in range(len(predicted_slots)):
            if len(predicted_slots) >= 2* len(sentence.split()):
                break
            if i - (len(predicted_slots) - len(sentence.split())) >= 0:
                j = i - (len(predicted_slots) - len(sentence.split()))
            else:
                j = i
            if predicted_slots[i] == 'B-origin':                
                origin = sentence.split()[j]
                origin_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'I-origin':
                origin += ' ' + sentence.split()[j]
                origin_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'B-destination':
                destination = sentence.split()[j]
                destination_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'I-destination':
                destination += ' ' + sentence.split()[j]
                destination_confidence.append(predicted_percentages[i])
        
        # Return the average confidence for each slot
        if origin_confidence:
            origin_confidence = sum(origin_confidence) / len(origin_confidence)
        else:
            origin_confidence = 0
        if destination_confidence:
            destination_confidence = sum(destination_confidence) / len(destination_confidence)
        else:
            destination_confidence = 0

        
        return {origin : origin_confidence}, {destination : destination_confidence}


    def predict_date_return(self, sentence):
        # Preprocess the new sentences
        sentence = self.remove_punctuation(sentence)

        inputs = self.date_tokenizer(sentence, padding='max_length', max_length=MAX_SEQUENCE_LENGTH, truncation=True, return_tensors="tf")
        input_ids = inputs['input_ids'][0]  
        attention_mask = inputs['attention_mask'][0]  

        input_ids_tensor = tf.keras.preprocessing.sequence.pad_sequences([input_ids], padding='post', maxlen=MAX_SEQUENCE_LENGTH)
        attention_mask_tensor = tf.keras.preprocessing.sequence.pad_sequences([attention_mask], padding='post', maxlen=MAX_SEQUENCE_LENGTH)

        # Make predictions
        predictions = self.date_model.predict([input_ids_tensor, attention_mask_tensor])

        # Decode the predictions
        predicted_slots = [self.date_y_tokenizer.index_word[i] for i in [np.argmax(x) for x in predictions[0][:]] if i != 0]

        # Predicted best two percentages for each slot
        predicted_percentages = [np.max(x) for x in predictions[0][:] if np.max(x) != 0]
        predicted_percentages = predicted_percentages[:len(predicted_slots)]
        
        # Get the date and return date
        date = ''
        return_date = ''
        date_confidence = []
        return_date_confidence = []
        for i in range(len(predicted_slots)):
            if len(predicted_slots) > 2 * len(sentence.split()):
                break
            if i - (len(predicted_slots) - len(sentence.split())) >= 0:
                j = i - (len(predicted_slots) - len(sentence.split()))
            else:
                j = i
            if predicted_slots[i] == 'B-date':
                date = sentence.split()[j]
                date_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'I-date':
                date += ' ' + sentence.split()[j]
                date_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'B-return':
                return_date = sentence.split()[j]
                return_date_confidence.append(predicted_percentages[i])
            elif predicted_slots[i] == 'I-return':
                return_date += ' ' + sentence.split()[j]
                return_date_confidence.append(predicted_percentages[i])
        
        # Return the average confidence for each slot
        if date_confidence:
            date_confidence = sum(date_confidence) / len(date_confidence)
        else:
            date_confidence = 0
        if return_date_confidence:
            return_date_confidence = sum(return_date_confidence) / len(return_date_confidence)
        else:
            return_date_confidence = 0

        return {date : date_confidence}, {return_date : return_date_confidence}


    # Remove punctuation except / - for dates
    def remove_punctuation(self, sentence):
        punctuation_marks = string.punctuation
        punctuation_marks = punctuation_marks.replace("/", "")
        punctuation_marks = punctuation_marks.replace("-", "")
        sentence = (''.join(ch for ch in sentence if ch not in punctuation_marks))

        return sentence