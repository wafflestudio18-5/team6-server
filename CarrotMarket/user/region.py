import requests
from rest_framework import status

def get_area_information(data):

    latlang = data.get(latlang)
    MY_API_KEY = data.get(API_KEY)

    if not latlang or not MY_API_KEY:
        return False


    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlang}&key={MY_API_KEY}"

    #url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlang}&key={MY_API_KEY}&language=ko" korean


    response = requests.get(url)


    if response.status_code != status.HTTP_200_OK:
        response_data = {}
        response_data['error_occured'] = "yes" 
        return response_data
    
    response_data = response.json()

    return response_data
