import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import numpy as np
import os

def get_location_coordinates(location_name):
    """获取地名的经纬度坐标"""
    try:
        geolocator = Nominatim(user_agent="my_map_application")
        location = geolocator.geocode(location_name)
        if location:
            return [location.latitude, location.longitude]
        return None
    except GeocoderTimedOut:
        return None

def calculate_map_center_and_zoom(coordinates_list):
    """计算地图中心点和合适的缩放级别"""
    if not coordinates_list:
        return [0, 0], 2
    
    # 计算中心点
    center_lat = np.mean([coord[0] for coord in coordinates_list])
    center_lon = np.mean([coord[1] for coord in coordinates_list])
    
    # 计算坐标范围
    lat_range = max([coord[0] for coord in coordinates_list]) - min([coord[0] for coord in coordinates_list])
    lon_range = max([coord[1] for coord in coordinates_list]) - min([coord[1] for coord in coordinates_list])
    
    # 根据坐标范围确定缩放级别
    max_range = max(lat_range, lon_range)
    if max_range < 1:
        zoom = 10
    elif max_range < 5:
        zoom = 8
    elif max_range < 20:
        zoom = 6
    elif max_range < 60:
        zoom = 4
    else:
        zoom = 2
        
    return [center_lat, center_lon], zoom

def create_map_with_markers(filename):
    """读取文件并创建地图"""
    # 读取文件中的地名和解释
    with open(filename, 'r', encoding='utf-8') as file:
        location_lines = file.read().splitlines()
    
    # 收集所有有效的坐标
    valid_coordinates = []
    location_markers = []
    
    for line in location_lines:
        # 分割地名和解释
        parts = line.strip().split(' ', 1)
        location_name = parts[0]
        description = parts[1] if len(parts) > 1 else ''  # 如果没有解释则为空字符串
        
        coordinates = get_location_coordinates(location_name)
        if coordinates:
            valid_coordinates.append(coordinates)
            location_markers.append((coordinates, location_name, description))
    
    # 计算中心点和缩放级别
    center, zoom_level = calculate_map_center_and_zoom(valid_coordinates)
    
    # 创建地图，使用计算得到的中心点和缩放级别
    m = folium.Map(location=center, zoom_start=zoom_level)
    
    # 添加标记
    for coordinates, location_name, description in location_markers:
        # 如果有解释，则在弹出框中显示解释，否则显示地名
        popup_text = description if description else location_name
        folium.Marker(
            coordinates,
            # 将地名作为图标标签
            tooltip=location_name,
            # 将解释（如果有）或地名作为弹出内容
            popup=popup_text,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # 创建适合Notion嵌入的HTML文件
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ position: absolute; top: 0; bottom: 0; right: 0; left: 0; }}
        </style>
    </head>
    <body>
        {m._repr_html_()}
    </body>
    </html>
    """
    
    # 保存为HTML文件
    with open('locations_map.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

# 使用示例
if __name__ == "__main__":
    create_map_with_markers("locations.txt")