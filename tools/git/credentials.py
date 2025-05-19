"""
Git credentials handling for the MCP server.

This module provides functions for reading and using Git credentials from a JSON configuration file.
"""

import os
import json
import urllib.parse
from typing import Dict, Optional, Any

def get_credentials_path(base_dir: str) -> str:
    """
    Get the path to the Git credentials file.
    
    Args:
        base_dir (str): Base directory of the MCP server
        
    Returns:
        str: Path to the Git credentials file
    """
    return os.path.join(base_dir, 'config', 'credentials.json')

def load_credentials(base_dir: str) -> Dict[str, Dict[str, str]]:
    """
    Load Git credentials from the credentials file.
    
    Args:
        base_dir (str): Base directory of the MCP server
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary of Git credentials by host
    """
    credentials_path = get_credentials_path(base_dir)
    
    try:
        if os.path.exists(credentials_path):
            try:
                with open(credentials_path, 'r') as f:
                    credentials = json.load(f)
                    
                    # Print the loaded credentials for debugging
                    print(f"DEBUG: Loaded credentials: {credentials}")
                    
                    # Check if these are the example credentials
                    has_example_creds = False
                    for domain, creds in credentials.items():
                        if 'token' in creds and 'example' in creds['token'].lower():
                            has_example_creds = True
                            break
                    
                    if has_example_creds:
                        print(f"WARNING: Using example credentials from {credentials_path}")
                        print(f"Please update with your own credentials before performing Git remote operations")
                    else:
                        print(f"Git credentials loaded from {credentials_path}")
                    
                    return credentials
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in credentials file: {e}")
                print(f"Please check and fix the format of {credentials_path}")
                
                # Display the problematic content for debugging
                with open(credentials_path, 'r') as f:
                    content = f.read()
                    print(f"DEBUG: Content of credentials file: {repr(content)}")
                
                return {}
        else:
            print(f"No Git credentials file found at {credentials_path}")
            print(f"Please create a credentials.json file in the config directory")
            return {}
    except Exception as e:
        print(f"Error loading Git credentials: {e}")
        return {}

def get_credentials_for_url(url: str, credentials: Dict[str, Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Get credentials for a Git URL from the credentials dictionary.
    
    Args:
        url (str): Git URL
        credentials (Dict[str, Dict[str, str]]): Credentials dictionary
        
    Returns:
        Optional[Dict[str, str]]: Credentials dictionary with username and token if found
    """
    # Extract domain from URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Handle SSH URLs (git@github.com:user/repo.git)
    if '@' in url and ':' in url and not parsed_url.netloc:
        domain = url.split('@')[1].split(':')[0]
    else:
        # Handle HTTPS URLs
        domain = parsed_url.netloc
    
    # Remove port if present
    domain = domain.split(':')[0]
    
    # Try to match the domain with our credentials
    for key, creds in credentials.items():
        if key in domain:
            # Check if these are example credentials
            if 'token' in creds and 'example' in creds['token'].lower():
                print(f"WARNING: Using example credentials for {domain}")
                print(f"Please update with your own credentials in config/credentials.json")
            
            return creds
    
    return None

def apply_credentials_to_url(url: str, credentials: Dict[str, str]) -> str:
    """
    Apply credentials to a Git URL if it's an HTTPS URL.
    
    Args:
        url (str): Git URL
        credentials (Dict[str, str]): Credentials dictionary with username and token
        
    Returns:
        str: URL with credentials included if applicable
    """
    if not credentials or 'username' not in credentials or 'token' not in credentials:
        return url
    
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Only apply to HTTP(S) URLs
    if parsed_url.scheme not in ('http', 'https'):
        return url
    
    # Replace with authentication
    netloc = f"{credentials['username']}:{credentials['token']}@{parsed_url.netloc}"
    parsed_url = parsed_url._replace(netloc=netloc)
    
    # Return the modified URL
    return urllib.parse.urlunparse(parsed_url)
