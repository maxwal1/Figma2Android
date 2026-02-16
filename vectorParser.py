import os
import json
import re
from colorParsing import get_color_mapping, rgbaToHex
from component_mapping import get_xml_tag

def get_path_bounds(path_data):
    if not path_data:
        return 0, 0, 0, 0
    
    #regex för att hitta alla nummer i path data
    numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", path_data)
    
    if not numbers:
        return 0, 0, 0, 0
    
    flyttal = [float(num) for num in numbers]
    
    #lagras som x1, y1, x2, y2, ...
    x_vals = flyttal[0::2]  #jämna index är x-koordinater
    y_vals = flyttal[1::2]  #udda index är y-koordinater

    if not x_vals or not y_vals:
        return 0, 0, 0, 0
    
    return min(x_vals), max(x_vals), min(y_vals), max(y_vals)

def generate_vector_drawable(node_id, node, fills, strokes, node_name, width, height): 
    
    # Mapp för drawables
    output_dir = os.path.join(os.getcwd(), "res", "drawable")
    resource_name = "ic_" + node_name.lower().replace(" ", "_").replace("-", "_")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        print("Vector drawable output directory created at:" + output_dir)
    except OSError as e:
        print(f"Error creating directory {output_dir}: {e}")
        return None
         
         
    file_path = os.path.join(output_dir, f"{resource_name}.xml")
    
    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="{round(width, 2)}dp"
    android:height="{round(height, 2)}dp"
    android:viewportWidth="{round(width, 2)}"
    android:viewportHeight="{round(height, 2)}">
"""

    stroke_width = node.get("strokeWeight", 0)
    
    fill_data_obj = fills[0] if fills and fills[0].get("type") == "SOLID" else None
    stroke_data_obj = strokes[0] if strokes and strokes[0].get("type") == "SOLID" else None
        
    if fill_data_obj and "color" in fill_data_obj:
        c = fill_data_obj["color"]
        fill_color = rgbaToHex(c.get("r", 0), c.get("g", 0), c.get("b", 0), c.get("a", 1))
    else:
        fill_color = "#00000000"  # Transparent if no fill

    if stroke_data_obj and "color" in stroke_data_obj:
        c = stroke_data_obj["color"]
        stroke_color = rgbaToHex(c.get("r", 0), c.get("g", 0), c.get("b", 0), c.get("a", 1))
    else:
        stroke_color = "#00000000"  # Transparent if no stroke
    
    all_paths = []
    
    for path in node.get("fillGeometry", []):
        all_paths.append(path.get("path", ""))
    
    if stroke_color != "#00000000":
        for path in node.get("strokeGeometry", []):
            all_paths.append(path.get("path", ""))
            
    #sätter till positiv och negativ oändlighet för jämförelse
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    has_paths = False
    
    for p in all_paths:
        if p:
            p_min_x, p_max_x, p_min_y, p_max_y = get_path_bounds(p)
            min_x = min(min_x, p_min_x)
            max_x = max(max_x, p_max_x)
            min_y = min(min_y, p_min_y)
            max_y = max(max_y, p_max_y)
            has_paths = True
            
    if has_paths and (max_x >= min_x) and (max_y >= min_y):
        calculated_width = max_x - min_x
        calculated_height = max_y - min_y
        
        if calculated_width > 0:
            width = calculated_width
        if calculated_height > 0:
            height = calculated_height
        
        #avstånd för att flytta alla paths så att de börjar vid (0,0)
        new_x_offset = -min_x
        new_y_offset = -min_y
    
    else:
        new_x_offset = 0
        new_y_offset = 0
        
    #säkerställer att bredd och höjd inte blir noll
    if width <= 0.1:
        width = 1.0
    if height <= 0.1:
        height = 1.0
        
    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="{round(width, 2)}dp"
    android:height="{round(height, 2)}dp"
    android:viewportWidth="{round(width, 2)}"
    android:viewportHeight="{round(height, 2)}">
    <group
        android:translateX="{round(new_x_offset, 2)}"
        android:translateY="{round(new_y_offset, 2)}">
"""
    
    for path in node.get("fillGeometry", []):
        path_data = path.get("path", "")
        if path_data:
            xml_content += f"""
    <path
        android:pathData="{path_data}"
        android:fillColor="{fill_color}"/>
"""        
    if stroke_color != "#00000000":
        for path in node.get("strokeGeometry", []):
            path_data = path.get("path", "")
            xml_content += f"""
        <path
            android:pathData="{path_data}"
            android:fillColor="{stroke_color}"/>
"""
        
    xml_content += "</group>\n</vector>\n"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return resource_name
    except IOError as e:
        print(f"Error writing vector drawable file to {file_path}: {e}")
        return None

def get_vector_resource_name(child_node, colors):
    node_tag = get_xml_tag(child_node.get("type"))
    has_geometry = "fillGeometry" in child_node or "strokeGeometry" in child_node
    
    if node_tag == "ImageView" and has_geometry:
        bounds = child_node.get("absoluteBoundingBox", {})
        width = bounds.get("width", 0)
        height = bounds.get("height", 0)
        
        resource_name = generate_vector_drawable(
            child_node.get("id"),
            child_node,
            child_node.get("fills", []),
            child_node.get("strokes", []),
            child_node.get("name"),
            width,
            height
        )
        return resource_name
    return None