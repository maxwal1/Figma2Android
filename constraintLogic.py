from vectorParser import get_path_bounds
import re


HORIZONTAL_CONSTRAINTS = {
    "LEFT": [' app:layout_constraintStart_toStartOf="parent"\n'],
    "RIGHT": [' app:layout_constraintEnd_toEndOf="parent"\n'],
    
    "LEFT_RIGHT": [' app:layout_constraintStart_toStartOf="parent"\n',
                   ' app:layout_constraintEnd_toEndOf="parent"\n'],
    
    "CENTER": [' app:layout_constraintStart_toStartOf="parent"\n',
               ' app:layout_constraintEnd_toEndOf="parent"\n'],
    
    "SCALE": [' app:layout_constraintStart_toStartOf="parent"\n',
               ' app:layout_constraintEnd_toEndOf="parent"\n']
}

VERTICAL_CONSTRAINTS = {
    "TOP": [' app:layout_constraintTop_toTopOf="parent"\n'],
    "BOTTOM": [' app:layout_constraintBottom_toBottomOf="parent"\n'],
    
    "TOP_BOTTOM": [' app:layout_constraintTop_toTopOf="parent"\n',
                   ' app:layout_constraintBottom_toBottomOf="parent"\n'],
    
    "CENTER": [' app:layout_constraintTop_toTopOf="parent"\n',
               ' app:layout_constraintBottom_toBottomOf="parent"\n'],
    
    "SCALE": [' app:layout_constraintTop_toTopOf="parent"\n',
               ' app:layout_constraintBottom_toBottomOf="parent"\n']
}

def get_view_dimensions(node):
    all_paths = []
    
    for path in node.get("fillGeometry", []):
        all_paths.append(path.get("path", ""))
    
    for path in node.get("strokeGeometry", []):
        all_paths.append(path.get("path", ""))
            
    if not all_paths:
        w = node.get("size", {}).get("x", 0)
        h = node.get("size", {}).get("y", 0)
        return w, h
            
    #boundingbox för paths
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
        w = max_x - min_x
        h = max_y - min_y
        
        if w <= 0.1:
            w = 1.0
        if h <= 0.1:
            h = 1.0
            
        return w, h
    else:
        return node.get("size", {}).get("x", 0), node.get("size", {}).get("y", 0)

def get_constraint_attributes(child_node, parent_bounds):
    constraint_attrs = ""
    
    bounds = child_node.get("absoluteBoundingBox", {})
    constraints = child_node.get("constraints", {})
    
    #förälderns dimensioner
    parent_x = parent_bounds.get("x", 0)
    parent_y = parent_bounds.get("y", 0)
    parent_w = parent_bounds.get("width", 0)
    parent_h = parent_bounds.get("height", 0)
    
    #barnets dimensioner
    view_w, view_h = get_view_dimensions(child_node)
    
    child_centerX = bounds.get("x", 0) + bounds.get("width", 0) / 2
    child_centerY = bounds.get("y", 0) + bounds.get("height", 0) / 2
    
    relative_centerX = child_centerX - parent_x
    relative_centerY = child_centerY - parent_y
    
    
    if child_node.get("type") == "TEXT":
        horizontal_type = child_node.get("style").get("textAlignHorizontal", "LEFT")
        vertical_type = child_node.get("style").get("textAlignVertical", "TOP")
        
    else: 
        horizontal_type = constraints.get("horizontal", "LEFT")
        vertical_type = constraints.get("vertical", "TOP")

    #Horisontella constraints (LEFT om typen saknas)
    constraint_attrs += "".join(HORIZONTAL_CONSTRAINTS.get(horizontal_type, HORIZONTAL_CONSTRAINTS["LEFT"]))
    
    #Horisontella constraints
    if horizontal_type in ["CENTER", "SCALE"]:
        if parent_w > 0:
            #bias = 0 -> vänster, bias = 0.5 -> center, bias = 1 -> höger
            bias = round(relative_centerX / parent_w, 2)
            if bias != 0.5:
                constraint_attrs += f' app:layout_constraintHorizontal_bias="{bias}"\n'
    
    elif horizontal_type == "RIGHT":        
        #margin från höger med rotation i åtanke
        margin_end = parent_w - (relative_centerX + view_w / 2)
        constraint_attrs += f' android:layout_marginEnd="{round(margin_end, 2)}dp"\n'
        
    else: 
        #margin från vänster med rotation i åtanke
        margin_start = relative_centerX - view_w / 2
        constraint_attrs += f' android:layout_marginStart="{round(margin_start, 2)}dp"\n'
        
    #Vertikala constraints (TOP om typen saknas)
    constraint_attrs += "".join(VERTICAL_CONSTRAINTS.get(vertical_type, VERTICAL_CONSTRAINTS["TOP"]))
        
    if vertical_type in ["CENTER", "SCALE"]:
        if parent_h > 0:
            bias = round(relative_centerY / parent_h, 2)
            if bias != 0.5:
                constraint_attrs += f' app:layout_constraintVertical_bias="{bias}"\n'
            
    elif vertical_type == "BOTTOM":
        #margin från botten med rotation i åtanke
        margin_bottom = parent_h - (relative_centerY + view_h / 2)
        constraint_attrs += f' android:layout_marginBottom="{round(margin_bottom, 2)}dp"\n'
        
    else: 
        #margin från toppen med rotation i åtanke
        margin_top = relative_centerY - view_h / 2
        constraint_attrs += f' android:layout_marginTop="{round(margin_top, 2)}dp"\n'
        
    return constraint_attrs

def get_size_attributes(child_node, xml_tag, parent_bounds):
    size_attrs = ""
    figma_type = child_node.get("type")
    
    if xml_tag == "TextView" and figma_type == "TEXT":
        #TextView får wrap_content
        size_attrs += ' android:layout_width="wrap_content"\n'
        size_attrs += ' android:layout_height="wrap_content"\n'
        return size_attrs
    
    w, h = get_view_dimensions(child_node)
    
    size_attrs += f' android:layout_width="{round(w, 2)}dp"\n'
    size_attrs += f' android:layout_height="{round(h, 2)}dp"\n'
    
    return size_attrs