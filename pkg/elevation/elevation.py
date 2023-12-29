from math import radians, cos, sin, asin, sqrt
import math
import json
import requests


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in meter. Use 3956 for miles. Determines return value units.
    r = 6371000
    return c * r


def move_coordinates(lat, lon, vertical_distance, horizontal_distance):
    # Переводим градусы в радианы
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Радиус Земли (примерно)
    R = 6371000  # метр

    # Расчет новой широты
    new_lat_rad = math.asin(math.sin(lat_rad) * math.cos(vertical_distance/R) +
                            math.cos(lat_rad) * math.sin(vertical_distance/R) * math.cos(horizontal_distance/R))
    new_lat = math.degrees(new_lat_rad)

    # Расчет новой долготы
    new_lon_rad = lon_rad + math.atan2(math.sin(horizontal_distance/R) * math.sin(vertical_distance/R) * math.cos(lat_rad),
                                       math.cos(vertical_distance/R) - math.sin(lat_rad) * math.sin(new_lat_rad))
    new_lon = math.degrees(new_lon_rad)

    return new_lat, new_lon

# area измеряется в гектарах


def getElevationAngle(lat, lon, area):
    offset = area**0.5/2
    lat1, lon1 = move_coordinates(lat, lon, offset, offset)
    lat2, lon2 = move_coordinates(lat, lon, -offset, -offset)

    lat3, lon3 = move_coordinates(lat, lon, -offset, offset)
    lat4, lon4 = move_coordinates(lat, lon, offset, -offset)

    response = requests.get(
        f'https://api.open-elevation.com/api/v1/lookup?locations={lat1},{lon1}|{lat2},{lon2}|{lat3},{lon3}|{lat4},{lon4}')
    data = json.loads(response.content)["results"]
    r1 = haversine(data[0]["latitude"], data[0]["longitude"],
                   data[1]["latitude"], data[1]["longitude"])
    r2 = haversine(data[0]["latitude"], data[0]["longitude"],
                   data[1]["latitude"], data[1]["longitude"])
    return min(max((max(data[0]["elevation"], data[1]["elevation"]) - min(data[0]["elevation"], data[1]["elevation"]))/r1,
               (max(data[2]["elevation"], data[3]["elevation"]) - min(data[2]["elevation"], data[3]["elevation"]))/r2), 0.1)
