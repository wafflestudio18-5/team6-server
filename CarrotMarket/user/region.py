import requests
from rest_framework import status

def get_area_information(data):

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    latlng = str(latitude)+","+str(longitude)
    #MY_API_KEY = data.get('API_KEY')

    if not latlng:
        response_data = {}
        response_data['error_occured'] = "latlng_miss" 
        return response_data

    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key=AIzaSyCQTWnxCsQW0RsDe_1IW8yh-_LuviWQcS4&language=ko&result_type=administrative_area_level_1|locality|sublocality_level_2"

    #sublocality_level_2
    #locality
    #administrative_area_level_1
    #url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key={MY_API_KEY}&language=ko" korean

    response = requests.get(url)

    if response.status_code != status.HTTP_200_OK:
        response_data = {}
        response_data['error_occured'] = "api response not OK" 
        return response_data
    
    response_json = response.json()
    
    response_result = response_json["results"]
    
    response_value = response_result[0]

    address_components = response_value["address_components"]
    formatted_address = response_value["formatted_address"]

    response_data = {}
    response_data["formatted_address"] = formatted_address

    for component in address_components:
        cur_type = component['types']
        cur_value = component["long_name"]

        if "sublocality_level_2" in cur_type:
            response_data["dong"] = cur_value
        elif "sublocality_level_1" in cur_type:
            response_data["gu"] = cur_value
        elif "administrative_area_level_1" in cur_type:
            response_data["province"] = cur_value
        elif "locality" in cur_type:
            response_data["si"] = cur_value
        else :
            pass

    #response_data = response_json

    response_data['error_occured'] = 'no'

    return response_data
