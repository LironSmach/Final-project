# -*- coding: utf-8 -*-
import requests
import pandas as pd

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
        print(f"✅ Fetched {len(data.get('features', []))} records from layer {layer_code}")
        return data
    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)
    except Exception as e:
        print("❌ Unknown error:", e)
    return None

def print_station_data(data):
    features = data.get("features", [])
    for feature in features[:100]:  # Print first 100 records
        attrs = feature.get("attributes", {})
        print("📍 תחנה:", attrs.get("Shem_tachana"))
        print("🚲 אופניים זמינים:", attrs.get("free_bikes"))
        print("📍 קואורדינטות: (lat:", attrs.get("lat"), ", lon:", attrs.get("lon"), ")")
        print("-" * 40)

def export_to_csv(data, filename="layer_835_data.csv"):
    features = data.get("features", [])
    records = [f.get("attributes", {}) for f in features]
    df = pd.DataFrame(records)
    # Export CSV with utf-8-sig to support Hebrew in Excel
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"📁 Data exported to {filename}")

if __name__ == "__main__":
    data = get_layer_data()
    if data:
        print_station_data(data)
        export_to_csv(data)
    else:
        print("⚠️ No data returned.")
