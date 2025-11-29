#!/usr/bin/env python3
"""
Enhanced Business Analyst Agent Startup Script
Launches the system with LangChain and OneDrive integration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'langchain',
        'langchain-core', 
        'langchain-community',
        'msal',
        'azure-identity'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check required environment variables
    required_vars = {
        'GEMINI_API_KEY': 'Gemini AI API Key',
        'DATABASE_URL': 'Database Connection URL'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
            print(f"❌ {var} - Missing")
        else:
            print(f"✅ {var} - Configured")
    
    # Check optional environment variables
    optional_vars = {
        'LANGCHAIN_ENABLED': 'LangChain Integration',
        'OPENAI_API_KEY': 'OpenAI API Key (for LangChain)'
    }
    
    for var, description in optional_vars.items():
        if os.getenv(var):
            print(f"✅ {var} - Configured")
        else:
            print(f"ℹ️ {var} - Not configured (optional)")
    
    if missing_vars:
        print(f"\n⚠️ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    
    required_files = [
        'main_enhanced.py',
        'langchain_integration.py',
        'config.py',
        'database.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} - Missing")
    
    if missing_files:
        print(f"\n⚠️ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True

def start_enhanced_server():
    """Start the enhanced server"""
    print("\n🚀 Starting Enhanced Business Analyst Agent...")
    
    try:
        # Import and run the enhanced main application
        from main_enhanced import app
        
        print("✅ Enhanced server imported successfully")
        print("🌐 Starting Flask application...")
        print("📊 Available endpoints:")
        print("   - /api/status - System status")
        print("   - /api/features - Available features")
        print("   - /api/langchain/status - LangChain status")
        print("   - /api/generate/enhanced - Enhanced document generation")
        print("\n🔗 Access the application at: http://localhost:5000")
        print("📚 API documentation available at: http://localhost:5000/api/status")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Failed to import enhanced server: {e}")
        print("💡 Make sure all required files are present and dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 Enhanced Business Analyst Agent Startup")
    print("=" * 60)
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please configure required variables.")
        return False
    
    # Check files
    if not check_files():
        print("❌ File check failed. Please ensure all required files are present.")
        return False
    
    # Start server
    print("\n" + "=" * 60)
    print("🎯 All checks passed! Starting enhanced server...")
    print("=" * 60)
    
    return start_enhanced_server()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Enhanced Business Analyst Agent stopped by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
