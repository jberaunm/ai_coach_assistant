#!/usr/bin/env python3
"""
Simple test for weekly API
"""

import requests
from datetime import datetime, timedelta

def test_weekly_api():
    # Get the Monday of the current week
    today = datetime.now()
    day = today.weekday()  # Monday is 0, Sunday is 6
    monday = today - timedelta(days=day)
    start_date = monday.strftime("%Y-%m-%d")
    
    print(f"Testing weekly API for week starting: {start_date}")
    
    try:
        # Test the weekly endpoint
        response = requests.get(f"http://localhost:8000/api/weekly/{start_date}")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Weekly API test successful!")
            print(f"Status: {data['status']}")
            print(f"Message: {data['message']}")
            
            if data['summary']:
                summary = data['summary']
                print(f"\n📊 Weekly Summary:")
                print(f"  Total Distance: {summary['total_distance']} km")
                print(f"  Total Sessions: {summary['total_sessions']}")
                print(f"  Completed Sessions: {summary['completed_sessions']}")
                print(f"  Completion Rate: {summary['completion_rate']:.1f}%")
            
            if data['data']:
                print(f"\n📅 Daily Data ({len(data['data'])} days):")
                for day_data in data['data']:
                    status = "✓" if day_data['session_completed'] else "○"
                    activity = "🏃" if day_data['has_activity'] else "😴"
                    print(f"  {day_data['day_name'][:3]} {day_data['date']}: {activity} {day_data['session_type']} ({day_data['distance']}km) {status}")
            
        else:
            print(f"❌ Weekly API test failed with status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error testing weekly API: {str(e)}")

if __name__ == "__main__":
    test_weekly_api() 