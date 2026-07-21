import streamlit as st
import sqlite3
import os
import bcrypt
from datetime import datetime
from PIL import Image
import secrets
import base64

# Set page configuration
st.set_page_config(page_title="webpage - home page", page_icon="📝", layout="wide")

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

# Helper: Get image as Base64 data URL
def get_image_base64_url(image_name):
    path = os.path.join(UPLOAD_DIR, image_name)
    if not os.path.exists(path):
        path = os.path.join(UPLOAD_DIR, "default.jpg")
    
    # If even default.jpg is missing, return a placeholder
    if not os.path.exists(path):
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    
    ext = os.path.splitext(path)[1].replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{encoded}"

# Inject custom CSS to match the original Flask application styles exactly
st.markdown("""
<style>
/* Hide standard Streamlit header, footer, and default sidebars */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
[data-testid="stSidebar"] {display: none;}

/* Body styling */
.stApp {
    background-color: #fafafa !important;
    color: #333333 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Central container adjustment */
.main .block-container {
    padding-top: 0rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Navbar container */
.navbar-custom {
    background-color: #5f788a;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 4px;
    margin-bottom: 30px;
    margin-top: 15px;
}
.navbar-brand {
    color: white !important;
    font-size: 1.35rem;
    font-weight: 500;
    text-decoration: none;
    margin-right: 20px;
}
.nav-links-left, .nav-links-right {
    display: flex;
    align-items: center;
    gap: 15px;
}
.nav-links-left a, .nav-links-right a {
    color: #cbd5db !important;
    text-decoration: none;
    font-size: 1rem;
}
.nav-links-left a:hover, .nav-links-right a:hover {
    color: white !important;
    text-decoration: none;
}

/* Content box / Section card */
.content-section {
    background: #ffffff;
    padding: 20px;
    border: 1px solid #dddddd;
    border-radius: 3px;
    margin-bottom: 20px;
    color: #333333;
}

/* Heading styles */
h1, h2, h3, h4, h5, h6 {
    color: #444444 !important;
    font-weight: 500;
}

/* Article inside feed styling */
.article-title {
    color: #444444;
    text-decoration: none;
}
a.article-title:hover {
    color: #428bca !important;
    text-decoration: none;
}
.article-img {
    height: 65px;
    width: 65px;
    margin-right: 16px;
    border-radius: 50%;
}
.article-metadata {
    padding-bottom: 1px;
    margin-bottom: 8px;
    border-bottom: 1px solid #e3e3e3;
    font-size: 0.9rem;
}
.article-metadata a {
    color: #007bff;
    text-decoration: none;
    font-weight: bold;
}
.article-metadata a:hover {
    color: #0056b3;
    text-decoration: underline;
}

/* Streamlit forms container customization */
div[data-testid="stForm"] {
    background-color: #ffffff !important;
    border: 1px solid #dddddd !important;
    border-radius: 3px !important;
    padding: 20px !important;
    box-shadow: none !important;
}

/* Set background for buttons */
button[kind="secondaryFormSubmit"], button[kind="primaryFormSubmit"], button[kind="secondary"] {
    border-radius: 3px !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
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

# Check current page query parameter
current_page = st.query_params.get("page", "home")

# Logout logic
if current_page == "logout":
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = ""
    st.session_state['email'] = ""
    st.session_state['image_file'] = "default.jpg"
    st.query_params["page"] = "home"
    st.rerun()

# --- TOP NAVIGATION BAR ---
left_links = f"""
<a href="?page=home" target="_self" class="navbar-brand">Flask Blog</a>
<a href="?page=home" target="_self" style="margin-right: 15px;">Home</a>
<a href="?page=about" target="_self">About</a>
"""

if st.session_state['logged_in']:
    right_links = f"""
    <a href="?page=new_post" target="_self">New Post</a>
    <a href="?page=account" target="_self">Account</a>
    <a href="?page=logout" target="_self">Logout</a>
    """
else:
    right_links = f"""
    <a href="?page=login" target="_self">Login</a>
    <a href="?page=register" target="_self">Register</a>
    """

st.markdown(f"""
<div class="navbar-custom">
    <div class="nav-links-left">
        {left_links}
    </div>
    <div class="nav-links-right">
        {right_links}
    </div>
</div>
""", unsafe_allow_html=True)

# --- TWO-COLUMN LAYOUT ---
col_main, col_side = st.columns([8, 4])

# SIDEBAR (RIGHT COLUMN)
with col_side:
    st.markdown("""
    <div class="content-section">
        <h3 style="color: #444444; margin-top: 0; font-size: 1.5rem; font-weight: 500;">Our Sidebar</h3>
        <p style="color: #6c757d; font-size: 0.9rem; margin-bottom: 15px;">You can put any information here you'd like.</p>
        <ul style="list-style: none; padding-left: 0; margin-bottom: 0;">
            <li style="padding: 10px 15px; background-color: #ffffff; border: 1px solid #dddddd; margin-bottom: -1px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-size: 0.9rem; color: #495057;">Latest Posts</li>
            <li style="padding: 10px 15px; background-color: #ffffff; border: 1px solid #dddddd; margin-bottom: -1px; font-size: 0.9rem; color: #495057;">Announcements</li>
            <li style="padding: 10px 15px; background-color: #ffffff; border: 1px solid #dddddd; margin-bottom: -1px; font-size: 0.9rem; color: #495057;">Calendars</li>
            <li style="padding: 10px 15px; background-color: #ffffff; border: 1px solid #dddddd; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; font-size: 0.9rem; color: #495057;">etc</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# MAIN CONTENT (LEFT COLUMN)
with col_main:
    # --- VIEW: HOME ---
    if current_page == "home":
        posts_per_page = 4
        offset = (st.session_state['page'] - 1) * posts_per_page

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM post")
        total_posts = cursor.fetchone()[0]
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

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
            st.info("No blog posts found.")
        else:
            for post in posts:
                post_id, title, date_posted, content, author_id, author_name, author_avatar = post
                avatar_url = get_image_base64_url(author_avatar)
                
                # Format Date
                try:
                    date_obj = datetime.strptime(date_posted.split(".")[0], "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%B %d, %Y")
                except Exception:
                    formatted_date = date_posted

                post_html = f"""
                <div class="content-section" style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                    <img src="{avatar_url}" class="article-img" style="width: 65px; height: 65px; margin-right: 16px; border-radius: 50%;">
                    <div style="flex-grow: 1;">
                        <div class="article-metadata" style="border-bottom: 1px solid #e3e3e3; margin-bottom: 8px; padding-bottom: 4px; font-size: 0.9rem;">
                            <a href="?page=user_posts&username={author_name}" target="_self" style="color: #007bff; text-decoration: none; font-weight: bold; margin-right: 10px;">{author_name}</a>
                            <small style="color: #6c757d;">{formatted_date}</small>
                        </div>
                        <h2><a href="?page=post&post_id={post_id}" target="_self" style="color: #444444; text-decoration: none; font-weight: 500; font-size: 1.5rem;" class="article-title">{title}</a></h2>
                        <p class="article-content" style="white-space: pre-line; color: #333333; margin-top: 10px; font-size: 1rem;">{content}</p>
                    </div>
                </div>
                """
                st.markdown(post_html, unsafe_allow_html=True)
                
                # Edit/Delete buttons if logged in and author
                if st.session_state['logged_in'] and st.session_state['user_id'] == author_id:
                    btn_cols = st.columns([1.5, 1.5, 7])
                    with btn_cols[0]:
                        if st.button("Update", key=f"edit_btn_{post_id}"):
                            st.query_params["page"] = "edit_post"
                            st.query_params["post_id"] = str(post_id)
                            st.rerun()
                    with btn_cols[1]:
                        if st.button("Delete", key=f"del_btn_{post_id}"):
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM post WHERE id = ?", (post_id,))
                            conn.commit()
                            conn.close()
                            st.success("Post deleted successfully!")
                            st.rerun()
                    st.write("")

            # Pagination Controls
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.session_state['page'] > 1:
                    if st.button("Previous"):
                        st.session_state['page'] -= 1
                        st.rerun()
            with col2:
                st.write(f"<p style='text-align:center;'>Page {st.session_state['page']} of {max(1, total_pages)}</p>", unsafe_allow_html=True)
            with col3:
                if st.session_state['page'] < total_pages:
                    if st.button("Next"):
                        st.session_state['page'] += 1
                        st.rerun()

    # --- VIEW: ABOUT ---
    elif current_page == "about":
        st.markdown("""
        <div class="content-section">
            <h1 style="border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px;">About</h1>
            <h2 style="color: #444444; font-weight: 500;">tarak suravarapu</h2>
            <h4 style="color: #6c757d; font-weight: normal;">DEVELOPER</h4>
            <p style="color: #333333; margin-top: 15px; font-size: 1.1rem;">Developer of this website</p>
            <small style="color: #999999;">December 21, 2024</small>
        </div>
        """, unsafe_allow_html=True)

    # --- VIEW: LOGIN ---
    elif current_page == "login":
        st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Log In</h2>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Remember me")
            submit = st.form_submit_button("Login")
            
            if submit:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, email, password, image_file FROM user WHERE email = ?", (email,))
                user_info = cursor.fetchone()
                conn.close()
                
                if user_info and check_password(password, user_info[3]):
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user_info[0]
                    st.session_state['username'] = user_info[1]
                    st.session_state['email'] = user_info[2]
                    st.session_state['image_file'] = user_info[4]
                    st.success(f"Welcome back, {user_info[1]}!")
                    st.query_params["page"] = "home"
                    st.rerun()
                else:
                    st.error("Login unsuccessful. Please check email and password.")
        st.markdown("""
        <div style="margin-top: 15px; font-size: 0.9rem;">
            <a href="?page=reset_request" target="_self" style="color: #007bff; text-decoration: none;">Forgot Password?</a>
        </div>
        <hr style="border-top: 1px solid #e3e3e3; margin: 20px 0;">
        <div style="font-size: 0.9rem; color: #6c757d;">
            Need An Account? <a href="?page=register" target="_self" style="color: #007bff; text-decoration: none; margin-left: 5px;">Sign Up</a>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # --- VIEW: REGISTER ---
    elif current_page == "register":
        st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Register</h2>', unsafe_allow_html=True)
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(username) < 2 or len(username) > 20:
                    st.error("Username must be between 2 and 20 characters.")
                elif not username or not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
                    if cursor.fetchone():
                        st.error("Username already exists.")
                        conn.close()
                    else:
                        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
                        if cursor.fetchone():
                            st.error("Email already exists.")
                            conn.close()
                        else:
                            hashed_pwd = hash_password(password)
                            cursor.execute("INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                                           (username, email, hashed_pwd))
                            conn.commit()
                            conn.close()
                            st.success("Account created successfully! You are now able to log in.")
                            st.query_params["page"] = "login"
                            st.rerun()
        st.markdown("""
        <hr style="border-top: 1px solid #e3e3e3; margin: 20px 0;">
        <div style="font-size: 0.9rem; color: #6c757d;">
            Already Have An Account? <a href="?page=login" target="_self" style="color: #007bff; text-decoration: none; margin-left: 5px;">Sign In</a>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # --- VIEW: ACCOUNT ---
    elif current_page == "account":
        if not st.session_state['logged_in']:
            st.warning("Please log in to view this page.")
        else:
            st.markdown('<div class="content-section">', unsafe_allow_html=True)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT username, email, image_file FROM user WHERE id = ?", (st.session_state['user_id'],))
            user_info = cursor.fetchone()
            conn.close()
            
            db_username, db_email, db_image_file = user_info
            avatar_url = get_image_base64_url(db_image_file)
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 30px;">
                <img src="{avatar_url}" style="width: 125px; height: 125px; border-radius: 50%; margin-right: 20px;">
                <div>
                    <h2 style="margin: 0; font-size: 2.5rem; font-weight: 500;">{db_username}</h2>
                    <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 1.1rem;">{db_email}</p>
                </div>
            </div>
            <h3 style="border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Account Info</h3>
            """, unsafe_allow_html=True)
            
            with st.form("account_form"):
                new_username = st.text_input("Username", db_username)
                new_email = st.text_input("Email", db_email)
                uploaded_file = st.file_uploader("Update Profile Picture", type=["png", "jpg", "jpeg"])
                submit = st.form_submit_button("Update")
                
                if submit:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
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
                            pic_fn = db_image_file
                            if uploaded_file is not None:
                                random_hex = secrets.token_hex(8)
                                _, f_ext = os.path.splitext(uploaded_file.name)
                                pic_fn = random_hex + f_ext
                                picture_path = os.path.join(UPLOAD_DIR, pic_fn)
                                
                                image = Image.open(uploaded_file)
                                image.thumbnail((125, 125))
                                image.save(picture_path)
                                
                                if db_image_file != "default.jpg":
                                    old_pic_path = os.path.join(UPLOAD_DIR, db_image_file)
                                    if os.path.exists(old_pic_path):
                                        os.remove(old_pic_path)
                            
                            cursor.execute("UPDATE user SET username = ?, email = ?, image_file = ? WHERE id = ?",
                                           (new_username, new_email, pic_fn, st.session_state['user_id']))
                            conn.commit()
                            conn.close()
                            
                            st.session_state['username'] = new_username
                            st.session_state['email'] = new_email
                            st.session_state['image_file'] = pic_fn
                            
                            st.success("Your account has been updated!")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- VIEW: NEW POST ---
    elif current_page == "new_post":
        if not st.session_state['logged_in']:
            st.warning("Please log in to write posts.")
        else:
            st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">New Post</h2>', unsafe_allow_html=True)
            with st.form("new_post_form"):
                title = st.text_input("Title")
                content = st.text_area("Content", height=200)
                submit = st.form_submit_button("Publish")
                
                if submit:
                    if not title or not content:
                        st.error("Please enter a title and content.")
                    else:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO post (title, content, user_id, date_posted) VALUES (?, ?, ?, ?)",
                                       (title, content, st.session_state['user_id'], datetime.now()))
                        conn.commit()
                        conn.close()
                        st.success("Your post has been created!")
                        st.query_params["page"] = "home"
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- VIEW: EDIT POST ---
    elif current_page == "edit_post":
        post_id = int(st.query_params.get("post_id", 0))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, content, user_id FROM post WHERE id = ?", (post_id,))
        post_info = cursor.fetchone()
        conn.close()
        
        if not post_info:
            st.error("Post not found.")
        elif post_info[2] != st.session_state['user_id']:
            st.error("You are not authorized to edit this post.")
        else:
            st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Update Post</h2>', unsafe_allow_html=True)
            with st.form("edit_post_form"):
                title = st.text_input("Title", post_info[0])
                content = st.text_area("Content", post_info[1], height=200)
                submit = st.form_submit_button("Update")
                
                if submit:
                    if not title or not content:
                        st.error("Please enter a title and content.")
                    else:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE post SET title = ?, content = ? WHERE id = ?", (title, content, post_id))
                        conn.commit()
                        conn.close()
                        st.success("Post updated successfully!")
                        st.query_params["page"] = "home"
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- VIEW: VIEW DETAILED POST ---
    elif current_page == "post":
        post_id = int(st.query_params.get("post_id", 0))
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.image_file
            FROM post
            JOIN user ON post.user_id = user.id
            WHERE post.id = ?
        """, (post_id,))
        post = cursor.fetchone()
        conn.close()
        
        if not post:
            st.error("Post not found.")
        else:
            post_id, title, date_posted, content, author_id, author_name, author_avatar = post
            avatar_url = get_image_base64_url(author_avatar)
            
            try:
                date_obj = datetime.strptime(date_posted.split(".")[0], "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%B %d, %Y")
            except Exception:
                formatted_date = date_posted
            
            post_html = f"""
            <div class="content-section" style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                <img src="{avatar_url}" class="article-img" style="width: 65px; height: 65px; margin-right: 16px; border-radius: 50%;">
                <div style="flex-grow: 1;">
                    <div class="article-metadata" style="border-bottom: 1px solid #e3e3e3; margin-bottom: 8px; padding-bottom: 4px; font-size: 0.9rem;">
                        <a href="?page=user_posts&username={author_name}" target="_self" style="color: #007bff; text-decoration: none; font-weight: bold; margin-right: 10px;">{author_name}</a>
                        <small style="color: #6c757d;">{formatted_date}</small>
                    </div>
                    <h2 style="color: #444444; margin: 0; font-size: 2rem; font-weight: 500;">{title}</h2>
                    <p class="article-content" style="white-space: pre-line; color: #333333; margin-top: 15px; font-size: 1.1rem;">{content}</p>
                </div>
            </div>
            """
            st.markdown(post_html, unsafe_allow_html=True)
            
            if st.session_state['logged_in'] and st.session_state['user_id'] == author_id:
                btn_cols = st.columns([1.5, 1.5, 7])
                with btn_cols[0]:
                    if st.button("Update", key=f"edit_btn_det_{post_id}"):
                        st.query_params["page"] = "edit_post"
                        st.query_params["post_id"] = str(post_id)
                        st.rerun()
                with btn_cols[1]:
                    if st.button("Delete", key=f"del_btn_det_{post_id}"):
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM post WHERE id = ?", (post_id,))
                        conn.commit()
                        conn.close()
                        st.success("Post deleted successfully!")
                        st.query_params["page"] = "home"
                        st.rerun()

    # --- VIEW: USER SPECIFIC POSTS ---
    elif current_page == "user_posts":
        username_filter = st.query_params.get("username", "")
        
        posts_per_page = 4
        offset = (st.session_state['page'] - 1) * posts_per_page
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE username = ?", (username_filter,))
        user_row = cursor.fetchone()
        
        if not user_row:
            st.error(f"User {username_filter} not found.")
            conn.close()
        else:
            user_id_filter = user_row[0]
            
            cursor.execute("SELECT COUNT(*) FROM post WHERE user_id = ?", (user_id_filter,))
            total_posts = cursor.fetchone()[0]
            total_pages = (total_posts + posts_per_page - 1) // posts_per_page
            
            cursor.execute("""
                SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.image_file
                FROM post
                JOIN user ON post.user_id = user.id
                WHERE post.user_id = ?
                ORDER BY post.date_posted DESC
                LIMIT ? OFFSET ?
            """, (user_id_filter, posts_per_page, offset))
            posts = cursor.fetchall()
            conn.close()
            
            st.markdown(f"<h1 style='border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;'>Posts by {username_filter} ({total_posts})</h1>", unsafe_allow_html=True)
            
            if not posts:
                st.info("No posts found for this user.")
            else:
                for post in posts:
                    post_id, title, date_posted, content, author_id, author_name, author_avatar = post
                    avatar_url = get_image_base64_url(author_avatar)
                    
                    try:
                        date_obj = datetime.strptime(date_posted.split(".")[0], "%Y-%m-%d %H:%M:%S")
                        formatted_date = date_obj.strftime("%B %d, %Y")
                    except Exception:
                        formatted_date = date_posted
                    
                    post_html = f"""
                    <div class="content-section" style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                        <img src="{avatar_url}" class="article-img" style="width: 65px; height: 65px; margin-right: 16px; border-radius: 50%;">
                        <div style="flex-grow: 1;">
                            <div class="article-metadata" style="border-bottom: 1px solid #e3e3e3; margin-bottom: 8px; padding-bottom: 4px; font-size: 0.9rem;">
                                <a href="?page=user_posts&username={author_name}" target="_self" style="color: #007bff; text-decoration: none; font-weight: bold; margin-right: 10px;">{author_name}</a>
                                <small style="color: #6c757d;">{formatted_date}</small>
                            </div>
                            <h2><a href="?page=post&post_id={post_id}" target="_self" style="color: #444444; text-decoration: none; font-weight: 500; font-size: 1.5rem;" class="article-title">{title}</a></h2>
                            <p class="article-content" style="white-space: pre-line; color: #333333; margin-top: 10px; font-size: 1rem;">{content}</p>
                        </div>
                    </div>
                    """
                    st.markdown(post_html, unsafe_allow_html=True)
                    
                    if st.session_state['logged_in'] and st.session_state['user_id'] == author_id:
                        btn_cols = st.columns([1.5, 1.5, 7])
                        with btn_cols[0]:
                            if st.button("Update", key=f"edit_btn_usr_{post_id}"):
                                st.query_params["page"] = "edit_post"
                                st.query_params["post_id"] = str(post_id)
                                st.rerun()
                        with btn_cols[1]:
                            if st.button("Delete", key=f"del_btn_usr_{post_id}"):
                                conn = sqlite3.connect(DB_PATH)
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM post WHERE id = ?", (post_id,))
                                conn.commit()
                                conn.close()
                                st.success("Post deleted successfully!")
                                st.rerun()
                        st.write("")
                
                # Pagination controls for user posts
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.session_state['page'] > 1:
                        if st.button("Previous", key="prev_usr"):
                            st.session_state['page'] -= 1
                            st.rerun()
                with col2:
                    st.write(f"<p style='text-align:center;'>Page {st.session_state['page']} of {max(1, total_pages)}</p>", unsafe_allow_html=True)
                with col3:
                    if st.session_state['page'] < total_pages:
                        if st.button("Next", key="next_usr"):
                            st.session_state['page'] += 1
                            st.rerun()

    # --- VIEW: REQUEST RESET ---
    elif current_page == "reset_request":
        st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Reset Password</h2>', unsafe_allow_html=True)
        with st.form("reset_request_form"):
            reset_email = st.text_input("Email")
            submit = st.form_submit_button("Request Password Reset")
            
            if submit:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM user WHERE email = ?", (reset_email,))
                user_info = cursor.fetchone()
                conn.close()
                
                if user_info is None:
                    st.error("No account with that email! You must register first.")
                else:
                    st.success("Password reset request submitted successfully!")
                    token = f"simulated_token_{user_info[0]}"
                    reset_link = f"?page=reset_password&token={token}&user_id={user_info[0]}"
                    st.info("Since email servers are not active on Streamlit Cloud without setup, here is your password reset link:")
                    st.markdown(f'<a href="{reset_link}" target="_self" style="color: #007bff; font-weight: bold;">Reset Password Link</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- VIEW: RESET PASSWORD ---
    elif current_page == "reset_password":
        token = st.query_params.get("token", "")
        user_id = int(st.query_params.get("user_id", 0))
        
        if not token or not user_id:
            st.error("Invalid or expired password reset link.")
        else:
            st.markdown('<div class="content-section"><h2 style="margin-top: 0; border-bottom: 1px solid #e3e3e3; padding-bottom: 10px; margin-bottom: 20px; font-weight: 500;">Reset Password</h2>', unsafe_allow_html=True)
            with st.form("reset_password_form"):
                new_password = st.text_input("New Password", type="password")
                confirm_new_password = st.text_input("Confirm New Password", type="password")
                submit = st.form_submit_button("Reset Password")
                
                if submit:
                    if new_password != confirm_new_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        hashed_pwd = hash_password(new_password)
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE user SET password = ? WHERE id = ?", (hashed_pwd, user_id))
                        conn.commit()
                        conn.close()
                        st.success("Your password has been updated! You are now able to log in.")
                        st.query_params["page"] = "login"
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
