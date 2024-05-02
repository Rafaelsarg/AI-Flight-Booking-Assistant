from datetime import datetime
from word2number import w2n
import re

greekword_to_number = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
    "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
    "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19, "twentieth": 20,
    "twenty first": 21, "twenty second": 22, "twenty third": 23, "twenty fourth": 24, "twenty fifth": 25,
    "twenty sixth": 26, "twenty seventh": 27, "twenty eighth": 28, "twenty ninth": 29, "thirtieth": 30,
    "thirty first": 31
}


def convert_date_1(date_str):
  """Converts a date string to the format YYYY-MM-DD.

  Args:
    date_str: The date string in one of the following formats:
      DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD

  Returns:
    The date in the format YYYY-MM-DD.

  Raises:
    ValueError: If the date string is not in one of the supported formats.
  """

  try:
    date = datetime.strptime(date_str, '%d/%m/%Y')
  except ValueError:
    try:
      date = datetime.strptime(date_str, '%d-%m-%Y')
    except ValueError:
      try:
        date = datetime.strptime(date_str, '%d.%m.%Y')
      except ValueError:
        try:
          date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
          try:
            date = datetime.strptime(date_str, '%Y/%m/%d')
          except ValueError:
            try:
              date = datetime.strptime(date_str, '%Y.%m.%d')
            except ValueError:
              return None

  return date.strftime('%Y-%m-%d')
    

def find_and_separate_year(input_string):
    """
    Finds and removes occurrences of years written in words like 'two thousand twenty-three'.
    
    Args:
        input_string (str): The input string to process.
        
    Returns:
        tuple: A tuple containing the cleaned string with removed year parts and a list of matched year parts.
    """
    # Replace '-' with space
    cleaned_string = input_string.replace('-', ' ')

    if 'of' in input_string:
      cleaned_string = cleaned_string.replace('of', '')
    
    # Find and remove the part representing years written in words
    pattern = r'(two thousand \w+ \w+)'
    matches = re.findall(pattern, cleaned_string)
    cleaned_string = re.sub(pattern, '', cleaned_string)
    
    if not matches:
        return cleaned_string, None
    
    return cleaned_string, matches[0]

def convert_date_2(input_date):
    year = None
    month = None
    day = None

    # Handle year 
    rest, year = find_and_separate_year(input_date)
    words = rest.split()
    if year is None:
      for word in words:
          if word.isdigit() and len(word) == 4:
              words.remove(word)
              year = int(word)
              break
      if year is None:
          year = datetime.now().year
    else:
      year = w2n.word_to_num(year)
    
    # Handle month
    for word in words:
        if word.lower() in ['january', 'february', 'march', 'april', 'may', 'june', 'july',
                            'august', 'september', 'october', 'november', 'december']:
            words.remove(word)
            month = datetime.strptime(word, '%B').month
            break
    if month is None:
        month = datetime.now().month
    
    # Handle day
    rest = ' '.join(words)
    if rest.isdigit():
      day = int(rest)
    elif rest.lower() in greekword_to_number.keys():
      day = greekword_to_number[rest.lower()]
    elif len(rest) > 2 and rest[-2:] in ['st', 'nd', 'rd', 'th']:
      day = int(rest[:-2])
    else:
      try:
        day = w2n.word_to_num(rest)
      except ValueError:
         return None
    
    # Convert to date
    try:
      date = datetime(year, month, day)
    except ValueError:
      return None
    
    return date.strftime('%Y-%m-%d')
