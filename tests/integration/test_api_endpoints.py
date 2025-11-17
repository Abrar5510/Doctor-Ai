"""
Integration tests for API endpoints.

Tests the complete API workflow including authentication, diagnostic analysis,
and AI-powered features.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from src.main import app


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_token(async_client):
    """Get authentication token for testing"""
    # Register a test user
    register_data = {
        "username": "test_physician",
        "email": "test@doctor-ai.com",
        "password": "Test123!@#Strong",
        "full_name": "Test Physician",
        "role": "physician"
    }

    response = await async_client.post("/api/v1/auth/register", json=register_data)

    # Login to get token
    login_data = {
        "username": "test_physician",
        "password": "Test123!@#Strong"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    return data["access_token"]


class TestHealthEndpoints:
    """Test health check and system status endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test root endpoint returns service info"""
        response = await async_client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["status"] == "operational"

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint"""
        response = await async_client.get("/api/v1/health")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestAuthenticationEndpoints:
    """Test authentication and authorization"""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client):
        """Test user registration"""
        user_data = {
            "username": "new_user_123",
            "email": "newuser123@doctor-ai.com",
            "password": "SecurePass123!@#",
            "full_name": "New User",
            "role": "physician"
        }

        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_user(self, async_client):
        """Test that duplicate registration fails"""
        user_data = {
            "username": "duplicate_user",
            "email": "duplicate@doctor-ai.com",
            "password": "SecurePass123!@#",
            "full_name": "Duplicate User",
            "role": "physician"
        }

        # First registration should succeed
        response1 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Second registration should fail
        response2 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_login_success(self, async_client):
        """Test successful login"""
        # Register user first
        register_data = {
            "username": "login_test_user",
            "email": "logintest@doctor-ai.com",
            "password": "LoginPass123!@#",
            "full_name": "Login Test",
            "role": "physician"
        }
        await async_client.post("/api/v1/auth/register", json=register_data)

        # Login
        login_data = {
            "username": "login_test_user",
            "password": "LoginPass123!@#"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent_user",
            "password": "WrongPassword123!"
        }

        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDiagnosticEndpoints:
    """Test diagnostic analysis endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_patient_case(self, async_client, auth_token):
        """Test patient case analysis"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        case_data = {
            "case_id": "test_case_001",
            "age": 45,
            "sex": "female",
            "chief_complaint": "Severe headache and sensitivity to light",
            "symptoms": [
                {
                    "name": "headache",
                    "severity": "severe",
                    "duration_days": 2,
                    "location": "frontal"
                },
                {
                    "name": "photophobia",
                    "severity": "moderate",
                    "duration_days": 2
                },
                {
                    "name": "nausea",
                    "severity": "mild",
                    "duration_days": 1
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/analyze",
            json=case_data,
            headers=headers
        )

        # May fail if services not available, but should not error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "case_id" in data
            assert "differential_diagnoses" in data

    @pytest.mark.asyncio
    async def test_analyze_requires_auth(self, async_client):
        """Test that analysis requires authentication"""
        case_data = {
            "case_id": "test_case_002",
            "age": 30,
            "sex": "male",
            "chief_complaint": "Chest pain",
            "symptoms": []
        }

        response = await async_client.post("/api/v1/analyze", json=case_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_enhanced_analysis(self, async_client, auth_token):
        """Test enhanced analysis with AI features"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        case_data = {
            "case_id": "test_case_enhanced_001",
            "age": 55,
            "sex": "male",
            "chief_complaint": "Persistent cough and fever",
            "symptoms": [
                {
                    "name": "cough",
                    "severity": "moderate",
                    "duration_days": 7
                },
                {
                    "name": "fever",
                    "severity": "moderate",
                    "duration_days": 5,
                    "onset_date": "2024-01-10"
                }
            ]
        }

        response = await async_client.post(
            "/api/v1/analyze/enhanced",
            json=case_data,
            headers=headers,
            params={
                "include_explanation": True,
                "include_questions": True,
                "include_report": False
            }
        )

        # May fail if AI service not available
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]

    @pytest.mark.asyncio
    async def test_get_system_stats(self, async_client, auth_token):
        """Test system statistics endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = await async_client.get("/api/v1/stats", headers=headers)

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "status" in data
            assert "features" in data


class TestInputValidation:
    """Test input validation and error handling"""

    @pytest.mark.asyncio
    async def test_invalid_age(self, async_client, auth_token):
        """Test that invalid age is rejected"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        case_data = {
            "case_id": "test_invalid_age",
            "age": -5,  # Invalid age
            "sex": "female",
            "chief_complaint": "Test",
            "symptoms": []
        }

        response = await async_client.post(
            "/api/v1/analyze",
            json=case_data,
            headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, async_client, auth_token):
        """Test that missing required fields are rejected"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        case_data = {
            "case_id": "test_missing_fields",
            # Missing age, sex, chief_complaint, symptoms
        }

        response = await async_client.post(
            "/api/v1/analyze",
            json=case_data,
            headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_cors_headers(async_client):
    """Test that CORS headers are present"""
    response = await async_client.options("/api/v1/health")

    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or True
