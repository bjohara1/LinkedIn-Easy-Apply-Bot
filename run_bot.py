#!/usr/bin/env python3
"""
LinkedIn Easy Apply Bot Launcher
This script checks prerequisites and launches the bot safely.
"""

import os
import sys
import yaml
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if config file exists
    if not os.path.exists("config.yaml"):
        print("❌ config.yaml not found!")
        print("Run 'python3 setup.py' to configure the bot first.")
        return False
    
    # Check if config is properly filled
    try:
        with open("config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        required_fields = ['username', 'password', 'phone_number', 'positions', 'locations']
        for field in required_fields:
            if not config.get(field):
                print(f"❌ Missing required field: {field}")
                return False
            
        # Check if credentials are not placeholder values
        if config['username'] == '# Insert your LinkedIn username/email here':
            print("❌ Please update your LinkedIn credentials in config.yaml")
            print("Run 'python3 setup.py' to configure the bot.")
            return False
            
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False
    
    # Check if resume and cover letter files exist
    if 'uploads' in config:
        for file_type, file_path in config['uploads'].items():
            if file_path and not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                print(f"Please ensure your {file_type.lower()} exists at the specified path.")
                return False
    
    print("✅ All prerequisites met!")
    return True

def main():
    """Main launcher function."""
    print("=" * 60)
    print("LinkedIn Easy Apply Bot Launcher")
    print("=" * 60)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Confirm before running
    print("\n⚠️  Important Notes:")
    print("- This bot will automatically apply to jobs on LinkedIn")
    print("- Make sure your resume and cover letter are up to date")
    print("- The bot may violate LinkedIn's Terms of Service")
    print("- Use responsibly and monitor its behavior")
    print()
    
    confirm = input("Do you want to proceed? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Bot launch cancelled.")
        sys.exit(0)
    
    # Launch the bot
    print("\n🚀 Launching LinkedIn Easy Apply Bot...")
    print("Press Ctrl+C to stop the bot at any time.")
    print()
    
    try:
        # Import and run the bot
        from easyapplybot import EasyApplyBot
        import yaml
        
        with open("config.yaml", 'r') as stream:
            parameters = yaml.safe_load(stream)
        
        # Create bot instance
        bot = EasyApplyBot(
            parameters['username'],
            parameters['password'],
            parameters['phone_number'],
            parameters['salary'],
            parameters['rate'],
            uploads=parameters.get('uploads', {}),
            filename=parameters.get('output_filename', ['output.csv'])[0],
            blacklist=parameters.get('blacklist', []),
            blackListTitles=parameters.get('blackListTitles', []),
            experience_level=parameters.get('experience_level', [])
        )
        
        # Start applying
        bot.start_apply(parameters['positions'], parameters['locations'])
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot stopped by user.")
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        print("Check the logs in the 'logs/' directory for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 