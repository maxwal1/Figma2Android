import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

FIGMA_FILE_KEY = os.environ.get("URL_KEY")
FIGMA_API_TOKEN = os.environ.get("API_KEY")
OUTPUT_FILENAME = "figma_design.json"

url = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}?geometry=paths"
headers = {
    "X-Figma-Token": FIGMA_API_TOKEN
}

if not FIGMA_API_TOKEN:
    print("Error: Figma API token not found. Please set the API_KEY environment variable.")
    exit(1)

def API_Call():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Figma design sparad som {OUTPUT_FILENAME} i {os.getcwd()}")
        return True
    else:
        print(f"Fel {response.status_code}: {response.text}")
        return False
        
