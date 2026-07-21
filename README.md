# Flask Blog Application (with Streamlit & Flask Interfaces)

A fully-featured blogging platform built with Python. This project co-exists with two web interfaces: a traditional **Flask web app** (using HTML/CSS templates) and a modern **Streamlit dashboard** (ideal for immediate cloud deployment on Streamlit Community Cloud). Both interfaces share the same SQLite database (`instance/site.db`).

## Features

- **User Authentication**: Secure registration, login, logout, and password hashing (using Bcrypt) across both Flask and Streamlit.
- **Post Management**: Create, read, update, and delete blog posts.
- **User Profiles**: Custom profile pictures (automatic cropping and resizing using Pillow) and profile updates.
- **Pagination**: Interactive pagination for navigating blog posts.
- **Password Reset**: Secure token-based password reset links emailed to users (using Gmail SMTP integration on Flask).
- **Deployment Ready**: Standard Docker configurations for production, plus immediate support for Streamlit Community Cloud deployment.

---

## 1. Streamlit Interface (Recommended for Quick Cloud Hosting)

Streamlit is the easiest way to run and deploy this application in the cloud for free.

### Run Streamlit Locally
Activate your virtual environment and run:
```bash
streamlit run streamlit_app.py
```
This opens the web app automatically at `http://localhost:8501`.

### Deploying to Streamlit Community Cloud (Free)
1. Push your code to GitHub.
2. Sign in to **[Streamlit Community Cloud](https://share.streamlit.io/)** using your GitHub account.
3. Click **New app** -> Select your **FLASK-PROJECT** repository.
4. Set the **Main file path** to `streamlit_app.py`.
5. Click **Deploy**. Your app will be live on a public URL in seconds!

---

## 2. Flask Interface (Traditional Web App)

### Run Flask Locally

Create a virtual environment, activate it, and install dependencies:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Copy the template configuration file:
```bash
cp .env.example .env
```
Open `.env` and fill in your details (`SECRET_KEY`, `EMAIL_USER`, `EMAIL_PASS`).

Start the Flask development server:
```bash
python run.py
```
Access the application at `http://127.0.0.1:5000`.

---

## 3. Running with Docker (Flask App)

You can build and run the Flask application inside a container locally:

1. **Build the Docker Image**:
   ```bash
   docker build -t flask-blog .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8000:8000 --env-file .env flask-blog
   ```
The app will be accessible at `http://localhost:8000`.

---

## 4. Production Deployment for Flask (e.g. on Render)

If deploying the Flask version to Render:
1. Create a PostgreSQL Database on Render.
2. Create a new **Web Service** on Render, linking your GitHub repository.
3. Select **Docker** as the Runtime.
4. Set environment variables `DATABASE_URL` (your PostgreSQL connection string), `SECRET_KEY`, `EMAIL_USER`, and `EMAIL_PASS`.
5. Deploy.
