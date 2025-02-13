import requests

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def test_subscription():
    # Test endpoints
    endpoints = [
        "/continents",
        "/countries",
        "/leagues",
        "/seasons",
        "/fixtures"
    ]
    
    base_url = "https://cricket.sportmonks.com/api/v2.0"
    params = {"api_token": API_TOKEN}
    
    print("Testing API endpoints...")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting {endpoint}...")
        
        try:
            response = requests.get(url, params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Success")
            elif response.status_code == 401:
                print("✗ Authentication failed")
            elif response.status_code == 403:
                print("✗ Not authorized (subscription may not include this endpoint)")
            else:
                print(f"✗ Error: {response.text}")
                
        except Exception as e:
            print(f"✗ Exception: {str(e)}")

if __name__ == "__main__":
    test_subscription() 