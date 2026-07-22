# Flask Blog Application

A fully-featured blogging platform built with Python Flask, SQLAlchemy, Bootstrap, and custom CSS styling.

## Features

- **User Authentication**: Secure registration, login, logout, and password hashing (using Bcrypt).
- **Post Management**: Create, read, update, and delete blog posts with author metadata.
- **User Profiles**: Custom profile picture uploads (automatic cropping and resizing via Pillow) and profile details management.
- **Pagination**: Interactive pagination for navigating blog posts.
- **Password Reset**: Token-based password reset links sent via email (SMTP).
- **Production Ready**: Includes `Procfile`, `Dockerfile`, and `gunicorn` configurations for free/easy cloud hosting (Render, PythonAnywhere, Railway, Docker).

---

## 1. Running Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Tarak098/FLASK-PROJECT.git
   cd FLASK-PROJECT
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   Copy `.env.example` to `.env` and fill in your secrets (e.g. `SECRET_KEY`, `EMAIL_USER`, `EMAIL_PASS`).

5. **Run the Flask application**:
   ```bash
   python run.py
   ```
   Open your browser at **`http://127.0.0.1:5000`**.

---

## 2. Deploying to Cloud Hosts (Render / Railway / PythonAnywhere)

### Option A: Render (Free Web Service)
1. Sign in to **[Render](https://render.com/)** and connect your GitHub account.
2. Click **New +** -> **Web Service** -> Select your **FLASK-PROJECT** repository.
3. Settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
4. Add Environment Variables (`SECRET_KEY`, `EMAIL_USER`, `EMAIL_PASS`).
5. Click **Create Web Service**. Your Flask app will be live on a public URL!

### Option B: PythonAnywhere (Free)
1. Sign up on **[PythonAnywhere](https://www.pythonanywhere.com/)**.
2. Open a bash console and clone your repository.
3. Create a Virtual Environment and install `requirements.txt`.
4. Under the **Web** tab, configure the WSGI file to point to `run.py` (`from run import app as application`).

---

## 3. Running with Docker

1. **Build the Docker Image**:
   ```bash
   docker build -t flask-blog .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 8000:8000 --env-file .env flask-blog
   ```
   Access at `http://localhost:8000`.
