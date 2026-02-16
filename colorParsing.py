# colorParsing.py
import json

FIGMA_TO_ANDROID_CONTEXT = {
    "fills": "android:background",
    "strokes": "android:strokeColor",
    "background": "android:background",
    "backgroundColor": "android:background",
    "color": "android:textColor",
    "textStyle": "android:textColor",
    "effects": "android:shadowColor",
    "tint": "android:tint",
    "overlay": "android:tint",
}


def rgbaToHex(r, g, b, a):
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    a = round(a * 255)
    
    if a == 255:
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    else:
        return "#{:02x}{:02x}{:02x}{:02x}".format(a, r, g, b)

def extract_colors(obj, current_id=None, context_path=None, colors=None):
    if colors is None:
        colors = {}

    if context_path is None:
        context_path = []

    if isinstance(obj, dict):
        if "id" in obj:
            current_id = obj["id"]

        for key, value in obj.items():
            if key == "color" and isinstance(value, dict):
                context = determine_context(context_path)
                c = value
                hexcode = rgbaToHex(
                    c.get("r", 0), c.get("g", 0), c.get("b", 0), c.get("a", 0)
                )
                if current_id:
                    if current_id not in colors:
                        colors[current_id] = {}
                    colors[current_id][context] = hexcode
            else:
                extract_colors(value, current_id, context_path + [key], colors)

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            extract_colors(v, current_id, context_path + [str(i)], colors)

    return colors


def determine_context(context_path):
    for key in reversed(context_path):
        if key in FIGMA_TO_ANDROID_CONTEXT:
            return FIGMA_TO_ANDROID_CONTEXT[key]
    return "android:background"  # Default context


def get_color_mapping(json_path="figma_design.json"):
    with open(json_path, "r") as f:
        data = json.load(f)
    return extract_colors(data)
