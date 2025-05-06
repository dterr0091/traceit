import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from ..main import app
from ..services.lineage_service import LineageService
from ..services.auth_service import AuthService

client = TestClient(app)

@pytest.fixture
def mock_auth_service():
    """Mock the auth service for testing."""
    with patch.object(AuthService, 'verify_token', new_callable=AsyncMock) as mock:
        # Return a mock user
        mock.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "is_admin": True
        }
        yield mock

@pytest.fixture
def mock_lineage_service():
    """Mock the lineage service for testing."""
    with patch.object(LineageService, 'get_spread_view', new_callable=AsyncMock) as mock_spread:
        # Return a mock spread view
        mock_spread.return_value = {
            "status": "success",
            "artifact_id": "test-artifact-id",
            "is_composite": False,
            "origin": {
                "url": "https://example.com/original",
                "title": "Original Content",
                "channel_id": "original-channel",
                "timestamp": "2023-01-01T00:00:00Z",
                "spread_count": 10,
                "engagement_score": 3
            },
            "spread_items": [
                {
                    "artifact_id": "spread-1",
                    "artifact_type": "text",
                    "hop_count": 1,
                    "url": "https://example.com/spread-1",
                    "title": "Spread 1",
                    "channel_id": "channel-1",
                    "timestamp": "2023-01-02T00:00:00Z",
                    "spread_count": 5,
                    "engagement_score": 2
                },
                {
                    "artifact_id": "spread-2",
                    "artifact_type": "text",
                    "hop_count": 2,
                    "url": "https://example.com/spread-2",
                    "title": "Spread 2",
                    "channel_id": "channel-2",
                    "timestamp": "2023-01-03T00:00:00Z",
                    "spread_count": 3,
                    "engagement_score": 1
                }
            ],
            "total_items": 2
        }
        
        with patch.object(LineageService, 'build_multi_hop_graph', new_callable=AsyncMock) as mock_update:
            # Return a mock update result
            mock_update.return_value = {
                "status": "success",
                "start_time": "2023-01-01T00:00:00Z",
                "end_time": "2023-01-01T00:05:00Z",
                "relationships_created": 25,
                "artifacts_processed": 10,
                "origins_updated": 5,
                "multi_hop_relationships": 15
            }
            
            yield mock_spread, mock_update

def test_get_spread_view(mock_auth_service, mock_lineage_service):
    """Test getting a spread view for an artifact."""
    mock_spread, _ = mock_lineage_service
    
    # Make request with auth token
    response = client.get(
        "/api/spread/test-artifact-id?max_depth=3",
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["artifact_id"] == "test-artifact-id"
    assert len(data["spread_items"]) == 2
    
    # Verify mocks were called correctly
    mock_auth_service.assert_called_once_with("test-token")
    mock_spread.assert_called_once_with("test-artifact-id", 3)

def test_force_lineage_update(mock_auth_service, mock_lineage_service):
    """Test forcing a lineage graph update."""
    _, mock_update = mock_lineage_service
    
    with patch('backend.app.routers.spread.SchedulerService.force_run_lineage_graph_update', new_callable=AsyncMock) as mock_scheduler:
        # Set up the mock to return the same value as mock_update
        mock_scheduler.return_value = mock_update.return_value
        
        # Make request with auth token
        response = client.post(
            "/api/spread/update",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["relationships_created"] == 25
        
        # Verify mocks were called correctly
        mock_auth_service.assert_called_once_with("test-token")
        mock_scheduler.assert_called_once() 