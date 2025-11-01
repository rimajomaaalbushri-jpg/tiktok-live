# TikTok Authentication Module

## Overview

The TikTok Authentication module provides cookie-based authentication for TikTok Live recording. It allows users to upload cookie files, validates them, and checks the login status.

## Features

- **Multiple Cookie Format Support**: 
  - Netscape format (standard browser export format)
  - Simple key=value format
  - JSON format

- **Cookie Validation**: Validates that required TikTok cookie fields are present

- **Login Status Check**: Verifies cookies by making a test request to TikTok's API

- **User-Friendly UI**: File upload button and validation button integrated in settings

## Usage

### From the UI

1. Navigate to **Settings** > **Cookie Settings**
2. Find the **TikTok Cookie** section
3. Click **Upload Cookie File** to select a plain text file containing your TikTok cookies
4. Click **Validate & Check Login** to verify the cookies are working

### Cookie File Formats

#### Simple Format (key=value)
```
sessionid=abc123def456
tt_csrf_token=xyz789
sid_guard=guard123
uid_tt=user456
```

#### Netscape Format (tab-separated)
```
.tiktok.com	TRUE	/	TRUE	0	sessionid	abc123def456
.tiktok.com	TRUE	/	TRUE	0	tt_csrf_token	xyz789
.tiktok.com	TRUE	/	TRUE	0	sid_guard	guard123
```

#### JSON Format
```json
{
  "sessionid": "abc123def456",
  "tt_csrf_token": "xyz789",
  "sid_guard": "guard123",
  "uid_tt": "user456"
}
```

### Required Cookie Fields

At minimum, the following cookie field is required:
- `sessionid` - Your TikTok session ID

Important (but optional) fields:
- `tt_csrf_token` - CSRF protection token
- `sid_guard` - Session guard
- `uid_tt` - User ID

## How to Get TikTok Cookies

### Using Browser Developer Tools

1. **Login to TikTok** at https://www.tiktok.com
2. **Open Developer Tools**:
   - Chrome/Edge: Press F12 or Ctrl+Shift+I
   - Firefox: Press F12 or Ctrl+Shift+I
   - Safari: Enable Developer Menu, then Cmd+Option+I
3. **Go to Application/Storage tab**:
   - Chrome: Application > Storage > Cookies > https://www.tiktok.com
   - Firefox: Storage > Cookies > https://www.tiktok.com
4. **Copy cookies**:
   - Find `sessionid` and other required cookies
   - Copy the values
5. **Create a text file** with the format shown above

### Using Browser Extensions

You can also use browser extensions like:
- "EditThisCookie" (Chrome)
- "Cookie-Editor" (Firefox/Chrome)

These extensions can export cookies in various formats that this module supports.

## API Reference

### TikTokAuth Class

#### Methods

##### `parse_cookie_file(content: str) -> Dict[str, str]`
Parse cookie content from plain text file.

**Parameters:**
- `content`: Cookie file content as string

**Returns:**
- Dictionary of cookie name-value pairs

**Example:**
```python
from app.core.auth.tiktok_auth import TikTokAuth

auth = TikTokAuth()
cookies = auth.parse_cookie_file("sessionid=abc123\ntt_csrf_token=xyz789")
# Returns: {'sessionid': 'abc123', 'tt_csrf_token': 'xyz789'}
```

##### `validate_cookie_format(cookies: Dict[str, str]) -> Tuple[bool, str]`
Validate that required TikTok cookie fields are present.

**Parameters:**
- `cookies`: Dictionary of cookie name-value pairs

**Returns:**
- Tuple of (is_valid, error_message)

**Example:**
```python
is_valid, message = auth.validate_cookie_format(cookies)
if is_valid:
    print("Cookies are valid!")
else:
    print(f"Invalid: {message}")
```

##### `async check_login_status(cookies: Dict[str, str]) -> Tuple[bool, str, Dict]`
Check if the provided cookies are valid by making a test request to TikTok.

**Parameters:**
- `cookies`: Dictionary of cookie name-value pairs

**Returns:**
- Tuple of (is_logged_in, message, user_info)

**Example:**
```python
import asyncio

async def check_login():
    is_logged_in, message, user_info = await auth.check_login_status(cookies)
    if is_logged_in:
        print(f"Logged in as: {user_info['nickname']}")
    else:
        print(f"Login failed: {message}")

asyncio.run(check_login())
```

##### `format_cookies_for_storage(cookies: Dict[str, str]) -> str`
Format cookies dictionary into a string suitable for storage.

**Parameters:**
- `cookies`: Dictionary of cookie name-value pairs

**Returns:**
- Formatted cookie string (semicolon-separated)

##### `parse_stored_cookies(cookie_str: str) -> Dict[str, str]`
Parse stored cookie string back into a dictionary.

**Parameters:**
- `cookie_str`: Cookie string from storage

**Returns:**
- Dictionary of cookie name-value pairs

## Security Considerations

1. **Keep Cookies Private**: Never share your cookie files or values publicly
2. **Cookie Expiration**: TikTok cookies may expire, requiring you to update them periodically
3. **Secure Storage**: Cookies are stored locally in the config directory
4. **HTTPS Only**: The module only works with HTTPS connections to TikTok

## Troubleshooting

### "Missing required cookie fields"
- Ensure your cookie file contains at least the `sessionid` field
- Check that the file format is correct

### "Cookies are invalid or expired"
- Your cookies may have expired - log in to TikTok again and export fresh cookies
- Ensure you're using the latest cookies from an active TikTok session

### "Connection error"
- Check your internet connection
- Ensure you can access https://www.tiktok.com in your browser
- If using a proxy, ensure it's configured correctly

### "Request timeout"
- The TikTok API may be temporarily unavailable
- Try again after a few moments
- Check your network connection

## Implementation Details

The TikTok authentication module is located at:
```
app/core/auth/tiktok_auth.py
```

UI integration is in:
```
app/ui/views/settings_view.py
```

Locale strings are in:
```
locales/en.json
locales/ar.json
```

## Future Enhancements

Potential improvements for future versions:
- Auto-refresh of expired cookies
- Support for more cookie export formats
- Encrypted cookie storage
- Multi-account support
- Browser cookie import automation
