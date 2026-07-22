# Flask Blog Application

A fully-featured blogging platform built with Python Flask, SQLAlchemy, Bootstrap, and custom CSS styling.

🌐 **Live Website**: [https://flask-project-4wkq.onrender.com](https://flask-project-4wkq.onrender.com)

---

## Features

- **User Authentication**: Secure registration, login, logout, and password hashing (using Bcrypt).
- **Post Management**: Create, read, update, and delete blog posts with author metadata.
- **User Profiles**: Custom profile picture uploads (automatic cropping and resizing via Pillow) and profile details management.
- **Pagination**: Interactive pagination for navigating blog posts.
- **Password Reset**: Token-based password reset links sent via email (Brevo HTTP API integration).
- **Production Ready**: Includes `Procfile`, `Dockerfile`, and `gunicorn` configurations deployed on Render.

---

## 1. Live Deployment

The live application is hosted on Render:
* **Web Application**: [https://flask-project-4wkq.onrender.com](https://flask-project-4wkq.onrender.com)
* **Login Page**: [https://flask-project-4wkq.onrender.com/login](https://flask-project-4wkq.onrender.com/login)

---

## 2. Running Locally

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
   Copy `.env.example` to `.env` and fill in your secrets (`SECRET_KEY`, `EMAIL_USER`, `EMAIL_PASS`).

5. **Run the Flask application**:
   ```bash
   python run.py
   ```
   Open your browser at **`http://127.0.0.1:5000`**.

---

## 3. Deploying to Cloud Hosts (Render / Railway / PythonAnywhere)

### Render Setup
1. Sign in to **[Render](https://render.com/)** and connect your GitHub account.
2. Click **New +** -> **Web Service** -> Select your **FLASK-PROJECT** repository.
3. Settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
4. Add Environment Variables:
   - `SECRET_KEY`
   - `EMAIL_USER` (your Brevo account email)
   - `EMAIL_PASS` (your Brevo API key starting with `xkeysib-...`)
5. Click **Create Web Service**.

---

## 4. Running with Docker

1. **Build the Docker Image**:
   ```bash
   docker build -t flask-blog .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 8000:8000 --env-file .env flask-blog
   ```
   Access at `http://localhost:8000`.
