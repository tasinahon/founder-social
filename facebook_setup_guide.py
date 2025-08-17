"""
Complete Facebook Token Setup Guide

This guide will help you get a proper Facebook token that lasts 60 days
and has all the required permissions.
"""

print("""
🚀 FACEBOOK TOKEN SETUP GUIDE
===============================================

📝 STEP-BY-STEP INSTRUCTIONS:

1️⃣ GO TO FACEBOOK GRAPH API EXPLORER:
   https://developers.facebook.com/tools/explorer/

2️⃣ SELECT YOUR APP:
   - Click on "Meta App" dropdown
   - Select your app: "1937644817012952"

3️⃣ GENERATE USER ACCESS TOKEN:
   - Click "Generate Access Token" button
   - Login to Facebook if prompted
   - Grant all permissions when asked

4️⃣ ADD REQUIRED PERMISSIONS:
   - Click "Add a Permission" 
   - Add these permissions:
     ✅ pages_manage_posts
     ✅ pages_read_engagement  
     ✅ pages_show_list
     ✅ public_profile

5️⃣ GENERATE TOKEN:
   - Click "Generate Access Token" again
   - Copy the token (it will be long)

6️⃣ CONVERT TO LONG-LIVED TOKEN:
   - Run: python facebook_token_manager.py
   - Choose option 1
   - Paste your token when prompted

7️⃣ UPDATE CONFIG:
   - Copy the new long-lived token
   - Update config.yaml

🎯 ALTERNATIVE: NEVER-EXPIRING PAGE TOKEN:
   - Run: python facebook_token_manager.py
   - Choose option 2
   - Follow the prompts for a page token that never expires

⚠️  IMPORTANT NOTES:
   - Short-lived tokens expire in 1-2 hours
   - Long-lived tokens expire in 60 days  
   - Page tokens can be permanent (never expire)
   - Always use page tokens for page posting

🔄 AUTO-RENEWAL REMINDER:
   Set a calendar reminder for October 5, 2025 to renew your token!

===============================================
""")

# Also create a simple token renewal reminder
import json
import os
from datetime import datetime, timedelta

reminder_data = {
    "facebook_token_expiry": "2025-10-06",
    "renewal_reminder": "2025-10-05", 
    "instructions": "Run 'python facebook_token_manager.py' to renew Facebook token",
    "created": datetime.now().isoformat()
}

os.makedirs('data', exist_ok=True)
with open('data/token_reminder.json', 'w') as f:
    json.dump(reminder_data, f, indent=2)

print("💾 Token expiry reminder saved to data/token_reminder.json")
print("📅 Set a calendar reminder for October 5, 2025!")
