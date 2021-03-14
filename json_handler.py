import json
import os

def save_data(dirs, title, data):
    if not os.path.isdir(dirs):
        os.makedirs(dirs)
    with open(dirs+title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    f.close()

def load_data(title):
    f = open(title, encoding='utf-8')
    response = json.load(f)
    f.close()
    return response