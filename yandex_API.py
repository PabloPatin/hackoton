import requests
from settings import COORDINATES_API_KEY, MATRIX_API_KEY, DATA_PATH, LOCATION_MATRIX_FILE
import pickle
import json
from tqdm import tqdm


def send_request(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def request_coordinates(adress):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={COORDINATES_API_KEY}&geocode={adress}&format=json"
    response = send_request(url).json()
    coordinates = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
    return coordinates[::-1]


def create_matrix_row(base_coordinate, coordinates: tuple[tuple[int]]) -> list[int]:
    time_row_2 = []
    if len(coordinates) > 100:
        time_row_2 = create_matrix_row(base_coordinate, coordinates[100:])
    coordinates = coordinates[:100]
    coordinates = '|'.join([f'{coordinate[0]},{coordinate[1]}' for coordinate in coordinates])
    base_coordinate = f'{base_coordinate[0]},{base_coordinate[1]}'
    url = f"https://api.routing.yandex.net/v2/distancematrix?origins={base_coordinate}&destinations={coordinates}&apikey={MATRIX_API_KEY}"
    response = requests.get(url).json()
    row = response["rows"][0]
    row = [element['duration']['value'] for element in row['elements']]
    row += time_row_2
    return row


def create_travel_matrix(*coordinates):
    matrix = []
    for coordinate in tqdm(coordinates):
        row = create_matrix_row(coordinate, coordinates)
        row = [i//60 for i in row]
        matrix.append(row)
    return matrix


def ask_yandex_for_time_matrix(locations: list[dict]):
    coordinates = []
    location_ids = []
    for location in locations:
        print(locations)
        coordinates.append((location['latitude'], location['longitude']))
        location_ids.append(location['id'])
    matrix = create_travel_matrix(*coordinates)
    data = {'location_ids': location_ids, 'time_matrix': matrix}
    return data


if __name__ == "__main__":
    with open('data', 'rb') as file:
        data = pickle.load(file)
    for row in data['time_matrix']:
        print(len(row))
    # print(data)
