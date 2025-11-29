#!/usr/bin/env python3
"""
Azure Communication Services Email Diagnostics Tool
Helps diagnose and fix email sending issues with ACS
"""

import os
import sys
from datetime import datetime
from azure.communication.email import EmailClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from config import ACS_CONNECTION_STRING, ACS_SENDER_ADDRESS, APPROVAL_RECIPIENT_EMAIL

def test_acs_connection():
    """Test basic ACS connection and authentication"""
    print("🔍 Testing Azure Communication Services Connection...")
    print("=" * 60)
    
    try:
        # Initialize the EmailClient
        email_client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)
        print("✅ ACS Email Client initialized successfully")
        return email_client
    except Exception as e:
        print(f"❌ Failed to initialize ACS Email Client: {str(e)}")
        return None

def validate_configuration():
    """Validate ACS configuration parameters"""
    print("\n📋 Validating Configuration...")
    print("=" * 60)
    
    issues = []
    
    # Check connection string format
    if not ACS_CONNECTION_STRING or not ACS_CONNECTION_STRING.startswith('endpoint='):
        issues.append("❌ Invalid ACS_CONNECTION_STRING format")
    else:
        print("✅ Connection string format is valid")
    
    # Check sender address format
    if not ACS_SENDER_ADDRESS or '@' not in ACS_SENDER_ADDRESS:
        issues.append("❌ Invalid ACS_SENDER_ADDRESS format")
    else:
        print("✅ Sender address format is valid")
        
        # Check if sender address uses ACS domain
        if '.azurecomm.net' not in ACS_SENDER_ADDRESS:
            issues.append("⚠️  Sender address should use .azurecomm.net domain")
    
    # Check recipient email
    if not APPROVAL_RECIPIENT_EMAIL or '@' not in APPROVAL_RECIPIENT_EMAIL:
        issues.append("❌ Invalid APPROVAL_RECIPIENT_EMAIL format")
    else:
        print("✅ Recipient email format is valid")
    
    return issues

def test_email_sending():
    """Test sending a simple email"""
    print("\n📧 Testing Email Sending...")
    print("=" * 60)
    
    try:
        email_client = EmailClient.from_connection_string(ACS_CONNECTION_STRING)
        
        # Create a simple test message
        message = {
            "senderAddress": ACS_SENDER_ADDRESS,
            "recipients": {
                "to": [{"address": APPROVAL_RECIPIENT_EMAIL}]
            },
            "content": {
                "subject": "BA Agent - Email Service Test",
                "plainText": f"This is a test email from BA Agent.\n\nSent at: {datetime.now()}\n\nIf you receive this, email service is working correctly.",
                "html": f"""
                <html>
                <body>
                    <h2>BA Agent - Email Service Test</h2>
                    <p>This is a test email from BA Agent.</p>
                    <p><strong>Sent at:</strong> {datetime.now()}</p>
                    <p>If you receive this, email service is working correctly.</p>
                </body>
                </html>
                """
            }
        }
        
        print(f"📤 Sending test email to: {APPROVAL_RECIPIENT_EMAIL}")
        print(f"📧 From: {ACS_SENDER_ADDRESS}")
        
        # Send the email
        poller = email_client.begin_send(message)
        result = poller.result()
        
        print(f"✅ Email sent successfully!")
        print(f"📝 Message ID: {result.message_id}")
        print(f"📊 Status: {result.status}")
        
        return True
        
    except ClientAuthenticationError as e:
        print(f"❌ Authentication Error: {str(e)}")
        print("💡 Suggestion: Check if your ACS connection string and access key are correct")
        return False
        
    except HttpResponseError as e:
        print(f"❌ HTTP Error: {str(e)}")
        
        if "Denied" in str(e):
            print("\n🔧 Possible Solutions for 'Denied' Error:")
            print("1. Verify sender address is added and verified in ACS")
            print("2. Check if ACS resource has email sending permissions")
            print("3. Ensure recipient domain is not blocked")
            print("4. Verify ACS resource is in 'Connected' state")
            
        elif "Forbidden" in str(e):
            print("\n🔧 Possible Solutions for 'Forbidden' Error:")
            print("1. Check ACS resource permissions")
            print("2. Verify access key is not expired")
            print("3. Ensure correct subscription and resource group")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def check_acs_resource_status():
    """Provide guidance on checking ACS resource status"""
    print("\n🔍 ACS Resource Status Check...")
    print("=" * 60)
    print("To verify your ACS resource status:")
    print("1. Go to Azure Portal (portal.azure.com)")
    print("2. Navigate to your Communication Service resource")
    print("3. Check the following:")
    print("   - Resource status should be 'Connected'")
    print("   - Email service should be enabled")
    print("   - Sender addresses should be verified")
    print("   - Check any recent activity logs for errors")

def provide_solutions():
    """Provide comprehensive solutions for common issues"""
    print("\n💡 Common Solutions...")
    print("=" * 60)
    
    solutions = [
        {
            "issue": "Denied by resource provider",
            "solutions": [
                "1. Verify sender email address in ACS portal",
                "2. Add sender address to verified senders list",
                "3. Check ACS resource permissions",
                "4. Ensure correct domain configuration",
                "5. Wait for DNS propagation (up to 24 hours)"
            ]
        },
        {
            "issue": "Authentication errors",
            "solutions": [
                "1. Regenerate ACS access key",
                "2. Update connection string in config",
                "3. Check resource group permissions",
                "4. Verify subscription is active"
            ]
        },
        {
            "issue": "Email not delivered",
            "solutions": [
                "1. Check recipient's spam folder",
                "2. Verify recipient domain accepts external emails",
                "3. Add sender to recipient's safe list",
                "4. Check ACS sending quotas and limits"
            ]
        }
    ]
    
    for solution in solutions:
        print(f"\n🔧 {solution['issue']}:")
        for sol in solution['solutions']:
            print(f"   {sol}")

def main():
    """Main diagnostic function"""
    print("🚀 BA Agent - Azure Communication Services Diagnostics")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python Version: {sys.version}")
    
    # Step 1: Validate configuration
    config_issues = validate_configuration()
    if config_issues:
        print("\n❌ Configuration Issues Found:")
        for issue in config_issues:
            print(f"   {issue}")
        print("\n🔧 Please fix configuration issues before proceeding")
        return
    
    # Step 2: Test connection
    email_client = test_acs_connection()
    if not email_client:
        print("\n❌ Cannot proceed with email testing due to connection issues")
        provide_solutions()
        return
    
    # Step 3: Test email sending
    email_success = test_email_sending()
    
    # Step 4: Provide guidance
    if not email_success:
        check_acs_resource_status()
        provide_solutions()
    else:
        print("\n🎉 All tests passed! Email service is working correctly.")
    
    print("\n" + "=" * 60)
    print("Diagnostics complete.")

if __name__ == "__main__":
    main()
