"""
Unit tests for authentication functionality.

Tests user registration, login, logout, email confirmation,
and access control mechanisms.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import url_for
from tests import BaseTestCase
from app.models import User


class TestAuthRoutes(BaseTestCase):
    """Test cases for authentication routes."""
    
    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'username', response.data)
        self.assertIn(b'password', response.data)
    
    def test_register_page_loads(self):
        """Test that the registration page loads correctly."""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Account', response.data)
        self.assertIn(b'username', response.data)
        self.assertIn(b'email', response.data)
    
    def test_successful_registration(self):
        """Test successful user registration."""
        with patch('auth.routes.send_confirmation_email') as mock_send:
            mock_send.return_value = True
            
            response = self.client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'confirmation email', response.data)
            
            # Check user was created
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'newuser@example.com')
            self.assertFalse(user.is_confirmed)
            self.assertFalse(user.is_admin)
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create existing user
        self.create_user(username='existing', email='existing@example.com')
        
        response = self.client.post('/auth/register', data={
            'username': 'existing',
            'email': 'different@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different username', response.data)
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create existing user
        self.create_user(username='existing', email='existing@example.com')
        
        response = self.client.post('/auth/register', data={
            'username': 'different',
            'email': 'existing@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different email', response.data)
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'different123'
        })
        
        self.assertEqual(response.status_code, 200)
        # Form validation should catch this
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNone(user)
    
    def test_successful_login(self):
        """Test successful user login."""
        # Create confirmed user
        user = self.create_user(is_confirmed=True)
        
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)
    
    def test_login_invalid_username(self):
        """Test login with invalid username."""
        response = self.client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect back to login
        
        response = self.client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        # Create user
        self.create_user(is_confirmed=True)
        
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_login_unconfirmed_user(self):
        """Test login with unconfirmed user."""
        # Create unconfirmed user
        self.create_user(is_confirmed=False)
        
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertIn(b'Please confirm your email', response.data)
    
    def test_logout(self):
        """Test user logout."""
        # Create and login user
        user = self.create_user(is_confirmed=True)
        self.login_user()
        
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out', response.data)
    
    def test_login_redirect_to_next_page(self):
        """Test login redirect to next page."""
        # Create confirmed user
        user = self.create_user(is_confirmed=True)
        
        # Try to access protected page
        response = self.client.get('/main/profile')
        self.assertEqual(response.status_code, 302)
        
        # Login with next parameter
        response = self.client.post('/auth/login?next=%2Fmain%2Fprofile', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        # Should redirect to profile page, not home
        self.assertIn('/main/profile', response.location)


class TestEmailConfirmation(BaseTestCase):
    """Test cases for email confirmation functionality."""
    
    @patch('auth.routes.mail.send')
    def test_send_confirmation_email(self):
        """Test sending confirmation email."""
        from auth.routes import send_confirmation_email
        
        result = send_confirmation_email('test@example.com')
        self.assertTrue(result)
    
    @patch('auth.routes.mail.send')
    def test_send_confirmation_email_failure(self):
        """Test handling of email send failure."""
        from auth.routes import send_confirmation_email
        
        # Mock email sending failure
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("SMTP Error")
        
        with patch('auth.routes.mail', mock_mail):
            result = send_confirmation_email('test@example.com')
            self.assertFalse(result)
    
    def test_generate_and_confirm_token(self):
        """Test token generation and confirmation."""
        from auth.routes import generate_confirmation_token, confirm_token
        
        email = 'test@example.com'
        token = generate_confirmation_token(email)
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)
        
        # Confirm valid token
        confirmed_email = confirm_token(token)
        self.assertEqual(confirmed_email, email)
    
    def test_confirm_expired_token(self):
        """Test confirmation with expired token."""
        from auth.routes import generate_confirmation_token, confirm_token
        
        email = 'test@example.com'
        token = generate_confirmation_token(email)
        
        # Test with very short expiration (should fail)
        confirmed_email = confirm_token(token, expiration=0)
        self.assertFalse(confirmed_email)
    
    def test_confirm_invalid_token(self):
        """Test confirmation with invalid token."""
        from auth.routes import confirm_token
        
        # Test with completely invalid token
        confirmed_email = confirm_token('invalid_token_string')
        self.assertFalse(confirmed_email)
    
    def test_email_confirmation_flow(self):
        """Test complete email confirmation flow."""
        from auth.routes import generate_confirmation_token
        
        # Create unconfirmed user
        user = self.create_user(is_confirmed=False)
        
        # Generate confirmation token
        token = generate_confirmation_token(user.email)
        
        # Confirm email via URL
        response = self.client.get(f'/auth/confirm/{token}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'confirmed your account', response.data)
        
        # Check user is now confirmed
        user = User.query.get(user.id)
        self.assertTrue(user.is_confirmed)
        self.assertIsNotNone(user.confirmed_on)
    
    def test_resend_confirmation(self):
        """Test resending confirmation email."""
        # Create and login unconfirmed user
        user = self.create_user(is_confirmed=False)
        self.login_user()
        
        with patch('auth.routes.send_confirmation_email') as mock_send:
            mock_send.return_value = True
            
            response = self.client.get('/auth/resend', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'new confirmation email', response.data)
            mock_send.assert_called_once_with(user.email)
    
    def test_resend_confirmation_already_confirmed(self):
        """Test resending confirmation for already confirmed user."""
        # Create and login confirmed user
        user = self.create_user(is_confirmed=True)
        self.login_user()
        
        response = self.client.get('/auth/resend', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already confirmed', response.data)


class TestAccessControl(BaseTestCase):
    """Test cases for access control and authentication requirements."""
    
    def test_anonymous_access_to_public_pages(self):
        """Test that anonymous users can access public pages."""
        public_urls = [
            '/',
            '/auth/login',
            '/auth/register',
            '/main/public_results',
            '/main/model_info'
        ]
        
        for url in public_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # 302 for redirects
    
    def test_anonymous_access_to_protected_pages(self):
        """Test that anonymous users cannot access protected pages."""
        protected_urls = [
            '/main/profile',
            '/main/edit_profile',
            '/main/survey',
            '/main/predict',
            '/main/results',
            '/admin/dashboard'
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect to login
            self.assertIn('/auth/login', response.location)
    
    def test_user_access_to_user_pages(self):
        """Test that regular users can access user pages."""
        # Create and login regular user
        user = self.create_user(is_confirmed=True, is_admin=False)
        self.login_user()
        
        user_urls = [
            '/main/profile',
            '/main/survey',
            '/main/predict',
            '/main/results'
        ]
        
        for url in user_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_user_access_to_admin_pages(self):
        """Test that regular users cannot access admin pages."""
        # Create and login regular user
        user = self.create_user(is_confirmed=True, is_admin=False)
        self.login_user()
        
        admin_urls = [
            '/admin/dashboard',
            '/admin/users',
            '/admin/surveys'
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_admin_access_to_admin_pages(self):
        """Test that admin users can access admin pages."""
        # Create and login admin user
        user = self.create_user(is_confirmed=True, is_admin=True)
        self.login_user()
        
        admin_urls = [
            '/admin/dashboard',
            '/admin/users',
            '/admin/surveys'
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_unconfirmed_user_access(self):
        """Test access control for unconfirmed users."""
        # Create and login unconfirmed user
        user = self.create_user(is_confirmed=False)
        
        # Should not be able to login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertIn(b'Please confirm your email', response.data)


class TestUserModel(BaseTestCase):
    """Test cases for User model functionality."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        user = User(username='test', email='test@example.com')
        
        # Set password
        user.set_password('mypassword123')
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, 'mypassword123')
        
        # Check password
        self.assertTrue(user.check_password('mypassword123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_get_full_name(self):
        """Test full name generation."""
        # User with first and last name
        user = User(
            username='test',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.get_full_name(), 'John Doe')
        
        # User without names
        user = User(username='test', email='test@example.com')
        self.assertEqual(user.get_full_name(), 'test')
    
    def test_user_representation(self):
        """Test string representation of user."""
        user = User(username='testuser', email='test@example.com')
        self.assertEqual(str(user), '<User testuser>')


if __name__ == '__main__':
    unittest.main()
