import requests

API_TOKEN = "johiHREyKMRBTqRBF8rwaaCYo4fpg12g3ZUVlS63PUIEKzeXGRtyqfvFBxrj"

def test_leagues_endpoint():
    """Test the leagues endpoint which should work with free plan"""
    
    # Base URL for leagues endpoint
    url = "https://cricket.sportmonks.com/api/v2.0/leagues"
    
    # Parameters including API token
    params = {
        "api_token": API_TOKEN
    }
    
    print("Testing leagues endpoint (should work with free plan)...")
    print(f"URL: {url}")
    print(f"API Token (first/last 5 chars): {API_TOKEN[:5]}...{API_TOKEN[-5:]}")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nSuccessful response!")
            
            # Check for expected leagues in free plan
            expected_leagues = {
                3: "Twenty20 International",
                10: "CSA T20 Challenge",
                5: "Big Bash League"
            }
            
            found_leagues = []
            if 'data' in data:
                for league in data['data']:
                    league_id = league.get('id')
                    league_name = league.get('name')
                    if league_id in expected_leagues:
                        found_leagues.append(f"{league_name} (ID: {league_id})")
                        
            print("\nFound leagues:")
            for league in found_leagues:
                print(f"✓ {league}")
                
            if not found_leagues:
                print("No expected leagues found in response")
                print("Raw response:", data)
        else:
            print("\nError in response!")
            print("Response:", response.text)
            print("\nTroubleshooting tips:")
            print("1. Verify you have registered at https://www.sportmonks.com/")
            print("2. Make sure you have activated the free cricket plan")
            print("3. Check if your API token is copied correctly")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_leagues_endpoint() 