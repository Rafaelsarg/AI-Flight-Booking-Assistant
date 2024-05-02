import json
import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
import lzma
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras import utils
from keras.utils import pad_sequences
from transformers import BertTokenizer, TFBertModel

MAX_SEQUENCE_LENGTH = 30

def train_model(data, model_paths):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = TFBertModel.from_pretrained('bert-base-uncased')

    features = tf.constant([[0] * MAX_SEQUENCE_LENGTH])
    bert_model._saved_model_inputs_spec = None
    bert_model._set_save_spec(features)

    # Freeze the BERT model so that only additional layers are trained
    bert_model.trainable = False

    # Tokenize the text
    input_ids_list = []
    attention_mask_list = []
    iob_labels = []


    for sample in data:
        sentence = sample['sentence']
        iob_tags = sample['iob_labels']

        inputs = tokenizer(sentence, padding='max_length', max_length=MAX_SEQUENCE_LENGTH, truncation=True, return_tensors="tf")
        input_ids = inputs['input_ids'].numpy()[0]
        attention_mask = inputs['attention_mask'].numpy()[0]

        input_ids_list.append(input_ids)
        attention_mask_list.append(attention_mask)

        iob_labels.append(iob_tags)

    # Reshape the inputs and masks for the model
    X_train_inputs = np.reshape(input_ids_list, (len(input_ids_list), MAX_SEQUENCE_LENGTH))
    X_train_mask = np.reshape(attention_mask_list, (len(attention_mask_list), MAX_SEQUENCE_LENGTH))

    # Convert the labels to a one-hot encoding 
    y_tokenizer = Tokenizer(filters = '', lower = False, split = ' ')
    y_tokenizer.fit_on_texts(iob_labels)

    iob_sequences = y_tokenizer.texts_to_sequences(iob_labels)
    iob_padded = tf.keras.preprocessing.sequence.pad_sequences(iob_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
    y_train = utils.to_categorical(iob_padded)

    num_classes = y_train.shape[2]

    # Bert input layers
    input_ids = tf.keras.layers.Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32', name='input_ids')
    attention_mask = tf.keras.layers.Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32', name='attention_mask')

    # BERT embeddings
    embeddings = bert_model(input_ids, attention_mask=attention_mask)[0]

    # Additional dense and Dropout layers
    layer = tf.keras.layers.Dense(256, activation='relu')(embeddings)
    layer = tf.keras.layers.Dropout(0.5)(layer)
    layer = tf.keras.layers.Dense(128, activation='relu')(layer)
    layer = tf.keras.layers.Dropout(0.5)(layer)

    # Output layer with softmax 
    output = tf.keras.layers.Dense(num_classes, activation='softmax')(layer)

    # Build the model
    model = tf.keras.Model(inputs=[input_ids, attention_mask], outputs=output)

    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
    
    # Print model summary
    model.summary()

    model.fit(
        x=[X_train_inputs, X_train_mask],
        y=y_train,
        batch_size=1,
        epochs=10)
    
    model.save(model_paths[0])
    tokenizer.save_pretrained(model_paths[1])
    with lzma.open(model_paths[2], 'wb') as f:
        pickle.dump(y_tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

def main():
    # Load the training dataset for origin and destination
    with open('data/city_IOB.json') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df.head()

    model_paths = ['model_city/city_model', 'model_city/tokenizer', 'model_city/y_tokenizer']
    train_model(data, model_paths)

    # Load the training dataset for date and return date    
    with open('data/date-IOB.json') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df.head()

    model_paths = ['model_date/date_model', 'model_date/tokenizer', 'model_date/y_tokenizer']
    train_model(data, model_paths)

    

if __name__ == '__main__':
    main()