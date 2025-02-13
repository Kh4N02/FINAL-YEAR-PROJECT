import requests

API_TOKEN = "johiHREyKMRBTqRwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def test_alternative_endpoint():
    # Try the leagues endpoint
    url = "https://cricket.sportmonks.com/api/v2.0/leagues"
    
    params = {
        "api_token": API_TOKEN
    }
    
    print("Testing leagues endpoint...")
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_alternative_endpoint() 