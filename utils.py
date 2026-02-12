import json
import os
import hashlib
from datetime import datetime
from PIL import Image

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ITEMS_FILE = os.path.join(DATA_DIR, "items.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

def init_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    if not os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "w") as f:
            json.dump([], f)

def load_users():
    init_data()
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_items():
    init_data()
    with open(ITEMS_FILE, "r") as f:
        return json.load(f)

def save_items(items):
    with open(ITEMS_FILE, "w") as f:
        json.dump(items, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, contact_info):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    users[username] = {
        "password": hash_password(password),
        "contact_info": contact_info
    }
    save_users(users)
    return True, "User registered successfully"

def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

def save_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None
    init_data()
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(uploaded_file.read()).hexdigest()[:8]}{file_extension}"
    uploaded_file.seek(0) # Reset pointer
    file_path = os.path.join(IMAGES_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def get_user_contact(username):
    users = load_users()
    return users.get(username, {}).get("contact_info", "No contact info")
