# Flask Blog Application

A fully-featured blogging platform built with Python using the Flask micro-framework, SQLite/PostgreSQL databases, and Docker containerization.

## Features

- **User Authentication**: Secure registration, login, logout, and password hashing (using Flask-Bcrypt).
- **Post Management**: Create, read, update, and delete blog posts.
- **User Profiles**: Custom profile pictures (automatic cropping and resizing using Pillow) and profile updates.
- **Pagination**: Interactive pagination for navigating home posts and user-specific posts.
- **Password Reset**: Secure token-based password reset links emailed to users (using `itsdangerous` tokens and Gmail SMTP integration).
- **Deployment Ready**: Fully configured for containerized deployments with a production-ready `Dockerfile` and Gunicorn WSGI server.

---

## Local Setup

### 1. Prerequisites
- Python 3.11 or newer

### 2. Installation
Clone the repository (if not already done) and enter the directory:
```bash
git clone https://github.com/Tarak098/FLASK-PROJECT.git
cd FLASK-PROJECT
```

Create a virtual environment and activate it:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template configuration file:
```bash
cp .env.example .env
```
Open `.env` and fill in your details:
- `SECRET_KEY`: Set a secure secret key for session signing.
- `DATABASE_URL`: Set a database URI (leave blank to default to SQLite `site.db`).
- `EMAIL_USER`: Your Gmail address (required for password resets).
- `EMAIL_PASS`: Your Gmail App Password (required for password resets).

### 4. Running the Application
Start the Flask development server:
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:5000`. The database will be created automatically on launch.

---

## Running with Docker

You can build and run the application inside a container locally:

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

## Production Deployment (e.g. on Render)

### 1. Database Setup
Since SQLite files are temporary on free hosting providers (e.g., Render, Railway), it is recommended to provision a PostgreSQL database:
1. Create a PostgreSQL Database on Render.
2. Copy the **External Database URL**.

### 2. Web Service Setup
1. Create a new **Web Service** on Render and link your GitHub repository.
2. Select **Docker** as the Runtime.
3. Add the following Environment Variables in the Render dashboard:
   - `DATABASE_URL` = *(Your PostgreSQL Database connection URL)*
   - `SECRET_KEY` = *(A secure random string)*
   - `EMAIL_USER` = *(Your Gmail address)*
   - `EMAIL_PASS` = *(Your Google App Password)*
4. Click **Deploy**. Render will automatically pull the code, compile the Docker container, run migrations, and publish the app!
