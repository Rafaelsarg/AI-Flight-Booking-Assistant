from amadeus import Client, ResponseError
from amadeus import Location
from datetime import datetime
from .. import constants_slots
import re
import json

class SearchAPI:
    def __init__(self, c_id, c_secret):
        self.full_flight_data = []
        self.flight_price_data = []
        
        self.amadeus = Client(
            client_id= c_id,
            client_secret= c_secret
        )


    def __call__(self, final_dialogue_states):
        self.origin_IATA, self.destination_IATA = self.search_IATA_codes(final_dialogue_states[constants_slots.ORIGIN], 
                                                                         final_dialogue_states[constants_slots.DESTINATION])
        
        self.flight_data = self.search_flight_offers(self.origin_IATA, self.destination_IATA, 
                                                     final_dialogue_states[constants_slots.DATE], 
                                                     final_dialogue_states[constants_slots.ADULTS], 
                                                     final_dialogue_states[constants_slots.CHILDREN], 
                                                     final_dialogue_states[constants_slots.INFANTS], 
                                                     final_dialogue_states[constants_slots.TICKET_CLASS],
                                                     final_dialogue_states[constants_slots.RETURN_DATE])

        if self.flight_data is None or len(self.flight_data) == 0:
            return []

     
        self.flight_price_data = self.search_flight_price(self.flight_data)

        if len(self.flight_price_data) == 0:
            return []
        
        # Extract the neccessary information from the flight data
        self.full_flight_data = self.extract_flight_data(self.flight_price_data)
        

        return self.full_flight_data
    
    # Search for IATA code of origin and destination
    def search_IATA_codes(self, origin, destination):
        try:
            origin_code = self.amadeus.reference_data.locations.get(keyword=origin,
                                                        subType=Location.ANY)
            destination_code = self.amadeus.reference_data.locations.get(keyword=destination,
                                                        subType=Location.ANY)
            return origin_code.data[0]['iataCode'], destination_code.data[0]['iataCode']
        except:
            return None, None
    
    def verify_city(self, city):
        try:
            city_code = self.amadeus.reference_data.locations.get(keyword=city,
                                                        subType=Location.ANY)
            return city_code.data[0]['iataCode']
        except:
            return None

    # Search for flight offers
    def search_flight_offers(self, origin_code, destination_code, departure_date, adult_num, children_num, infants_num, travel_class, return_date):
        try:
            if travel_class == 'None':
                travel_class = 'ECONOMY'
            if return_date == 'None':
                flight_details = self.amadeus.shopping.flight_offers_search.get(
                        originLocationCode=origin_code, destinationLocationCode=destination_code, 
                        departureDate=departure_date, adults=adult_num,children=children_num, infants=infants_num, travelClass=travel_class)
                

            else:
                flight_details = self.amadeus.shopping.flight_offers_search.get(
                        originLocationCode=origin_code, destinationLocationCode=destination_code, 
                        departureDate=departure_date, adults=adult_num, children=children_num, infants=infants_num, travelClass=travel_class, returnDate=return_date)
            
             # If no flight offers are found, search for flight offers without a travel class
            if len(flight_details.data) == 0:
                if return_date == '':
                    flight_details = self.amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin_code, destinationLocationCode=destination_code, 
                    departureDate=departure_date, adults=adult_num, children=children_num, infants=infants_num)
                else:
                    flight_details = self.amadeus.shopping.flight_offers_search.get(
                        originLocationCode=origin_code, destinationLocationCode=destination_code, 
                        departureDate=departure_date, adults=adult_num, children=children_num, infants=infants_num, returnDate=return_date)
                    
            return flight_details.data
        except ResponseError as error:
            return None

        

    # Search for the price of a the first 5 flight offers 
    def search_flight_price(self, flight_details):
        flight_prices = []
        count = 0
        for flight in flight_details:
            if count == 5:
                break
            try:
                flight_prices.append(self.amadeus.shopping.flight_offers.pricing.post(flight))
                count += 1
            except:
                continue
                
            
        return flight_prices
    
    def extract_flight_data(self, flight_price_data):
        """Extracts the necessary information from the flight data.

        Args:
            flight_price_data: The flight price data from the API.

        Returns:
            A dictionary containing the flight information.
        """

        flights = {}
        counter = 1

        for price_data in flight_price_data:
            for flight in price_data.data["flightOffers"]:
                flight_info = {}

                # Information about each segment of the flight
                for segment in flight["itineraries"][0]["segments"]:
                    part = {
                        "departure": segment["departure"],
                        "arrival": segment["arrival"],
                        "duration": self._convert_duration_to_dict(segment["duration"]),
                    }
                    part['departure']["at"] = self._dates_converter(part['departure']["at"])
                    part['arrival']["at"] = self._dates_converter(part['arrival']["at"])

                    if "segments" not in flight_info:
                        flight_info["segments"] = [part]
                    else:
                        flight_info["segments"].append(part)

                #Information about the return flight
                if len(flight["itineraries"]) > 1:
                    for segment in flight["itineraries"][1]["segments"]:
                        part = {
                            "departure": segment["departure"],
                            "arrival": segment["arrival"],
                            "duration": self._convert_duration_to_dict(segment["duration"]),
                        }
                        part['departure']["at"] = self._dates_converter(part['departure']["at"])
                        part['arrival']["at"] = self._dates_converter(part['arrival']["at"])

                        if "return" not in flight_info:
                            flight_info["return"] = [part]
                        else:
                            flight_info["return"].append(part)

                # Origin and destination
                flight_info["origin"] = flight_info["segments"][0]["departure"]["iataCode"]
                flight_info["destination"] = flight_info["segments"][-1]["arrival"]["iataCode"]
                
                # Departure and arrival dates and times
                flight_info["departure"] = flight_info["segments"][0]["departure"]["at"]
                flight_info["arrival"] = flight_info["segments"][-1]["arrival"]["at"]

                

                # Flight duration
                flight_info["duration"] = self._calculate_duration(flight_info["segments"])
                if "return" in flight_info:
                    flight_info["return_duration"] = self._calculate_duration(flight_info["return"]) if "return" in flight_info else None

                    # Return departure and arrival dates and times
                    flight_info["return_departure"] = flight_info["return"][0]["departure"]["at"]
                    flight_info["return_arrival"] = flight_info["return"][-1]["arrival"]["at"]

                # Price and currency
                flight_info["price"] = flight["price"]["total"]
                flight_info["currency"] = flight["price"]["currency"]

                # Number of stops
                flight_info["stops"] = len(flight["itineraries"][0]["segments"]) - 1
                if "return" in flight_info:
                    flight_info["return_stops"] = len(flight["itineraries"][1]["segments"]) - 1 if "return" in flight_info else None

                flights["flight" + str(counter)] = flight_info
                counter += 1

        return flights


    def _convert_duration_to_dict(self, duration_str: str) -> dict:
        """Converts the duration of a flight from a string to a dictionary.

        Args:
            duration_str: The duration of the flight in string format.

        Returns:
            A dictionary containing the duration of the flight in hours and minutes.
        """
        match = re.match(r'PT(?P<hours>\d+)H(?P<minutes>\d+)M', duration_str)
        if match:
            return {'hour': int(match.group('hours')), 'minute':  int(match.group('minutes') or '0')}

        match_hours = re.match(r'PT(?P<hours>\d+)H', duration_str)
        if match_hours:
            return {'hour': int(match_hours.group('hours')), 'minute': 0}

        match_minutes = re.match(r'PT(?P<minutes>\d+)M', duration_str)
        if match_minutes:
            return {'hour': 0, 'minute': int(match_minutes.group('minutes'))}

        return {'hour': 0, 'minute': 0}
    

    def _calculate_duration(self, segments):
        """Calculates the total duration of a flight itinerary.

        Args:
            segments: A list of flight segments.

        Returns:
            A dictionary containing the total duration of the flight itinerary, in hours
            and minutes.
        """

        total_flight_time = {"hour": 0, "minute": 0}
        total_date_time_difference = 0

        for i in range(len(segments)):
            if i == len(segments) - 1:
                flight_time = segments[i]["duration"]
                total_flight_time["hour"] += flight_time["hour"]
                total_flight_time["minute"] += flight_time["minute"]
                if total_flight_time["minute"] > 60:
                    add_hour = total_flight_time["minute"] // 60
                    total_flight_time["minute"] = total_flight_time["minute"] % 60
                    total_flight_time["hour"] += add_hour
                break

            arrival_datetime = datetime(
                segments[i]["arrival"]["at"]["year"],
                segments[i]["arrival"]["at"]["month"],
                segments[i]["arrival"]["at"]["day"],
                segments[i]["arrival"]["at"]["hour"],
                segments[i]["arrival"]["at"]["minute"],
                segments[i]["arrival"]["at"]["second"])
            departure_datetime = datetime(
                segments[i + 1]["departure"]["at"]["year"],
                segments[i + 1]["departure"]["at"]["month"],
                segments[i + 1]["departure"]["at"]["day"],
                segments[i + 1]["departure"]["at"]["hour"],
                segments[i + 1]["departure"]["at"]["minute"],
                segments[i + 1]["departure"]["at"]["second"])

            flight_time = segments[i]["duration"]

            if total_date_time_difference == 0:
                total_date_time_difference = departure_datetime - arrival_datetime
            else:
                total_date_time_difference += departure_datetime - arrival_datetime

            total_flight_time["hour"] += flight_time["hour"]
            total_flight_time["minute"] += flight_time["minute"]

            total_flight_time["hour"] += total_flight_time["minute"] // 60
            total_flight_time["minute"] = total_flight_time["minute"] % 60

        if total_date_time_difference != 0:
            total_flight_time["hour"] += total_date_time_difference.days * 24 + total_date_time_difference.seconds // 3600
            total_flight_time["minute"] += (total_date_time_difference.seconds // 60) % 60
            if total_flight_time["minute"] > 60:
                add_hour = total_flight_time["minute"] // 60
                total_flight_time["minute"] = total_flight_time["minute"] % 60
                total_flight_time["hour"] += add_hour

        return total_flight_time
    
    def _dates_converter(self, date_str):
        time_info = {}

        date, time = date_str.split('T')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')

        time_info['year'] = int(year)
        time_info['month'] = int(month)
        time_info['day'] = int(day)
        time_info['hour'] = int(hour)
        time_info['minute'] = int(minute)
        time_info['second'] = int(second)

        return time_info