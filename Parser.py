import json
from colorParsing import get_color_mapping
from component_mapping import get_xml_tag, is_image_node
from constraintLogic import get_constraint_attributes, get_size_attributes
from vectorParser import get_vector_resource_name
import os
import math

def slugify(name: str) -> str:#för skapande av filnamn utan mellanslag
    return name.lower().replace(" ", "_")

def get_layout_output_path(filename: str) -> str:#för skapande av layout mapp
    layout_dir = os.path.join(os.getcwd(), "res", "layout")
    os.makedirs(layout_dir, exist_ok=True)
    return os.path.join(layout_dir, filename)

def open_File():
    global colors
    colors = get_color_mapping()
    
    with open ('figma_design.json', 'r') as f:
        data = json.load(f)

        
    document=data.get("document", {})
    children=document.get("children", [])
        
    #hämtar första sidan
    Page=children[0] if children else {}
    noderna=Page.get("children", [])
    
    #hämtar den yttre förälderns dimensioner (rotnoden)
    root_bounds = {}

   ## print(data)
    Pages=data.get("document", {}).get("children", [])
    if not Pages:
        print("Error: Hittade inga pages i JSON-filen")
        return
    
    for page_index, page in enumerate(Pages):
            page_name = page.get("name", f"Page_{page_index}")
            print(f"\n=== Page {page_index}: {page_name} ===")
            filename = f"{slugify(page_name)}.xml"
    #hämtar den yttre förälderns dimensioner (rotnoden)
            root_node= page
            root_bounds=root_node.get("absoluteBoundingBox", {})
            root_node= page
            root_bounds=root_node.get("absoluteBoundingBox", {})
            noderna=page.get("children", [])#
            for node in noderna:
                # print(f"Nodnamn: {node.get('name')}, Nodtyp: {node.get('type')}")
                node_typ=node.get("type")
                node_name=node.get("name")      
                if node_typ=="FRAME":
                        print(f"Frame namn: {node_name}\n")
                        
                        used_ids = set()
                        
                        Output_file=node_to_xml(node, colors, root_bounds, used_ids, indent=0, is_root=True)
                        full_xml = '<?xml version="1.0" encoding="utf-8"?>\n' +  Output_file
                        xml_path = get_layout_output_path(filename)
                        with open(xml_path, "w", encoding="utf-8") as output:
                            output.write(full_xml)
                            print(f"XML fil skapad som Index.xml i")
                            
                else:
                        print(f"Error Det finns ingen Frame i JSON filen")  
    

 
  
def node_to_xml(node, colors, parent_bounds, used_ids, indent=0, is_root=False):
    figma_type = node.get("type")
    xml_tag = get_xml_tag(node)
    children = node.get("children", [])

    indent_str = " " * indent
    specific_attrs = get_tag_attributes(node, xml_tag, colors, used_ids)
    
    #hanterar barn som blir större än föräldern
    clip_attr = ' android:clipChildren="false"\n' if children else ""

    if is_root:
        constraint_attrs = ""
        size_attrs = ' android:layout_width="match_parent"\n  android:layout_height="match_parent"\n'
        xmlns_attrs = ' xmlns:android="http://schemas.android.com/apk/res/android"\n xmlns:app="http://schemas.android.com/apk/res-auto"\n'
    else:
        constraint_attrs = get_constraint_attributes(node, parent_bounds)
        size_attrs = get_size_attributes(node, xml_tag, parent_bounds)

        #Om ImageView har 0dp bredd eller höjd, sätt till wrap_content
        if xml_tag == "ImageView":
            if 'android_layout_width="0.0dp"' in size_attrs or 'android_layout_width="0p"' in size_attrs:
                size_attrs = size_attrs.replace(' android:layout_width="0.0dp"\n', ' android:layout_width="wrap_content"\n')
                size_attrs = size_attrs.replace(' android:layout_width="0p"\n', ' android:layout_width="wrap_content"\n')
                
            if 'android_layout_height="0.0dp"' in size_attrs or 'android_layout_height="0p"' in size_attrs:
                size_attrs = size_attrs.replace(' android:layout_height="0.0dp"\n', ' android:layout_height="wrap_content"\n')
                size_attrs = size_attrs.replace(' android:layout_height="0p"\n', ' android:layout_height="wrap_content"\n')            
                
        xmlns_attrs = ""
        
    #Alla attribut
    attrs_block = xmlns_attrs + constraint_attrs + specific_attrs + size_attrs + clip_attr

    if xml_tag == "androidx.constraintlayout.widget.ConstraintLayout" and children:
        # Opening tag
        xml = f'{indent_str}<{xml_tag}\n{attrs_block}{indent_str}>\n'

        # Recurse into children
        #För barnen används den nuvarande nodens (frame) bounding box som förälder
        current_bounds = node.get("absoluteBoundingBox", {})
        for child in children:
            xml += node_to_xml(child, colors, current_bounds, used_ids, indent + 2, is_root=False)

        # Closing tag
        xml += f'{indent_str}</{xml_tag}>\n'
        return xml

    else:
        # Leaf view (no children or not a container)
        xml = f'{indent_str}<{xml_tag}\n{attrs_block}{indent_str}/>\n'
        return xml
     
def get_tag_attributes(child_node, xml_tag, colors, used_ids):
    
    spec_attrs = ""
    
    node_id = child_node.get("id")
    name = child_node.get("name")
    name_id = name.replace(" ", "_").replace("-", "_").replace(".", "").replace(":","")
    counter = 1
    
    if name_id[0].isdigit():
        name_id = "id_"+name_id
    
    while name_id in used_ids:
        name_id = f"{name_id}_{counter}"
        counter += 1
        
    used_ids.add(name_id)
    
    spec_attrs += f' android:id="@+id/{name_id}"\n'
            
    roation_radians = child_node.get("rotation", 0)
    if roation_radians:
        degrees = math.degrees(roation_radians)
        spec_attrs += f'  android:rotation="{round(degrees, 2)}"\n'
    
    if node_id in colors:
        for android_attr, hexcode in colors[node_id].items():
            if xml_tag == "ImageView":
                continue  # Hoppa över bakgrund för ImageView
            
            if xml_tag == "TextView" and android_attr == "android:background":
                android_attr = "android:textColor"
                
            if is_image_node(child_node):
                continue
            
            spec_attrs += f'  {android_attr}="{hexcode}"\n'
            
    #Placeholder för bildfiler
    if is_image_node(child_node):
        spec_attrs += f'  android:text=" Insert image *{name}* here "\n'
        spec_attrs += f'  android:gravity="center"\n'
        spec_attrs += f'  android:background="#CCCCCC"\n' # ljusgrå bakgrund
        spec_attrs += f'  android:textColor="#666666"\n' # mörkgrå textfärg
        spec_attrs += f'  android:textStyle="italic"\n'
        spec_attrs += f'  android:textSize="16sp"\n'
            
    #hanterar textinnehåll
    if xml_tag == "TextView":
        text_content = child_node.get("characters")
        if text_content:
            escaped_text = text_content.replace('"', '//"').replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            spec_attrs += f'  android:text="{escaped_text}"\n'
            
        spec_attrs += f'  android:includeFontPadding="false"\n'
                        
        style = child_node.get("style", {})
        font_size = style.get("fontSize")
        if font_size:
            spec_attrs += f'  android:textSize="{round(font_size, 2)}sp"\n'
            
    #bild-/vectorlogik
    if xml_tag == "ImageView":
        resource_name = get_vector_resource_name(child_node, colors)
        if resource_name:
            spec_attrs += f'  android:src="@drawable/{resource_name}"\n'
        else:
            spec_attrs += f'  android:src="@drawable/ic_placeholder"\n'
    
    return spec_attrs
    