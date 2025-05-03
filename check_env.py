#!/usr/bin/env python3

import os

def check_env_file():
    """Check if .env file exists and has expected variables."""
    try:
        if os.path.exists('.env'):
            print("✅ .env file exists")
            
            with open('.env', 'r') as f:
                content = f.read()
                
            if 'OPENAI_API_KEY' in content:
                print("✅ OPENAI_API_KEY found in .env")
            else:
                print("❌ OPENAI_API_KEY not found in .env")
                
            if 'SONAR_API_KEY' in content:
                print("✅ SONAR_API_KEY found in .env")
            else:
                print("❌ SONAR_API_KEY not found in .env")
        else:
            print("❌ .env file not found")
    except Exception as e:
        print(f"Error checking .env file: {e}")

def check_env_example_file():
    """Check if .env.example file exists and has expected variables."""
    try:
        if os.path.exists('.env.example'):
            print("✅ .env.example file exists")
            
            with open('.env.example', 'r') as f:
                content = f.read()
                
            if 'OPENAI_API_KEY' in content:
                print("✅ OPENAI_API_KEY found in .env.example")
            else:
                print("❌ OPENAI_API_KEY not found in .env.example")
                
            if 'SONAR_API_KEY' in content:
                print("✅ SONAR_API_KEY found in .env.example")
            else:
                print("❌ SONAR_API_KEY not found in .env.example")
        else:
            print("❌ .env.example file not found")
    except Exception as e:
        print(f"Error checking .env.example file: {e}")

def check_dotenv_import():
    """Check if dotenv import is correctly implemented."""
    try:
        # Check cli.ts
        if os.path.exists('src/cli.ts'):
            with open('src/cli.ts', 'r') as f:
                content = f.read()
            if "import 'dotenv/config'" in content and content.find("import 'dotenv/config'") <= 5:
                print("✅ dotenv/config import exists at the top of src/cli.ts")
            else:
                print("❌ dotenv/config import not found at the top of src/cli.ts")
        else:
            print("❌ src/cli.ts file not found")
            
        # Check testSetup.ts
        if os.path.exists('src/testSetup.ts'):
            with open('src/testSetup.ts', 'r') as f:
                content = f.read()
            if "import 'dotenv/config'" in content:
                print("✅ dotenv/config import exists in src/testSetup.ts")
            else:
                print("❌ dotenv/config import not found in src/testSetup.ts")
        else:
            print("❌ src/testSetup.ts file not found")
            
        # Check jest.config.js
        if os.path.exists('jest.config.js'):
            with open('jest.config.js', 'r') as f:
                content = f.read()
            if "setupFiles: ['<rootDir>/src/testSetup.ts']" in content:
                print("✅ setupFiles points to src/testSetup.ts in jest.config.js")
            else:
                print("❌ setupFiles does not point to src/testSetup.ts in jest.config.js")
        else:
            print("❌ jest.config.js file not found")
    except Exception as e:
        print(f"Error checking dotenv imports: {e}")

if __name__ == "__main__":
    print("\n=== Checking .env file ===")
    check_env_file()
    
    print("\n=== Checking .env.example file ===")
    check_env_example_file()
    
    print("\n=== Checking dotenv implementation ===")
    check_dotenv_import()
    
    print("\nVerification complete!") 