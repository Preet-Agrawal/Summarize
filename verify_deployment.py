
#!/usr/bin/env python3
"""
Deployment Verification Script for Story Quiz
Checks if all required files and dependencies are ready for Render deployment
"""

import os
import sys
import json

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_python_package(package_name):
    """Check if a Python package can be imported"""
    try:
        __import__(package_name)
        print(f"✅ Python package '{package_name}' installed")
        return True
    except ImportError:
        print(f"❌ Python package '{package_name}' not found")
        return False

def check_env_example():
    """Check if .env.example has all required variables documented"""
    required_vars = ['MONGO_URI', 'GROQ_API_KEY', 'SECRET_KEY']
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            missing = []
            for var in required_vars:
                if var not in content:
                    missing.append(var)
            
            if missing:
                print(f"⚠️  .env.example missing variables: {', '.join(missing)}")
                return False
            else:
                print("✅ .env.example has all required variables")
                return True
    else:
        print("❌ .env.example not found")
        return False

def main():
    print("🔍 Story Quiz Deployment Verification")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check required files
    print("\n📁 Checking Required Files:")
    required_files = [
        ('app.py', 'Main application'),
        ('requirements.txt', 'Python dependencies'),
        ('render.yaml', 'Render configuration'),
        ('Procfile', 'Process file'),
        ('runtime.txt', 'Python runtime'),
        ('package.json', 'npm configuration'),
        ('.env.example', 'Environment template')
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check Python packages
    print("\n📦 Checking Python Packages:")
    packages = [
        'flask',
        'flask_cors',
        'flask_bcrypt',
        'flask_pymongo',
        'flask_wtf',
        'flask_mail',
        'groq',
        'dotenv'
    ]
    
    for package in packages:
        if not check_python_package(package):
            all_checks_passed = False
    
    # Check environment variables documentation
    print("\n🔐 Checking Environment Variables:")
    if not check_env_example():
        all_checks_passed = False
    
    # Check render.yaml configuration
    print("\n⚙️  Checking Render Configuration:")
    if os.path.exists('render.yaml'):
        with open('render.yaml', 'r') as f:
            content = f.read()
            if 'buildCommand' in content and 'startCommand' in content:
                print("✅ render.yaml has build and start commands")
            else:
                print("❌ render.yaml missing build or start commands")
                all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("✅ All checks passed! Ready for Render deployment.")
        print("\nNext steps:")
        print("1. Set up MongoDB Atlas and get connection string")
        print("2. Get Groq API key from https://console.groq.com")
        print("3. Push to GitHub: git push origin main")
        print("4. Deploy on Render: https://render.com")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nRun 'npm run build' to install missing dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())