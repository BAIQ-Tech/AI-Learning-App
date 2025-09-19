import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
import json

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth_headers():
    """Mock authentication headers for testing"""
    return {"Authorization": "Bearer mock_token"}

class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

class TestLanguageEndpoints:
    def test_get_supported_languages(self, client):
        """Test getting supported languages"""
        response = client.get("/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "en" in data
        assert "ja" in data
        assert "zh" in data

class TestTranslationEndpoint:
    @patch('backend.main.client')
    def test_translate_text_success(self, mock_client, client, auth_headers):
        """Test successful text translation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hola, ¿cómo estás?"
        mock_client.chat.completions.create.return_value = mock_response
        
        translation_data = {
            "text": "Hello, how are you?",
            "source_language": "en",
            "target_language": "es"
        }
        
        response = client.post("/api/translate", json=translation_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "translated_text" in data
        assert data["original_text"] == translation_data["text"]

    def test_translate_text_no_auth(self, client):
        """Test translation without authentication"""
        translation_data = {
            "text": "Hello",
            "source_language": "en",
            "target_language": "es"
        }
        
        response = client.post("/api/translate", json=translation_data)
        assert response.status_code == 401

class TestConversationEndpoint:
    @patch('backend.main.client')
    def test_ai_conversation_success(self, mock_client, client, auth_headers):
        """Test successful AI conversation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "¡Hola! ¿Cómo puedo ayudarte hoy?"
        mock_client.chat.completions.create.return_value = mock_response
        
        conversation_data = {
            "message": "Hello, I want to learn Spanish",
            "language_code": "es",
            "user_id": 1
        }
        
        response = client.post("/api/conversation", json=conversation_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_message" in data
        assert "ai_response" in data
        assert data["user_message"] == conversation_data["message"]

    def test_ai_conversation_no_auth(self, client):
        """Test conversation without authentication"""
        conversation_data = {
            "message": "Hello",
            "language_code": "en"
        }
        
        response = client.post("/api/conversation", json=conversation_data)
        assert response.status_code == 401

class TestRateLimiting:
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present"""
        response = client.get("/api/languages")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

class TestErrorHandling:
    def test_404_endpoint(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client, auth_headers):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/translate",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422
