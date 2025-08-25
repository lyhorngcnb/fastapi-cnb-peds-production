#!/usr/bin/env python3
"""
Test script for Customer Management API
Run this script to test the customer endpoints
"""

import requests
import json
import time
from typing import Optional

class CustomerAPITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.auth_token: Optional[str] = None
        
    def login(self, email: str, password: str) -> bool:
        """Login and get JWT token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                print(f"✅ Login successful for {email}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self) -> dict:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def create_customer(self, customer_data: dict) -> Optional[dict]:
        """Create a new customer"""
        try:
            response = requests.post(
                f"{self.base_url}/api/customers/",
                headers=self.get_headers(),
                json=customer_data
            )
            
            if response.status_code == 201:
                customer = response.json()
                print(f"✅ Customer created: {customer['first_name']} {customer['last_name']} (ID: {customer['id']})")
                return customer
            else:
                print(f"❌ Create customer failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Create customer error: {e}")
            return None
    
    def get_customers(self, search: str = None, limit: int = 10) -> Optional[dict]:
        """Get customers with optional search"""
        try:
            params = {"limit": limit}
            if search:
                params["search"] = search
                
            response = requests.get(
                f"{self.base_url}/api/customers/",
                headers=self.get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved {len(data['customers'])} customers (Total: {data['total']})")
                return data
            else:
                print(f"❌ Get customers failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Get customers error: {e}")
            return None
    
    def get_customer(self, customer_id: int) -> Optional[dict]:
        """Get a specific customer"""
        try:
            response = requests.get(
                f"{self.base_url}/api/customers/{customer_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                customer = response.json()
                print(f"✅ Retrieved customer: {customer['first_name']} {customer['last_name']}")
                return customer
            else:
                print(f"❌ Get customer failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Get customer error: {e}")
            return None
    
    def update_customer(self, customer_id: int, update_data: dict) -> Optional[dict]:
        """Update a customer"""
        try:
            response = requests.put(
                f"{self.base_url}/api/customers/{customer_id}",
                headers=self.get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                customer = response.json()
                print(f"✅ Customer updated: {customer['first_name']} {customer['last_name']}")
                return customer
            else:
                print(f"❌ Update customer failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Update customer error: {e}")
            return None
    
    def upload_image(self, customer_id: int, image_type: str, file_path: str) -> Optional[dict]:
        """Upload an image for a customer"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                response = requests.post(
                    f"{self.base_url}/api/customers/{customer_id}/images/{image_type}",
                    headers=headers,
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Image uploaded: {result['file_name']} ({result['file_size']} bytes)")
                return result
            else:
                print(f"❌ Upload image failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Upload image error: {e}")
            return None
    
    def get_image_url(self, customer_id: int, image_type: str) -> Optional[str]:
        """Get presigned URL for an image"""
        try:
            response = requests.get(
                f"{self.base_url}/api/customers/{customer_id}/images/{image_type}/url",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Image URL retrieved: {data['file_url'][:50]}...")
                return data['file_url']
            else:
                print(f"❌ Get image URL failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Get image URL error: {e}")
            return None

def main():
    """Main test function"""
    print("🧾 Customer Management API Test")
    print("=" * 50)
    
    # Initialize tester
    tester = CustomerAPITester()
    
    # Test login (you'll need to create a user first or use existing credentials)
    print("\n1. Testing Login...")
    if not tester.login("admin@example.com", "password"):
        print("⚠️  Login failed. Please create a user first or check credentials.")
        print("   You can create a user using the auth endpoints.")
        return
    
    # Test customer creation
    print("\n2. Testing Customer Creation...")
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "national_id": "1234567890",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "phone_number": "+1234567890",
        "email": "john.doe@example.com",
        "address": "123 Main St, City, Country"
    }
    
    customer = tester.create_customer(customer_data)
    if not customer:
        print("❌ Customer creation failed. Stopping tests.")
        return
    
    customer_id = customer['id']
    
    # Test getting customers
    print("\n3. Testing Get Customers...")
    customers_data = tester.get_customers(search="John", limit=5)
    
    # Test getting specific customer
    print("\n4. Testing Get Specific Customer...")
    retrieved_customer = tester.get_customer(customer_id)
    
    # Test updating customer
    print("\n5. Testing Update Customer...")
    update_data = {
        "phone_number": "+1987654321",
        "address": "456 Oak Ave, New City, Country"
    }
    updated_customer = tester.update_customer(customer_id, update_data)
    
    # Test image upload (if you have a test image)
    print("\n6. Testing Image Upload...")
    print("   Note: This requires a test image file.")
    print("   Create a test image or comment out this section.")
    
    # Uncomment the following lines if you have a test image:
    # image_result = tester.upload_image(customer_id, "photo", "test_image.jpg")
    # if image_result:
    #     print("\n7. Testing Get Image URL...")
    #     image_url = tester.get_image_url(customer_id, "photo")
    
    print("\n✅ Test completed!")
    print(f"   Customer ID: {customer_id}")
    print(f"   You can view the customer at: {tester.base_url}/api/customers/{customer_id}")

if __name__ == "__main__":
    main() 