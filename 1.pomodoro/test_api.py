"""
Test script for Pomodoro API endpoints
Usage: python test_api.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"


def print_result(test_name, response):
    """Print test result"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    print_result("Health Check", response)
    assert response.status_code == 200


def test_get_settings():
    """Test GET /api/settings"""
    response = requests.get(f"{BASE_URL}/api/settings")
    print_result("GET /api/settings", response)
    assert response.status_code == 200
    assert response.json()['success'] is True


def test_update_settings():
    """Test PUT /api/settings"""
    data = {
        "work_duration": 30,
        "break_duration": 10,
        "sound_volume": 80,
        "auto_start_breaks": True
    }
    response = requests.put(
        f"{BASE_URL}/api/settings",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result("PUT /api/settings", response)
    assert response.status_code == 200
    assert response.json()['data']['work_duration'] == 30


def test_invalid_settings():
    """Test PUT /api/settings with invalid data"""
    data = {
        "work_duration": 200  # Invalid: exceeds maximum
    }
    response = requests.put(
        f"{BASE_URL}/api/settings",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result("PUT /api/settings (Invalid)", response)
    assert response.status_code == 400
    assert 'error' in response.json()


def test_create_session():
    """Test POST /api/sessions"""
    data = {
        "session_type": "work",
        "duration": 25,
        "task_name": "テストタスク",
        "started_at": "2026-02-24T10:00:00Z",
        "ended_at": "2026-02-24T10:25:00Z",
        "completed": True,
        "notes": "集中して作業完了"
    }
    response = requests.post(
        f"{BASE_URL}/api/sessions",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result("POST /api/sessions", response)
    assert response.status_code == 201
    assert response.json()['data']['task_name'] == "テストタスク"


def test_get_sessions():
    """Test GET /api/sessions"""
    response = requests.get(f"{BASE_URL}/api/sessions")
    print_result("GET /api/sessions", response)
    assert response.status_code == 200
    assert 'data' in response.json()
    assert 'count' in response.json()


def test_get_sessions_by_date():
    """Test GET /api/sessions with date filter"""
    response = requests.get(
        f"{BASE_URL}/api/sessions",
        params={"date": "2026-02-24"}
    )
    print_result("GET /api/sessions?date=2026-02-24", response)
    assert response.status_code == 200


def test_invalid_session():
    """Test POST /api/sessions with invalid data"""
    data = {
        "session_type": "invalid",
        "duration": 25,
        "started_at": "2026-02-24T10:00:00Z",
        "ended_at": "2026-02-24T10:25:00Z"
    }
    response = requests.post(
        f"{BASE_URL}/api/sessions",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result("POST /api/sessions (Invalid)", response)
    assert response.status_code == 400
    assert 'error' in response.json()


def test_invalid_date_format():
    """Test GET /api/sessions with invalid date"""
    response = requests.get(
        f"{BASE_URL}/api/sessions",
        params={"date": "invalid-date"}
    )
    print_result("GET /api/sessions (Invalid Date)", response)
    assert response.status_code == 400


def run_all_tests():
    """Run all tests"""
    tests = [
        test_health,
        test_get_settings,
        test_update_settings,
        test_invalid_settings,
        test_create_session,
        test_get_sessions,
        test_get_sessions_by_date,
        test_invalid_session,
        test_invalid_date_format
    ]
    
    print("Starting API Tests...")
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✓ {test.__name__} passed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
