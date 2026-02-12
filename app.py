import streamlit as st
import utils
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Lost & Found Platform", page_icon="🔍", layout="wide")

# Initialize Session State
if "user" not in st.session_state:
    st.session_state["user"] = None

def login_page():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if utils.authenticate_user(username, password):
            st.session_state["user"] = username
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")

def register_page():
    st.sidebar.title("Register")
    new_user = st.sidebar.text_input("New Username")
    new_pass = st.sidebar.text_input("New Password", type="password")
    contact = st.sidebar.text_input("Contact Info (Email/Phone)")
    if st.sidebar.button("Register"):
        success, msg = utils.register_user(new_user, new_pass, contact)
        if success:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
            
def logout():
    st.session_state["user"] = None
    st.rerun()

def main():
    st.title("🔍 Lost & Found Platform")

    # Authentication
    if st.session_state["user"]:
        st.sidebar.write(f"Welcome, **{st.session_state['user']}**!")
        if st.sidebar.button("Logout"):
            logout()
        
        # Navigation
        menu = ["Home", "Post Item", "My Items"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Home":
            show_home()
        elif choice == "Post Item":
            show_post_item()
        elif choice == "My Items":
            show_my_items()
            
    else:
        st.info("Please Login or Register to post items or contact owners.")
        auth_mode = st.sidebar.radio("Auth Mode", ["Login", "Register"])
        if auth_mode == "Login":
            login_page()
        else:
            register_page()
        
        # Show public home page even if not logged in
        show_home(public=True)

def show_home(public=False):
    st.header("Latest Listings")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search Items (Title/Description)")
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All", "Lost", "Found"])
        
    items = utils.load_items()
    
    # Logic to filter
    filtered_items = []
    for item in items:
        if filter_type != "All" and item['type'] != filter_type:
            continue
        if search_term and (search_term.lower() not in item['title'].lower() and search_term.lower() not in item['description'].lower()):
            continue
        filtered_items.append(item)
        
    # Display Items
    if not filtered_items:
        st.info("No items found.")
    else:
        for item in reversed(filtered_items): # Show newest first
            with st.container():
                st.markdown("---")
                c1, c2 = st.columns([1, 3])
                with c1:
                    if item.get("image_path"):
                        try:
                            st.image(item["image_path"], use_container_width=True)
                        except:
                            st.error("Image not found")
                    else:
                        st.text("No Image")
                with c2:
                    st.subheader(f"[{item['type']}] {item['title']}")
                    st.caption(f"Posted by {item['owner']} on {item['date']} | Location: {item['location']}")
                    st.write(item['description'])
                    
                    if not public:
                        if st.button(f"Contact Owner", key=f"contact_{item['id']}"):
                            contact = utils.get_user_contact(item['owner'])
                            st.success(f"Contact Info: {contact}")
                    else:
                        st.caption("Login to view contact info")

def show_post_item():
    st.header("Post a New Item")
    
    with st.form("post_item_form"):
        title = st.text_input("Item Title")
        itype = st.selectbox("Type", ["Lost", "Found"])
        description = st.text_area("Description")
        location = st.text_input("Location (City, Area, Place)")
        date_str = st.date_input("Date Lost/Found", datetime.today())
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
        
        submitted = st.form_submit_button("Post Item")
        
        if submitted:
            if not title or not description or not location:
                st.error("Please fill in all required fields.")
            else:
                image_path = None
                if uploaded_file:
                    image_path = utils.save_uploaded_image(uploaded_file)
                
                items = utils.load_items()
                new_item = {
                    "id": len(items) + 1,
                    "title": title,
                    "type": itype,
                    "description": description,
                    "location": location,
                    "date": str(date_str),
                    "image_path": image_path,
                    "owner": st.session_state["user"],
                    "status": "Active" # or Resolved
                }
                items.append(new_item)
                utils.save_items(items)
                st.success("Item posted successfully!")

def show_my_items():
    st.header("My Items")
    user = st.session_state["user"]
    items = utils.load_items()
    
    my_items = [i for i in items if i['owner'] == user]
    
    if not my_items:
        st.info("You haven't posted any items yet.")
    else:
        for item in my_items:
            with st.expander(f"[{item['type']}] {item['title']} ({item['status']})"):
                st.write(f"Description: {item['description']}")
                st.write(f"Location: {item['location']}")
                st.write(f"Date: {item['date']}")
                if item.get("image_path"):
                    st.image(item["image_path"], width=200)
                
                # Delete logic needs careful list manipulation or tracking via ID.
                # In Streamlit, deleting inside a loop can be tricky due to rerun.
                # We'll use a unique key for the button.
                if st.button("Delete Item", key=f"del_{item['id']}"):
                    items = [i for i in items if i['id'] != item['id']]
                    utils.save_items(items)
                    st.success("Item deleted!")
                    st.rerun()

if __name__ == "__main__":
    main()
