"""
TikTok authentication and cookie validation module.
"""
import json
from typing import Dict, Tuple

import httpx

from ...utils.logger import logger


class TikTokAuth:
    """Handle TikTok cookie authentication and validation."""
    
    def __init__(self):
        self.validation_url = "https://www.tiktok.com/api/user/detail/"
        self.timeout = 10
    
    def parse_cookie_file(self, content: str) -> Dict[str, str]:
        """
        Parse cookie content from plain text file.
        Supports multiple formats:
        - Netscape format (from browser export)
        - Simple key=value format
        - JSON format
        
        Args:
            content: Cookie file content as string
            
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        
        # Try to parse as JSON first
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                cookies = parsed
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and 'name' in item and 'value' in item:
                        cookies[item['name']] = item['value']
            if cookies:
                logger.info("Parsed cookies from JSON format")
                return cookies
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Try Netscape format (tab-separated)
        # Format: domain flag path secure expiration name value
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Check if it's Netscape format (has tabs)
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    cookies[name] = value
            # Check if it's simple key=value format
            elif '=' in line:
                # Split only on first = to handle values with =
                parts = line.split('=', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    cookies[name] = value
        
        if cookies:
            logger.info(f"Parsed {len(cookies)} cookies from file")
        else:
            logger.warning("No cookies could be parsed from file content")
        
        return cookies
    
    def validate_cookie_format(self, cookies: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validate that required TikTok cookie fields are present.
        
        Args:
            cookies: Dictionary of cookie name-value pairs
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Common TikTok cookie fields that should be present
        required_fields = ['sessionid']  # At minimum, sessionid is required
        important_fields = ['tt_csrf_token', 'sid_guard', 'uid_tt']
        
        if not cookies:
            return False, "No cookies provided"
        
        # Check for required fields
        missing_required = [field for field in required_fields if field not in cookies]
        if missing_required:
            return False, f"Missing required cookie fields: {', '.join(missing_required)}"
        
        # Check for empty values
        empty_fields = [key for key, value in cookies.items() if not value]
        if empty_fields:
            logger.warning(f"Empty cookie values for: {', '.join(empty_fields)}")
        
        # Log missing important fields (warning, not error)
        missing_important = [field for field in important_fields if field not in cookies]
        if missing_important:
            logger.warning(f"Missing important cookie fields (may affect functionality): {', '.join(missing_important)}")
        
        return True, "Cookie format is valid"
    
    async def check_login_status(self, cookies: Dict[str, str]) -> Tuple[bool, str, Dict]:
        """
        Check if the provided cookies are valid by making a test request to TikTok.
        
        Args:
            cookies: Dictionary of cookie name-value pairs
            
        Returns:
            Tuple of (is_logged_in, message, user_info)
        """
        if not cookies:
            return False, "No cookies provided", {}
        
        # Format cookies for the request
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
            'Cookie': cookie_str
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # Try to access TikTok's user info endpoint
                response = await client.get(
                    'https://www.tiktok.com/api/user/detail/',
                    headers=headers,
                    params={'uniqueId': 'self'}  # Request current user info
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Check if we got valid user data
                        if 'userInfo' in data and 'user' in data['userInfo']:
                            user = data['userInfo']['user']
                            username = user.get('uniqueId', 'Unknown')
                            nickname = user.get('nickname', username)
                            user_info = {
                                'username': username,
                                'nickname': nickname,
                                'id': user.get('id', ''),
                            }
                            logger.info(f"TikTok login validated for user: {username}")
                            return True, f"Successfully logged in as {nickname}", user_info
                        else:
                            # Response doesn't have expected structure
                            logger.warning("TikTok API returned unexpected response structure")
                            return False, "Could not verify login status - unexpected response", {}
                    except Exception as e:
                        logger.error(f"Failed to parse TikTok API response: {e}")
                        return False, f"Failed to parse response: {str(e)}", {}
                elif response.status_code == 401 or response.status_code == 403:
                    logger.warning("TikTok cookies are invalid or expired")
                    return False, "Cookies are invalid or expired", {}
                else:
                    logger.warning(f"TikTok API returned status code {response.status_code}")
                    return False, f"API returned status code {response.status_code}", {}
                    
        except httpx.TimeoutException:
            logger.error("Timeout while checking TikTok login status")
            return False, "Request timeout - please try again", {}
        except httpx.ConnectError:
            logger.error("Connection error while checking TikTok login status")
            return False, "Connection error - please check your internet connection", {}
        except Exception as e:
            logger.error(f"Error checking TikTok login status: {e}")
            return False, f"Error: {str(e)}", {}
    
    def format_cookies_for_storage(self, cookies: Dict[str, str]) -> str:
        """
        Format cookies dictionary into a string suitable for storage.
        
        Args:
            cookies: Dictionary of cookie name-value pairs
            
        Returns:
            Formatted cookie string
        """
        # Store as semicolon-separated key=value pairs
        return "; ".join([f"{k}={v}" for k, v in cookies.items()])
    
    def parse_stored_cookies(self, cookie_str: str) -> Dict[str, str]:
        """
        Parse stored cookie string back into a dictionary.
        
        Args:
            cookie_str: Cookie string from storage
            
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        if not cookie_str:
            return cookies
        
        # Split by semicolon and parse key=value pairs
        pairs = cookie_str.split(';')
        for pair in pairs:
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        return cookies
