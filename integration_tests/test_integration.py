import requests

def test_service_health():
    url = "https://aiinenterprise-final-project-group9-u64ezt75sq-uc.a.run.app"  # Replace with your app's health check URL
    response = requests.get(url)
    assert response.status_code == 200
