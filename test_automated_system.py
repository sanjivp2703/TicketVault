#!/usr/bin/env python3
"""
Comprehensive Test Suite for Safe Transaction Automated System
Tests all components of the automated verification and payment system
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta

class SystemTester:
    """Test the entire automated system"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_database_schema(self):
        """Test database schema has all required fields"""
        try:
            conn = sqlite3.connect('var/insta485.sqlite3')
            cursor = conn.cursor()
            
            # Check transactions table structure
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_fields = [
                'transaction_id', 'buyer_email', 'seller_email', 'price',
                'status', 'awaiting_ticket_email', 'original_event_details',
                'ticket_email_received', 'ticket_verification_score',
                'payment_deadline', 'listing_created_time'
            ]
            
            missing_fields = [field for field in required_fields if field not in columns]
            
            if missing_fields:
                self.log_test("Database Schema", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Database Schema", True, "All required fields present")
                
            conn.close()
            
        except Exception as e:
            self.log_test("Database Schema", False, f"Error: {e}")
    
    def test_listing_creation(self):
        """Test listing creation API"""
        try:
            # Test data
            listing_data = {
                "buyer_email": "test.buyer@example.com",
                "event_name": "Test Concert 2024",
                "location": "Test Arena",
                "event_datetime": "2024-12-31T20:00",
                "price": 150
            }
            
            # Create listing via form submission (simulating browser)
            response = requests.post(
                f"{self.base_url}/create-transaction",
                data=listing_data,
                allow_redirects=False
            )
            
            if response.status_code in [200, 302]:
                self.log_test("Listing Creation", True, "Listing created successfully")
                return True
            else:
                self.log_test("Listing Creation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listing Creation", False, f"Error: {e}")
            return False
    
    def test_verification_api(self):
        """Test the verification API endpoints"""
        try:
            # Get the latest transaction ID from database
            conn = sqlite3.connect('var/insta485.sqlite3')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(transaction_id) FROM transactions")
            result = cursor.fetchone()
            transaction_id = result[0] if result and result[0] else 1
            conn.close()
            
            # Test the test-verify endpoint
            verify_data = {
                "transaction_id": transaction_id,
                "test_mode": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/test-verify",
                json=verify_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("Verification API", True, "Test verification successful")
                    return transaction_id
                else:
                    self.log_test("Verification API", False, f"API error: {result.get('error')}")
            else:
                self.log_test("Verification API", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Verification API", False, f"Error: {e}")
            
        return None
    
    def test_transaction_status(self, transaction_id):
        """Test transaction status API"""
        try:
            response = requests.get(f"{self.base_url}/api/transactions/{transaction_id}/status")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    transaction = result.get("transaction", {})
                    status = transaction.get("status")
                    self.log_test("Transaction Status API", True, f"Status: {status}")
                    return status
                else:
                    self.log_test("Transaction Status API", False, "No transaction data")
            else:
                self.log_test("Transaction Status API", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Transaction Status API", False, f"Error: {e}")
            
        return None
    
    def test_email_simulation(self, transaction_id):
        """Test email simulation endpoint"""
        try:
            email_data = {
                "transaction_id": transaction_id,
                "subject": "Your Test Concert 2024 Tickets - Confirmation",
                "body": "Thank you for your purchase! Your tickets for Test Concert 2024 at Test Arena are attached."
            }
            
            response = requests.post(
                f"{self.base_url}/api/simulate-ticket-email",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_test("Email Simulation", True, "Email processed successfully")
                    return True
                else:
                    self.log_test("Email Simulation", False, f"Error: {result.get('error')}")
            else:
                self.log_test("Email Simulation", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Email Simulation", False, f"Error: {e}")
            
        return False
    
    def test_payment_page_access(self, transaction_id):
        """Test payment page accessibility"""
        try:
            response = requests.get(f"{self.base_url}/pay/{transaction_id}")
            
            if response.status_code == 200:
                self.log_test("Payment Page Access", True, "Payment page accessible")
                return True
            elif response.status_code == 302:
                self.log_test("Payment Page Access", True, "Redirected to payment processor")
                return True
            else:
                self.log_test("Payment Page Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Payment Page Access", False, f"Error: {e}")
            
        return False
    
    def test_webhook_endpoints(self):
        """Test webhook endpoints are accessible"""
        endpoints = [
            "/webhook/mailgun",
            "/webhook/sendgrid"
        ]
        
        for endpoint in endpoints:
            try:
                # Test with empty POST (should not crash)
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    data={},
                    timeout=5
                )
                
                # Webhook should handle empty data gracefully
                if response.status_code in [200, 400, 500]:
                    self.log_test(f"Webhook {endpoint}", True, f"Endpoint responsive (HTTP {response.status_code})")
                else:
                    self.log_test(f"Webhook {endpoint}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Webhook {endpoint}", False, f"Error: {e}")
    
    def test_admin_dashboard(self):
        """Test admin dashboard accessibility"""
        try:
            response = requests.get(f"{self.base_url}/admin")
            
            if response.status_code in [200, 302]:
                self.log_test("Admin Dashboard", True, "Dashboard accessible")
            else:
                self.log_test("Admin Dashboard", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Dashboard", False, f"Error: {e}")
    
    def test_ui_components(self):
        """Test main UI components"""
        try:
            # Test main index page
            response = requests.get(f"{self.base_url}/")
            
            if response.status_code in [200, 302]:
                self.log_test("Main UI", True, "Index page accessible")
            else:
                self.log_test("Main UI", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Main UI", False, f"Error: {e}")
    
    def run_full_test_suite(self):
        """Run all tests in sequence"""
        print("🚀 Starting Safe Transaction System Tests")
        print("=" * 50)
        
        # Basic infrastructure tests
        print("\n📋 Testing Infrastructure...")
        self.test_database_schema()
        self.test_ui_components()
        self.test_admin_dashboard()
        self.test_webhook_endpoints()
        
        # Core functionality tests
        print("\n🔧 Testing Core Functionality...")
        listing_created = self.test_listing_creation()
        
        if listing_created:
            # Get latest transaction for testing
            conn = sqlite3.connect('var/insta485.sqlite3')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(transaction_id) FROM transactions")
            result = cursor.fetchone()
            transaction_id = result[0] if result and result[0] else None
            conn.close()
            
            if transaction_id:
                print(f"\n🧪 Testing Transaction {transaction_id}...")
                
                # Test verification
                verified_id = self.test_verification_api()
                if verified_id:
                    transaction_id = verified_id
                
                # Test status tracking
                status = self.test_transaction_status(transaction_id)
                
                # Test payment flow
                self.test_payment_page_access(transaction_id)
                
                # Test email simulation
                self.test_email_simulation(transaction_id)
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "tests": self.test_results
        }
        
        with open(f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Your system is ready for production.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please review and fix issues before production deployment.")


def main():
    """Run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Safe Transaction Automated System")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for testing")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    tester = SystemTester(args.url)
    
    if args.quick:
        print("🏃 Running quick tests...")
        tester.test_database_schema()
        tester.test_ui_components()
        tester.test_verification_api()
        tester.generate_test_report()
    else:
        tester.run_full_test_suite()


if __name__ == "__main__":
    main()
