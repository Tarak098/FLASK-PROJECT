import unittest
from flask1 import create_app, db
from flask1.models import User, Post

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Use a temporary in-memory database for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def test_pages_load(self):
        # Homepage
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # About
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'tarak suravarapu', response.data)

    def test_registration_and_login(self):
        # Register user
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'submit': 'sign up'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
            
        # Login user
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123',
            'submit': 'login'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account', response.data)
        self.assertIn(b'Logout', response.data)

    def test_password_reset_flow(self):
        # Register user first so the email exists in DB
        self.client.post('/register', data={
            'username': 'resetuser',
            'email': 'reset@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'submit': 'sign up'
        }, follow_redirects=True)
        
        # Test password reset request page submits successfully without 500 error
        response = self.client.post('/reset_password', data={
            'email': 'reset@example.com',
            'submit': 'Request Password Reset'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unable to send password reset email', response.data)

if __name__ == '__main__':
    unittest.main()
