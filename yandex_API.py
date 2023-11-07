import requests
from settings import COORDINATES_API_KEY, MATRIX_API_KEY
import pickle


def request_coordinates(adress):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={COORDINATES_API_KEY}&geocode={adress}&format=json"
    response = requests.get(url).json()
    coordinates = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
    print(coordinates)
    return coordinates


def create_matrix_row(base_coordinate, coordinates: tuple[tuple[str]]) -> list[int]:
    time_row_2 = []
    if len(coordinates) > 100:
        time_row_2 = create_matrix_row(base_coordinate, coordinates[100:])
    coordinates = coordinates[:100]
    coordinates = '|'.join([','.join(coordinate[::-1]) for coordinate in coordinates])
    base_coordinate = ','.join(base_coordinate[::-1])
    url = f"https://api.routing.yandex.net/v2/distancematrix?origins={base_coordinate}&destinations={coordinates}&apikey={MATRIX_API_KEY}"
    response = requests.get(url).json()
    row = response["rows"][0]
    row = [element['duration']['value'] for element in row['elements']]
    row += time_row_2
    return row


def create_travel_matrix(*coordinates):
    matrix = []
    for coordinate in coordinates:
        row = create_matrix_row(coordinate, coordinates)
        matrix.append(row)
    return matrix
    # with open("data.json", "w") as file:
    #     json.dump(response, file, indent=4, ensure_ascii=False)


def ask_yandex_for_time_matrix(*address_list: str):
    coordinates = []
    for address in address_list:
        coordinates.append(request_coordinates(address))
    matrix = create_travel_matrix(*coordinates)
    data = {'address_list': address_list, 'time_matrix': matrix}
    with open('data', 'wb') as file:
        pickle.dump(data, file)


if __name__ == "__main__":
    with open('data', 'rb') as file:
        data = pickle.load(file)
    for row in data['time_matrix']:
        print(len(row))
    # print(data)
