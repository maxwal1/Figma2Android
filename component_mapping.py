FIGMA_TYPE_TO_XML_TAG = {
    
    "TEXT": "TextView",
    
    
    "GROUP": "androidx.constraintlayout.widget.ConstraintLayout",
    "FRAME": "androidx.constraintlayout.widget.ConstraintLayout",
    "COMPONENT": "androidx.constraintlayout.widget.ConstraintLayout",
    
    "RECTANGLE": "ImageView",
    "POLYGON": "ImageView",
    "REGULAR_POLYGON": "ImageView",
    "STAR": "ImageView",
    "LINE": "ImageView", 
    "ELLIPSE": "ImageView",
    "VECTOR": "ImageView",
    "SLICE": "ImageView",

}

def is_image_node(node):
    fills = node.get("fills", [])
    for fill in fills:
        if fill.get("type") == "IMAGE":
            return True
    return False


def get_xml_tag(node):
    if isinstance(node, str):
        figma_type = node
        is_image = False
    else:
        figma_type = node.get("type", "")
        is_image = is_image_node(node)
    
    normalized_type = figma_type.upper()
    
    #Om bildfil: gör om till TextView för placeholder
    if is_image:
        return "TextView"
    
    xml_tag = FIGMA_TYPE_TO_XML_TAG.get(normalized_type, "View")
    
    if xml_tag == "View" and normalized_type not in FIGMA_TYPE_TO_XML_TAG:
        print(f"Warning: Unrecognized Figma type '{figma_type}'. Defaulting to 'View'.")
        
    print(f"Figma type '{figma_type}' maps to XML tag '{xml_tag}'.")
    return xml_tag


