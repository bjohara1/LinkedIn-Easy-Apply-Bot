#!/usr/bin/env python3
"""
Test script to run the bot without interactive prompts
"""

import yaml
from easyapplybot import EasyApplyBot

def main():
    """Run the bot directly"""
    print("🚀 Starting LinkedIn Easy Apply Bot...")

    # Load config
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

if __name__ == "__main__":
    main()
