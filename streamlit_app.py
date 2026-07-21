import streamlit as st
import sqlite3
import os
import bcrypt
from datetime import datetime
from PIL import Image
import secrets

# Set page configuration
st.set_page_config(page_title="Flask Blog - Streamlit Interface", page_icon="📝", layout="centered")

DB_PATH = os.path.join("instance", "site.db")
UPLOAD_DIR = os.path.join("flask1", "static", "profile_pics")

# Database initialization
def init_db():
    os.makedirs("instance", exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(20) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        image_file VARCHAR(20) NOT NULL DEFAULT 'default.jpg',
        password VARCHAR(60) NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS post (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(80) NOT NULL,
        date_posted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper: Hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Helper: Check password
def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

# Initialize Session State variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'email' not in st.session_state:
    st.session_state['email'] = ""
if 'image_file' not in st.session_state:
    st.session_state['image_file'] = "default.jpg"
if 'page' not in st.session_state:
    st.session_state['page'] = 1

# Sidebar Navigation
st.sidebar.title("Flask Blog")
if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as **{st.session_state['username']}**")
    
    # Render user avatar
    avatar_path = os.path.join(UPLOAD_DIR, st.session_state['image_file'])
    if not os.path.exists(avatar_path):
        avatar_path = os.path.join(UPLOAD_DIR, "default.jpg")
    
    if os.path.exists(avatar_path):
        st.sidebar.image(Image.open(avatar_path), width=80)
    
    menu = ["Home", "Create Post", "Account Settings", "Log Out"]
else:
    menu = ["Home", "Login", "Register"]

choice = st.sidebar.radio("Navigate", menu)

# --- HOME VIEW ---
if choice == "Home":
    st.title("Blog Posts")
    
    # Pagination configuration
    posts_per_page = 4
    offset = (st.session_state['page'] - 1) * posts_per_page

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get total posts count
    cursor.execute("SELECT COUNT(*) FROM post")
    total_posts = cursor.fetchone()[0]
    total_pages = (total_posts + posts_per_page - 1) // posts_per_page
    
    # Fetch posts page
    cursor.execute("""
        SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.image_file
        FROM post
        JOIN user ON post.user_id = user.id
        ORDER BY post.date_posted DESC
        LIMIT ? OFFSET ?
    """, (posts_per_page, offset))
    posts = cursor.fetchall()
    conn.close()

    if not posts:
        st.info("No blog posts found. Register and create one!")
    else:
        for post in posts:
            post_id, title, date_posted, content, author_id, author_name, author_avatar = post
            
            # Format date
            try:
                date_obj = datetime.strptime(date_posted, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_posted, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    date_obj = date_posted
            
            formatted_date = date_obj.strftime("%B %d, %Y") if isinstance(date_obj, datetime) else date_posted

            with st.container():
                st.subheader(title)
                st.write(f"By **{author_name}** on *{formatted_date}*")
                st.write(content)
                
                # Check if logged in user is the author
                if st.session_state['logged_in'] and st.session_state['user_id'] == author_id:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit Post", key=f"edit_{post_id}"):
                            st.session_state['edit_post_id'] = post_id
                            st.session_state['edit_post_title'] = title
                            st.session_state['edit_post_content'] = content
                            st.switch_page("streamlit_app.py") # Triggers refresh
                    with col2:
                        if st.button("Delete Post", key=f"del_{post_id}"):
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM post WHERE id = ?", (post_id,))
                            conn.commit()
                            conn.close()
                            st.success("Post deleted successfully!")
                            st.rerun()
                st.markdown("---")

        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.session_state['page'] > 1:
                if st.button("Previous"):
                    st.session_state['page'] -= 1
                    st.rerun()
        with col2:
            st.write(f"Page {st.session_state['page']} of {max(1, total_pages)}")
        with col3:
            if st.session_state['page'] < total_pages:
                if st.button("Next"):
                    st.session_state['page'] += 1
                    st.rerun()

    # Edit Post Form (Overlay logic)
    if 'edit_post_id' in st.session_state:
        st.write("---")
        st.subheader("Edit Post")
        new_title = st.text_input("Title", st.session_state['edit_post_title'])
        new_content = st.text_area("Content", st.session_state['edit_post_content'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Changes"):
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE post SET title = ?, content = ? WHERE id = ?", 
                               (new_title, new_content, st.session_state['edit_post_id']))
                conn.commit()
                conn.close()
                st.success("Post updated successfully!")
                del st.session_state['edit_post_id']
                st.rerun()
        with col2:
            if st.button("Cancel"):
                del st.session_state['edit_post_id']
                st.rerun()

# --- CREATE POST VIEW ---
elif choice == "Create Post":
    st.title("Create a New Post")
    title = st.text_input("Title")
    content = st.text_area("Content", height=200)
    
    if st.button("Publish"):
        if not title or not content:
            st.error("Please fill in both title and content.")
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO post (title, content, user_id, date_posted) VALUES (?, ?, ?, ?)",
                           (title, content, st.session_state['user_id'], datetime.now()))
            conn.commit()
            conn.close()
            st.success("Post published successfully!")
            st.rerun()

# --- ACCOUNT SETTINGS VIEW ---
elif choice == "Account Settings":
    st.title("Account Settings")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, image_file FROM user WHERE id = ?", (st.session_state['user_id'],))
    user_info = cursor.fetchone()
    conn.close()
    
    username, email, image_file = user_info
    
    st.write("### Update Profile Info")
    new_username = st.text_input("Username", username)
    new_email = st.text_input("Email", email)
    
    # Picture upload
    uploaded_file = st.file_uploader("Update Profile Picture", type=["png", "jpg", "jpeg"])
    
    if st.button("Update"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check username / email uniqueness
        cursor.execute("SELECT id FROM user WHERE username = ? AND id != ?", (new_username, st.session_state['user_id']))
        if cursor.fetchone():
            st.error("Username already exists.")
            conn.close()
        else:
            cursor.execute("SELECT id FROM user WHERE email = ? AND id != ?", (new_email, st.session_state['user_id']))
            if cursor.fetchone():
                st.error("Email already exists.")
                conn.close()
            else:
                # Handle picture save if uploaded
                pic_fn = image_file
                if uploaded_file is not None:
                    random_hex = secrets.token_hex(8)
                    _, f_ext = os.path.splitext(uploaded_file.name)
                    pic_fn = random_hex + f_ext
                    picture_path = os.path.join(UPLOAD_DIR, pic_fn)
                    
                    # Open and resize
                    image = Image.open(uploaded_file)
                    image.thumbnail((125, 125))
                    image.save(picture_path)
                    
                    # Delete old image if not default
                    if image_file != "default.jpg":
                        old_pic_path = os.path.join(UPLOAD_DIR, image_file)
                        if os.path.exists(old_pic_path):
                            os.remove(old_pic_path)
                
                cursor.execute("UPDATE user SET username = ?, email = ?, image_file = ? WHERE id = ?",
                               (new_username, new_email, pic_fn, st.session_state['user_id']))
                conn.commit()
                conn.close()
                
                # Update Session State
                st.session_state['username'] = new_username
                st.session_state['email'] = new_email
                st.session_state['image_file'] = pic_fn
                st.success("Account updated successfully!")
                st.rerun()

# --- REGISTER VIEW ---
elif choice == "Register":
    st.title("Sign Up")
    reg_username = st.text_input("Username")
    reg_email = st.text_input("Email")
    reg_password = st.text_input("Password", type="password")
    reg_confirm = st.text_input("Confirm Password", type="password")
    
    if st.button("Sign Up"):
        if reg_password != reg_confirm:
            st.error("Passwords do not match.")
        elif not reg_username or not reg_email or not reg_password:
            st.error("Please fill in all fields.")
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check unique username
            cursor.execute("SELECT id FROM user WHERE username = ?", (reg_username,))
            if cursor.fetchone():
                st.error("Username already exists.")
                conn.close()
            else:
                # Check unique email
                cursor.execute("SELECT id FROM user WHERE email = ?", (reg_email,))
                if cursor.fetchone():
                    st.error("Email already exists.")
                    conn.close()
                else:
                    hashed_pwd = hash_password(reg_password)
                    cursor.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                                   (reg_username, reg_email, hashed_pwd))
                    conn.commit()
                    conn.close()
                    st.success("Account created successfully! Please log in.")

# --- LOGIN VIEW ---
elif choice == "Login":
    st.title("Log In")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, image_file FROM user WHERE email = ?", (login_email,))
        user_info = cursor.fetchone()
        conn.close()
        
        if user_info and check_password(login_password, user_info[3]):
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user_info[0]
            st.session_state['username'] = user_info[1]
            st.session_state['email'] = user_info[2]
            st.session_state['image_file'] = user_info[4]
            st.success(f"Welcome back, {user_info[1]}!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

# --- LOG OUT VIEW ---
elif choice == "Log Out":
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = ""
    st.session_state['email'] = ""
    st.session_state['image_file'] = "default.jpg"
    st.success("Logged out successfully!")
    st.rerun()
