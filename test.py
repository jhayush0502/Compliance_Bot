#!/usr/bin/env python3
"""
Simple script to test if environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are loaded"""
    
    print("🔍 Testing Environment Variables...")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Define required environment variables
    required_vars = {
        'AWS_ACCESS_KEY_ID': 'Your AWS Access Key ID',
        'AWS_SECRET_ACCESS_KEY': 'Your AWS Secret Access Key', 
        'AWS_REGION': 'AWS Region (e.g., us-east-1)',
        'BEDROCK_MODEL_ID': 'Bedrock Model ID',
        'BEDROCK_MAX_TOKENS': 'Maximum tokens for responses',
        'BEDROCK_TEMPERATURE': 'Temperature for AI responses',
        'KENDRA_INDEX_ID': 'Kendra Index ID for RAG',
        'KENDRA_MIN_CONFIDENCE_SCORE': 'Minimum confidence score for Kendra results'
    }
    
    # Check each variable
    missing_vars = []
    found_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Mask sensitive information
            if 'SECRET' in var_name or 'KEY' in var_name:
                display_value = '***' + value[-4:] if len(value) > 4 else '***'
            else:
                display_value = value
            
            print(f"✅ {var_name}: {display_value}")
            found_vars.append(var_name)
        else:
            print(f"❌ {var_name}: NOT FOUND")
            missing_vars.append(var_name)
    
    print("=" * 50)
    
    # Summary
    if not missing_vars:
        print("🎉 All environment variables found!")
        print("✅ Your .env file is configured correctly.")
        return True
    else:
        print(f"⚠️  Missing {len(missing_vars)} environment variable(s):")
        for var in missing_vars:
            print(f"   - {var}: {required_vars[var]}")
        
        print("\n📝 Steps to fix:")
        print("1. Create a .env file in your project root directory")
        print("2. Add the missing variables to your .env file")
        print("3. Make sure the .env file is in the same directory as your Python script")
        
        return False

def create_sample_env_file():
    """Create a sample .env file"""
    sample_content = """# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAYXT5S2A
AWS_SECRET_ACCESS_KEY=Lr4gYdA7m0+zZKvrH
AWS_REGION=us-east-1

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=2000
BEDROCK_TEMPERATURE=0.7

# Kendra Configuration (for RAG)
KENDRA_INDEX_ID=salespitch
KENDRA_MIN_CONFIDENCE_SCORE=0.3
"""
    
    try:
        with open('.env.sample', 'w') as f:
            f.write(sample_content)
        print("📄 Created .env.sample file with your credentials")
        print("💡 You can rename it to .env or copy the content to your .env file")
        return True
    except Exception as e:
        print(f"❌ Error creating sample file: {e}")
        return False

def check_dotenv_installation():
    """Check if python-dotenv is installed"""
    try:
        import dotenv
        print("✅ python-dotenv is installed")
        return True
    except ImportError:
        print("❌ python-dotenv is not installed")
        print("💡 Install it with: pip install python-dotenv")
        return False

if __name__ == "__main__":
    print("🧪 Compliance Bot - Environment Test")
    print("=" * 50)
    
    # Check if dotenv is installed
    if not check_dotenv_installation():
        exit(1)
    
    # Test environment variables
    if not test_environment_variables():
        print("\n🔧 Would you like me to create a sample .env file? (y/n): ", end="")
        response = input().lower().strip()
        if response in ['y', 'yes']:
            create_sample_env_file()
        
        print("\n🚀 After fixing your .env file, run this script again to verify!")
        exit(1)
    
    print("\n🎯 Environment is ready! You can now run the compliance bot.")