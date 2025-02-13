import requests

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"  # Your correct token

def test_simple_request():
    # Test the continents endpoint first (simpler endpoint)
    url = "https://cricket.sportmonks.com/api/v2.0/continents"
    
    # API key should be passed as a query parameter only
    params = {
        "api_token": API_TOKEN
    }
    
    print("Making request to:", url)
    print("With API token:", f"{API_TOKEN[:5]}...{API_TOKEN[-5:]}")  # Show partial token for security
    
    try:
        response = requests.get(url, params=params)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nSuccessful response!")
            print(f"Data received: {data}")
            return True
        else:
            print("\nError in response!")
            print("Full response:", response.text)
            print("\nTroubleshooting tips:")
            print("1. Verify your API token in SportMonks dashboard")
            print("2. Check if you have an active cricket subscription")
            print("3. Make sure you have access to the continents endpoint")
            return False
            
    except Exception as e:
        print("Exception occurred:", str(e))
        return False

def verify_token():
    print("Verifying API token...")
    print(f"Token length: {len(API_TOKEN)}")
    print(f"Token first 10 chars: {API_TOKEN[:10]}...")
    print(f"Token last 10 chars: ...{API_TOKEN[-10:]}")
    
    # Check for common issues
    if ' ' in API_TOKEN:
        print("Warning: Token contains spaces!")
    if len(API_TOKEN) != 40:  # Adjust this if the expected length is different
        print(f"Warning: Token length ({len(API_TOKEN)}) might be incorrect!")

if __name__ == "__main__":
    print("Testing API connection...")
    verify_token()
    test_simple_request() 