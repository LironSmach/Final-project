import requests
import pandas as pd
import folium

# API URL and parameters
url = "https://gisn.tel-aviv.gov.il/GisOpenData/service.asmx/GetLayer"
params = {
    "layerCode": "835",
    "layerWhere": "",
    "xmin": "",
    "ymin": "",
    "xmax": "",
    "ymax": "",
    "projection": "wgs84"
}

# Request data
response = requests.get(url, params=params)
data = response.json()

# Extract stations data
stations = [f['attributes'] for f in data['features']]

# Convert to DataFrame
df = pd.DataFrame(stations)

# Print top 10 stations by available bikes
print("🚲 Top 10 stations with most available bikes:")
print(df[['Shem_tachana', 'free_bikes', 'free_amudim']].sort_values(by='free_bikes', ascending=False).head(10))

# Create map centered on Tel Aviv
m = folium.Map(location=[32.08, 34.78], zoom_start=13)

# Add station markers to map
for idx, row in df.iterrows():
    name = row['Shem_tachana']
    bikes = row['free_bikes']
    slots = row['free_amudim']
    
    # Choose marker color based on bike availability
    if bikes >= 5:
        color = "green"
    elif bikes > 0:
        color = "orange"
    else:
        color = "red"
    
    popup = (
        f"{name}<br>"
        f"🟢 Available bikes: {bikes}<br>"
        f"⚪ Free slots: {slots}"
    )
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=popup
    ).add_to(m)

# Save map to HTML file
m.save("tel_o_fun_map.html")
print("📍 Map saved as tel_o_fun_map.html — open it in your browser.")
