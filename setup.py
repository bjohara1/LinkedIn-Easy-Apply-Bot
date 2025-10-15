#!/usr/bin/env python3
"""
LinkedIn Easy Apply Bot Setup Script
This script helps you configure the bot with your LinkedIn credentials and preferences.
"""

import os
import yaml
import getpass
from pathlib import Path

def get_user_input(prompt, is_password=False):
    """Get user input, hiding password if needed."""
    if is_password:
        return getpass.getpass(prompt)
    return input(prompt)

def setup_config():
    """Interactive setup for the LinkedIn Easy Apply Bot."""
    print("=" * 60)
    print("LinkedIn Easy Apply Bot Setup")
    print("=" * 60)
    print()
    
    # Load existing config if it exists
    config_file = "config.yaml"
    config = {}
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        print("Found existing config file. Current settings:")
        for key, value in config.items():
            if key in ['username', 'password']:
                print(f"  {key}: {'*' * len(str(value)) if value else 'Not set'}")
            else:
                print(f"  {key}: {value}")
        print()
    
    # Get LinkedIn credentials
    print("LinkedIn Credentials:")
    print("-" * 20)
    username = get_user_input("LinkedIn Email/Username: ")
    password = get_user_input("LinkedIn Password: ", is_password=True)
    phone_number = get_user_input("Phone Number: ")
    
    # Get job preferences
    print("\nJob Search Preferences:")
    print("-" * 25)
    
    print("\nPositions to search for (one per line, press Enter twice when done):")
    positions = []
    while True:
        position = input("Position: ").strip()
        if not position:
            break
        positions.append(position)
    
    print("\nLocations to search in (one per line, press Enter twice when done):")
    locations = []
    while True:
        location = input("Location: ").strip()
        if not location:
            break
        locations.append(location)
    
    salary = input("Minimum yearly salary (e.g., 80000): ").strip()
    rate = input("Minimum hourly rate (e.g., 40): ").strip()
    
    # Experience levels
    print("\nExperience levels to apply for:")
    print("1. Entry level")
    print("2. Associate") 
    print("3. Mid-Senior level")
    print("4. Director")
    print("5. Executive")
    print("6. Internship")
    
    experience_input = input("Enter numbers separated by commas (e.g., 1,2,3): ").strip()
    experience_level = [int(x.strip()) for x in experience_input.split(',') if x.strip().isdigit()]
    
    # File uploads
    print("\nFile Uploads:")
    print("-" * 15)
    
    resume_path = input("Path to your resume (PDF): ").strip()
    cover_letter_path = input("Path to your cover letter (PDF): ").strip()
    
    # Blacklist
    print("\nCompany Blacklist (companies to ignore):")
    print("Enter company names one per line, press Enter twice when done:")
    blacklist = []
    while True:
        company = input("Company to blacklist: ").strip()
        if not company:
            break
        blacklist.append(company)
    
    # Build config
    new_config = {
        'username': username,
        'password': password,
        'phone_number': phone_number,
        'profile_path': '',
        'positions': positions,
        'locations': locations,
        'salary': int(salary) if salary.isdigit() else 80000,
        'rate': int(rate) if rate.isdigit() else 40,
        'uploads': {
            'Resume': resume_path,
            'Cover Letter': cover_letter_path
        },
        'output_filename': ['out.csv'],
        'blacklist': blacklist,
        'experience_level': experience_level
    }
    
    # Save config
    with open(config_file, 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Configuration saved to {config_file}")
    print("\nNext steps:")
    print("1. Make sure your resume and cover letter files exist at the specified paths")
    print("2. Run: python3 easyapplybot.py")
    print("3. The bot will log into LinkedIn and start applying to jobs")
    print("\n⚠️  IMPORTANT: Never commit your config.yaml file to version control!")

if __name__ == "__main__":
    setup_config() 