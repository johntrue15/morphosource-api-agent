import os
import pytest
import requests
from urllib.parse import urljoin
from typing import Dict, Optional

class MorphoSourceAPI:
    def __init__(self):
        self.base_url = os.getenv('MORPHOSOURCE_API_URL', 'https://www.morphosource.org')
        self.api_token = os.getenv('MORPHOSOURCE_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}' if self.api_token else None,
            'Accept': 'application/json'
        }
        # Remove trailing slash if present for consistent URL joining
        self.base_url = self.base_url.rstrip('/')

    def get_media(self, media_id: str) -> Dict:
        """Get individual media record"""
        url = urljoin(f"{self.base_url}/", f"api/media/{media_id}")
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def search_media(self, params: Optional[Dict] = None) -> Dict:
        """Search media records"""
        url = urljoin(f"{self.base_url}/", "api/media")
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_physical_object(self, object_id: str) -> Dict:
        """Get individual physical object record"""
        url = urljoin(f"{self.base_url}/", f"api/physical-objects/{object_id}")
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

class TestMorphoSourceAPI:
    @pytest.fixture
    def api(self):
        return MorphoSourceAPI()

    @pytest.fixture
    def mock_api_url(self):
        """Fixture for mock API URL"""
        return "https://stoplight.io/mocks/morphosource/morphosource-api/61245152"

    def test_search_media(self, api, mock_api_url):
        """Test basic media search functionality"""
        api.base_url = mock_api_url
        
        response = api.search_media()
        assert response is not None
        assert 'response' in response
        assert 'pages' in response['response']
        # Verify pagination info exists
        assert all(key in response['response']['pages'] for key in ['current_page', 'limit_value'])
        # Verify facets exist
        assert 'facets' in response['response']

    @pytest.mark.xfail(reason="Mock server returns 422 for individual media endpoints")
    def test_get_media(self, api, mock_api_url):
        """Test retrieving individual media record"""
        api.base_url = mock_api_url
        
        # Use a known test media ID for the mock server
        media_id = "1"  # Using a simple ID for testing
        response = api.get_media(media_id)
        
        assert response is not None
        assert 'response' in response

    def test_get_physical_object(self, api, mock_api_url):
        """Test retrieving physical object record"""
        api.base_url = mock_api_url
        
        # Use a known test physical object ID for the mock server
        object_id = "test_object_id"
        response = api.get_physical_object(object_id)
        
        assert response is not None
        assert 'response' in response
        # Verify the mock response structure for physical objects
        assert 'biological_specimen || cultural_heritage_object' in response['response']
        object_data = response['response']['biological_specimen || cultural_heritage_object']
        # Verify expected fields are present
        assert 'catalog_number' in object_data
        assert 'collection_code' in object_data
        assert 'creator' in object_data
        assert 'date_modified' in object_data

    @pytest.mark.skip("Mock server doesn't properly simulate HTTP errors")
    def test_invalid_media_id(self, api, mock_api_url):
        """Test error handling for invalid media ID"""
        api.base_url = mock_api_url
        
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_media('invalid_id')

    @pytest.mark.skip("Mock server doesn't properly simulate HTTP errors")
    def test_invalid_physical_object_id(self, api, mock_api_url):
        """Test error handling for invalid physical object ID"""
        api.base_url = mock_api_url
        
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_physical_object('invalid_id')
