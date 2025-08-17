"""
Complete Multi-Platform Test - Twitter, LinkedIn, Facebook

Test all three platforms with your actual credentials.
"""

import asyncio
import yaml
from datetime import datetime
import sys
import os

# Add the agent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from agent.publisher import Publisher

async def test_all_platforms():
    """Test posting to Twitter, LinkedIn, and Facebook"""
    print("🚀 COMPLETE MULTI-PLATFORM TEST")
    print("=" * 70)
    
    # Load config
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize publisher
    publisher = Publisher(config)
    
    # Test content - works for all platforms
    timestamp = int(datetime.now().timestamp())
    test_content = f"🚀 Multi-platform content distribution test! 💼📘🐦 \n\nTesting automated posting across social media platforms from SocioFi Technology! \n\n#SocialMediaAutomation #TechStartup #{timestamp}"
    
    print(f"📝 Test content ({len(test_content)} chars):")
    print(f"   {test_content}")
    print()
    
    results = {}
    
    # Test 1: Twitter
    print("🐦 TESTING TWITTER...")
    print("-" * 40)
    try:
        twitter_result = await publisher.publish(test_content, "twitter", "social", metadata={})
        results['twitter'] = twitter_result
        print(f"Twitter result: {'✅ Success' if twitter_result else '❌ Failed'}")
    except Exception as e:
        print(f"❌ Twitter error: {e}")
        results['twitter'] = False
    
    print()
    
    # Test 2: LinkedIn Personal
    print("💼 TESTING LINKEDIN (Personal)...")
    print("-" * 40)
    try:
        linkedin_personal_result = await publisher.publish(test_content, "linkedin", "social", 
                                                          metadata={}, posting_mode='personal')
        results['linkedin_personal'] = linkedin_personal_result
        print(f"LinkedIn Personal result: {'✅ Success' if linkedin_personal_result else '❌ Failed'}")
    except Exception as e:
        print(f"❌ LinkedIn Personal error: {e}")
        results['linkedin_personal'] = False
    
    print()
    
    # Test 3: LinkedIn Company
    print("🏢 TESTING LINKEDIN (Company)...")
    print("-" * 40)
    try:
        linkedin_company_result = await publisher.publish(test_content, "linkedin", "social", 
                                                         metadata={}, posting_mode='company')
        results['linkedin_company'] = linkedin_company_result
        print(f"LinkedIn Company result: {'✅ Success' if linkedin_company_result else '❌ Failed'}")
    except Exception as e:
        print(f"❌ LinkedIn Company error: {e}")
        results['linkedin_company'] = False
    
    print()
    
    # Test 4: Facebook
    print("📘 TESTING FACEBOOK...")
    print("-" * 40)
    try:
        facebook_result = await publisher.publish(test_content, "facebook", "social", metadata={})
        results['facebook'] = facebook_result
        print(f"Facebook result: {'✅ Success' if facebook_result else '❌ Failed'}")
    except Exception as e:
        print(f"❌ Facebook error: {e}")
        results['facebook'] = False
    
    print()
    print("📊 FINAL RESULTS:")
    print("=" * 70)
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for platform, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"   {platform.ljust(25)}: {status}")
    
    print()
    print(f"🎯 Overall success: {success_count}/{total_count} platforms")
    
    if success_count == total_count:
        print("🎉 ALL PLATFORMS WORKING PERFECTLY!")
        print("💡 You can now publish to Twitter, LinkedIn, and Facebook simultaneously!")
    elif success_count >= 2:
        print("✅ Most platforms working! Minor tweaks needed for others.")
    elif success_count > 0:
        print("⚠️  Some platforms working, others need attention")
    else:
        print("❌ All platforms failed - check configurations")
    
    # Show next steps
    print()
    print("🚀 READY FOR WEB DASHBOARD:")
    print("- Start server: python run.py")
    print("- Create content in the dashboard")
    print("- Select multiple platforms for publishing")
    print("- Choose LinkedIn mode (personal/company)")
    print("- Publish to all platforms at once!")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_platforms())
