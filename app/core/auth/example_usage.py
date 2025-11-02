"""
Example usage of the TikTok Authentication module.

This demonstrates how to use the TikTokAuth class programmatically.
Run from the project root: python -m app.core.auth.example_usage
"""
import asyncio
import os
import sys

# Add project root to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.core.auth.tiktok_auth import TikTokAuth


async def main():
    """Example usage of TikTok authentication."""
    
    # Initialize the auth module
    auth = TikTokAuth()
    
    print("=== TikTok Cookie Authentication Example ===\n")
    
    # Example 1: Parse cookies from a simple text format
    print("1. Parsing cookies from text...")
    cookie_text = """sessionid=abc123def456
tt_csrf_token=xyz789token
sid_guard=guard123
uid_tt=user456"""
    
    cookies = auth.parse_cookie_file(cookie_text)
    print(f"   Parsed {len(cookies)} cookies: {list(cookies.keys())}")
    
    # Example 2: Validate cookie format
    print("\n2. Validating cookie format...")
    is_valid, message = auth.validate_cookie_format(cookies)
    if is_valid:
        print(f"   ✓ {message}")
    else:
        print(f"   ✗ {message}")
    
    # Example 3: Format cookies for storage
    print("\n3. Formatting cookies for storage...")
    cookie_str = auth.format_cookies_for_storage(cookies)
    print(f"   Formatted: {cookie_str[:50]}...")
    
    # Example 4: Parse stored cookies back
    print("\n4. Parsing stored cookies...")
    parsed_cookies = auth.parse_stored_cookies(cookie_str)
    print(f"   Parsed back: {len(parsed_cookies)} cookies")
    
    # Example 5: Check login status (will fail with test data)
    print("\n5. Checking login status...")
    print("   Note: This will fail with test cookies - use real cookies to test")
    is_logged_in, status_message, user_info = await auth.check_login_status(cookies)
    
    if is_logged_in:
        print(f"   ✓ Logged in as: {user_info.get('nickname', 'Unknown')}")
        print(f"     Username: {user_info.get('username', 'Unknown')}")
    else:
        print(f"   ✗ Login failed: {status_message}")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
