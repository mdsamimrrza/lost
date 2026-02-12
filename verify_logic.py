import utils
import os
import io
import shutil

# Setup clean environment for testing
print("Setting up test environment...")
if os.path.exists("data_test"):
    shutil.rmtree("data_test")
    
# Mock DATA_DIR in utils (monkey patching for test)
utils.DATA_DIR = "data_test"
utils.USERS_FILE = os.path.join(utils.DATA_DIR, "users.json")
utils.ITEMS_FILE = os.path.join(utils.DATA_DIR, "items.json")
utils.IMAGES_DIR = os.path.join(utils.DATA_DIR, "images")

# 1. Test Init
print("Testing initialization...")
utils.init_data()
assert os.path.exists(utils.DATA_DIR)
assert os.path.exists(utils.USERS_FILE)
assert os.path.exists(utils.ITEMS_FILE)
print("Initialization passed.")

# 2. Test Registration
print("Testing registration...")
success, msg = utils.register_user("testuser", "password123", "test@example.com")
assert success == True
success, msg = utils.register_user("testuser", "password123", "other@example.com")
assert success == False # Duplicate user
print("Registration passed.")

# 3. Test Authentication
print("Testing authentication...")
assert utils.authenticate_user("testuser", "password123") == True
assert utils.authenticate_user("testuser", "wrongpassword") == False
assert utils.authenticate_user("nonexistent", "password123") == False
print("Authentication passed.")

# 4. Test Item Handling
print("Testing item handling...")
items = utils.load_items()
assert len(items) == 0
new_item = {
    "id": 1,
    "title": "Lost Keys",
    "type": "Lost",
    "description": "Keys with a blue keychain",
    "location": "Park",
    "date": "2023-10-27",
    "image_path": None,
    "owner": "testuser",
    "status": "Active"
}
items.append(new_item)
utils.save_items(items)
loaded_items = utils.load_items()
assert len(loaded_items) == 1
assert loaded_items[0]["title"] == "Lost Keys"
print("Item handling passed.")

# 5. Test Image Save
print("Testing image save...")
mock_file = io.BytesIO(b"fake image content")
mock_file.name = "test_image.png"
path = utils.save_uploaded_image(mock_file)
assert path is not None
assert os.path.exists(path)
assert path.startswith(os.path.join(utils.DATA_DIR, "images"))
print("Image save passed.")

# Cleanup
# shutil.rmtree("data_test") # Commented out to inspect if needed
print("All tests passed!")
