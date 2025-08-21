"""
Tests for login handler functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper.login_handler import LoginHandler


class TestLoginHandler:
    """Test cases for LoginHandler class."""
    
    def test_login_handler_initialization(self):
        """Test that LoginHandler initializes correctly."""
        handler = LoginHandler()
        assert handler is not None
    
    def test_basic_auth_login(self):
        """Test basic authentication login."""
        handler = LoginHandler()
        
        credentials = {
            "username": "testuser",
            "password": "testpass",
            "auth_type": "basic"
        }
        
        with patch('requests.Session') as mock_session:
            mock_sess = MagicMock()
            mock_session.return_value = mock_sess
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sess.post.return_value = mock_response
            
            result = handler.login("https://example.com/login", credentials)
            
            assert result is True
            mock_sess.post.assert_called_once()
    
    def test_form_based_login(self):
        """Test form-based authentication."""
        handler = LoginHandler()
        
        credentials = {
            "username": "testuser",
            "password": "testpass",
            "auth_type": "form",
            "username_field": "email",
            "password_field": "pwd"
        }
        
        with patch('requests.Session') as mock_session:
            mock_sess = MagicMock()
            mock_session.return_value = mock_sess
            mock_response = Mock()
            mock_response.status_code = 200
            mock_sess.post.return_value = mock_response
            
            result = handler.login("https://example.com/login", credentials)
            
            assert result is True
            # Verify form data was sent
            call_args = mock_sess.post.call_args
            assert 'data' in call_args[1]
    
    def test_oauth_login_flow(self):
        """Test OAuth authentication flow."""
        handler = LoginHandler()
        
        credentials = {
            "auth_type": "oauth",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "redirect_uri": "https://app.example.com/callback"
        }
        
        with patch('requests.Session') as mock_session:
            mock_sess = MagicMock()
            mock_session.return_value = mock_sess
            
            # Mock authorization URL generation
            auth_url = handler.get_oauth_auth_url(credentials)
            assert "client_id=test_client" in auth_url
            assert "redirect_uri=" in auth_url
    
    def test_session_management(self):
        """Test session management and persistence."""
        handler = LoginHandler()
        
        # Test session creation
        session = handler.create_session()
        assert session is not None
        
        # Test session persistence
        cookies = {"session_id": "abc123", "csrf_token": "xyz789"}
        handler.save_session(cookies)
        
        restored_session = handler.restore_session()
        assert restored_session is not None
    
    def test_csrf_token_handling(self):
        """Test CSRF token extraction and handling."""
        handler = LoginHandler()
        
        html_content = """
        <html>
            <form>
                <input type="hidden" name="csrf_token" value="abc123def456">
                <input type="text" name="username">
                <input type="password" name="password">
            </form>
        </html>
        """
        
        csrf_token = handler.extract_csrf_token(html_content)
        assert csrf_token == "abc123def456"
    
    def test_captcha_detection(self):
        """Test CAPTCHA detection in login forms."""
        handler = LoginHandler()
        
        # HTML with CAPTCHA
        html_with_captcha = """
        <form>
            <img src="/captcha.png" alt="CAPTCHA">
            <input name="captcha_response">
        </form>
        """
        
        has_captcha = handler.detect_captcha(html_with_captcha)
        assert has_captcha is True
        
        # HTML without CAPTCHA
        html_without_captcha = """
        <form>
            <input name="username">
            <input name="password">
        </form>
        """
        
        has_captcha = handler.detect_captcha(html_without_captcha)
        assert has_captcha is False
    
    def test_login_failure_handling(self):
        """Test handling of login failures."""
        handler = LoginHandler()
        
        credentials = {
            "username": "wronguser",
            "password": "wrongpass",
            "auth_type": "form"
        }
        
        with patch('requests.Session') as mock_session:
            mock_sess = MagicMock()
            mock_session.return_value = mock_sess
            mock_response = Mock()
            mock_response.status_code = 401  # Unauthorized
            mock_sess.post.return_value = mock_response
            
            result = handler.login("https://example.com/login", credentials)
            
            assert result is False
    
    def test_two_factor_authentication(self):
        """Test two-factor authentication handling."""
        handler = LoginHandler()
        
        credentials = {
            "username": "testuser",
            "password": "testpass",
            "auth_type": "form",
            "two_factor_enabled": True,
            "two_factor_code": "123456"
        }
        
        with patch('requests.Session') as mock_session:
            mock_sess = MagicMock()
            mock_session.return_value = mock_sess
            
            # Mock first response requiring 2FA
            mock_response_2fa = Mock()
            mock_response_2fa.status_code = 200
            mock_response_2fa.text = "Enter verification code"
            
            # Mock final success response
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.text = "Login successful"
            
            mock_sess.post.side_effect = [mock_response_2fa, mock_response_success]
            
            result = handler.login_with_2fa("https://example.com/login", credentials)
            
            assert result is True
            assert mock_sess.post.call_count == 2
