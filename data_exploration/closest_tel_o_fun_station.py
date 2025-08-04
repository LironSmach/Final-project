# -*- coding: utf-8 -*-
import requests
import pandas as pd
import math

def get_layer_data(layer_code=835, projection='itm'):
    url = "https://gisn.tel-aviv.gov.il/GisOpenData/service.asmx/GetLayer"
    params = {
        "layerCode": layer_code,
        "layerWhere": "",
        "xmin": "",
        "ymin": "",
        "xmax": "",
        "ymax": "",
        "projection": projection
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Fetched {len(data.get('features', []))} stations from layer {layer_code}")
        return data
    except Exception as e:
        print("❌ Error fetching layer:", e)
        return None

def convert_latlon_to_itm(lat, lon):
    url = "https://gisn.tel-aviv.gov.il/GisOpenData/service.asmx/GetItmFromGeo"
    params = {
        "longitude": lon,
        "latitude": lat
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        itm_coords = response.json()
        return float(itm_coords['x']), float(itm_coords['y'])
    except Exception as e:
        print("❌ Error converting lat/lon to ITM:", e)
        return None, None

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def find_closest_station(df, input_x, input_y, top_n=1):
    # Make sure x/y are numeric
    df['x'] = pd.to_numeric(df['x'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.dropna(subset=['x', 'y'])

    df['distance_m'] = df.apply(
        lambda row: calculate_distance(input_x, input_y, row['x'], row['y']),
        axis=1
    )
    closest = df.sort_values(by='distance_m').head(top_n)
    return closest

# === MAIN ===
if __name__ == "__main__":
    # Step 1: Fetch station data
    data = get_layer_data()
    if not data:
        exit()

    features = data.get("features", [])
    records = [f["attributes"] for f in features]
    df = pd.DataFrame(records)

    # Step 2: Ask for lat/lon input
    try:
        lat = float(input("Enter your latitude (WGS84): "))
        lon = float(input("Enter your longitude (WGS84): "))
    except ValueError:
        print("❌ Invalid input. Please enter numeric lat/lon values.")
        exit()

    # Step 3: Convert lat/lon to ITM
    x_input, y_input = convert_latlon_to_itm(lat, lon)
    if x_input is None or y_input is None:
        print("❌ Failed to convert coordinates.")
        exit()

    # Step 4: Find closest station
    closest = find_closest_station(df, x_input, y_input)

    # Step 5: Show result
    print("\n📍 Closest Tel-O-Fun station:")
    for idx, row in closest.iterrows():
        print(f"🚲 Station: {row.get('Shem_tachana')}")
        print(f"📍 Location: x={row.get('x')}, y={row.get('y')}")
        print(f"🟢 Available Bikes: {row.get('free_bikes')}")
        print(f"🅿️ Free Docks: {row.get('free_amudim')}")
        print(f"📏 Distance: {row.get('distance_m'):.1f} meters")
        print("-" * 40)
