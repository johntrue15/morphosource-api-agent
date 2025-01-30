import os
import pytest
import requests
from typing import Dict, Optional

class MorphoSourceAPI:
    def __init__(self):
        self.base_url = os.getenv('MORPHOSOURCE_API_URL', 'https://www.morphosource.org')
        self.api_token = os.getenv('MORPHOSOURCE_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}' if self.api_token else None,
            'Accept': 'application/json'
        }

    def get_media(self, media_id: str) -> Dict:
        """Get individual media record"""
        response = requests.get(
            f"{self.base_url}/api/media/{media_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def search_media(self, params: Optional[Dict] = None) -> Dict:
        """Search media records"""
        response = requests.get(
            f"{self.base_url}/api/media",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_physical_object(self, object_id: str) -> Dict:
        """Get individual physical object record"""
        response = requests.get(
            f"{self.base_url}/api/physical-objects/{object_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

class TestMorphoSourceAPI:
    @pytest.fixture
    def api(self):
        return MorphoSourceAPI()

    def test_search_media(self, api):
        """Test basic media search functionality"""
        response = api.search_media()
        assert response is not None
        assert 'data' in response
        assert isinstance(response['data'], list)

    def test_get_media(self, api):
        """Test retrieving individual media record"""
        # First get a media ID from search
        search_response = api.search_media({'limit': 1})
        assert search_response['data']
        
        media_id = search_response['data'][0]['id']
        response = api.get_media(media_id)
        
        assert response is not None
        assert 'data' in response
        assert response['data']['id'] == media_id

    def test_get_physical_object(self, api):
        """Test retrieving physical object record"""
        # First get a physical object ID from media search
        search_response = api.search_media({'limit': 1})
        assert search_response['data']
        
        media = search_response['data'][0]
        if 'relationships' in media and 'physical_object' in media['relationships']:
            physical_object_id = media['relationships']['physical_object']['data']['id']
            response = api.get_physical_object(physical_object_id)
            
            assert response is not None
            assert 'data' in response
            assert response['data']['id'] == physical_object_id

    def test_invalid_media_id(self, api):
        """Test error handling for invalid media ID"""
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_media('invalid_id')

    def test_invalid_physical_object_id(self, api):
        """Test error handling for invalid physical object ID"""
        with pytest.raises(requests.exceptions.HTTPError):
            api.get_physical_object('invalid_id')
