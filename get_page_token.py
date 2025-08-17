#!/usr/bin/env python3
"""
Facebook Page Token Generator
This script helps you get the correct page access token with proper permissions.
"""

import yaml
import sys

def get_page_token_instructions():
    print("🔧 FACEBOOK PAGE TOKEN GENERATOR")
    print("=" * 50)
    
    # Load config to get current values
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        facebook_config = config.get('social_media', {}).get('facebook', {})
        app_id = facebook_config.get('app_id', 'YOUR_APP_ID')
        page_id = facebook_config.get('page_id', 'YOUR_PAGE_ID')
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        app_id = "YOUR_APP_ID"
        page_id = "YOUR_PAGE_ID"
    
    print("\n🚨 PROBLEM: Your current token doesn't have the right permissions!")
    print("The error shows you need a PAGE ACCESS TOKEN with specific permissions.")
    print("\n📋 SOLUTION: Get a new Page Access Token")
    print("=" * 45)
    
    print("\n🔗 STEP 1: Go to Facebook Graph API Explorer")
    print("https://developers.facebook.com/tools/explorer/")
    
    print(f"\n⚙️  STEP 2: Configure the Explorer")
    print(f"   1. In 'Facebook App' dropdown: Select '{app_id}' (your app)")
    print("   2. In 'User or Page' dropdown: Select 'Get Page Access Token'")
    print(f"   3. Select your page: 'SocioFi Technology' (ID: {page_id})")
    
    print(f"\n🔑 STEP 3: Add Required Permissions")
    print("   Click 'Add a permission' and add these permissions:")
    print("   ✅ pages_read_engagement")
    print("   ✅ pages_manage_posts")
    print("   ✅ pages_show_list")
    print("   ✅ public_profile")
    
    print(f"\n🎯 STEP 4: Generate Page Token")
    print("   1. Click 'Generate Access Token'")
    print("   2. Login and authorize the permissions")
    print("   3. Copy the generated token (it will be very long)")
    
    print(f"\n💾 STEP 5: Update Your Config")
    print("   Replace the access_token in config/config.yaml with the new PAGE token")
    
    print(f"\n🔍 STEP 6: Test the Token")
    print("   Run this in Graph API Explorer to test:")
    print(f"   GET /{page_id}?fields=name,access_token")
    print("   This should return your page info without errors")
    
    print(f"\n🆚 USER TOKEN vs PAGE TOKEN")
    print("=" * 30)
    print("❌ USER TOKEN (what you might have now):")
    print("   - Starts with 'EAAbiRx...'")
    print("   - Has limited permissions")
    print("   - Cannot post to pages directly")
    print("")
    print("✅ PAGE TOKEN (what you need):")
    print("   - Also starts with 'EAAbiRx...' but different")
    print("   - Has page-specific permissions")
    print("   - Can post to your page")
    print("   - Lasts longer (doesn't expire as quickly)")
    
    print(f"\n🔧 QUICK FIX URLS:")
    print("=" * 15)
    print(f"Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print(f"Your App Settings: https://developers.facebook.com/apps/{app_id}/settings/basic/")
    print(f"App Permissions: https://developers.facebook.com/apps/{app_id}/app-review/permissions/")
    
    print(f"\n⚡ AFTER GETTING NEW TOKEN:")
    print("   1. Update config.yaml with the new page token")
    print("   2. Run the publishing test again")
    print("   3. Your posts should work!")

if __name__ == "__main__":
    get_page_token_instructions()
