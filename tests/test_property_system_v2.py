#!/usr/bin/env python3
"""
Comprehensive test script for the Property Evaluation System
Tests the complete flow from login to property creation and management
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class PropertySystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_data = {}
        
    def print_step(self, step, description):
        """Print a formatted step header"""
        print(f"\n{'='*60}")
        print(f"STEP {step}: {description}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")
    
    def test_login(self):
        """Test user login and get JWT token"""
        self.print_step(1, "Testing User Login")
        
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.print_success(f"Login successful! Token received: {self.token[:20]}...")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Login error: {str(e)}")
            return False
    
    def test_get_customers(self):
        """Test getting customers for property creation"""
        self.print_step(2, "Getting Customers for Property Creation")
        
        try:
            response = self.session.get(f"{BASE_URL}/customers/")
            
            if response.status_code == 200:
                data = response.json()
                customers = data.get("customers", [])
                if customers:
                    self.test_data["customer_id"] = customers[0]["id"]
                    self.print_success(f"Found {len(customers)} customers. Using customer ID: {self.test_data['customer_id']}")
                    return True
                else:
                    self.print_error("No customers found. Please create a customer first.")
                    return False
            else:
                self.print_error(f"Failed to get customers: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Get customers error: {str(e)}")
            return False
    
    def test_get_loan_requests(self):
        """Test getting loan requests for property creation"""
        self.print_step(3, "Getting Loan Requests for Property Creation")
        
        try:
            response = self.session.get(f"{BASE_URL}/loan-requests/")
            
            if response.status_code == 200:
                data = response.json()
                loan_requests = data.get("loan_requests", [])
                if loan_requests:
                    self.test_data["loan_request_id"] = loan_requests[0]["id"]
                    self.print_success(f"Found {len(loan_requests)} loan requests. Using loan request ID: {self.test_data['loan_request_id']}")
                    return True
                else:
                    self.print_error("No loan requests found. Please create a loan request first.")
                    return False
            else:
                self.print_error(f"Failed to get loan requests: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Get loan requests error: {str(e)}")
            return False
    
    def test_get_locations(self):
        """Test getting location data"""
        self.print_step(4, "Getting Location Data")
        
        try:
            # Get provinces
            response = self.session.get(f"{BASE_URL}/properties/enums/ownership-titles")
            if response.status_code == 200:
                self.print_success("Ownership title enums retrieved successfully")
            
            response = self.session.get(f"{BASE_URL}/properties/enums/property-types")
            if response.status_code == 200:
                self.print_success("Property type enums retrieved successfully")
            
            response = self.session.get(f"{BASE_URL}/properties/enums/title-types")
            if response.status_code == 200:
                self.print_success("Title type enums retrieved successfully")
            
            response = self.session.get(f"{BASE_URL}/properties/enums/measurement-info")
            if response.status_code == 200:
                self.print_success("Measurement info enums retrieved successfully")
            
            response = self.session.get(f"{BASE_URL}/properties/enums/source-types")
            if response.status_code == 200:
                self.print_success("Source type enums retrieved successfully")
            
            return True
                
        except Exception as e:
            self.print_error(f"Get locations error: {str(e)}")
            return False
    
    def test_create_property(self):
        """Test creating a property"""
        self.print_step(5, "Creating a Property")
        
        try:
            property_data = {
                "requester_id": self.test_data["loan_request_id"],
                "ownership_title": "Yes",
                "owner_1_id": self.test_data["customer_id"],
                "type_of_property": "Residential land",
                "information_property": "Test property for evaluation",
                "land_details": [
                    {
                        "land_size": 100.50,
                        "front": 10.00,
                        "back": 10.00,
                        "length": 10.05,
                        "width": 10.00,
                        "flat_unit_type": "Villa",
                        "number_of_lot": 1
                    }
                ],
                "building_details": [
                    {
                        "source_type": "Branch",
                        "description": "Villa",
                        "total_building_area": 150.00,
                        "building_width": 12.00,
                        "building_length": 12.50,
                        "number_of_floors": 2,
                        "estimated_size": 150.00,
                        "remark": "Test building details"
                    }
                ],
                "google_maps": [
                    {
                        "map_coordinates": "{\"lat\": 11.5564, \"lng\": 104.9282}",
                        "map_color": "green"
                    }
                ]
            }
            
            response = self.session.post(f"{BASE_URL}/properties/", json=property_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["property_id"] = data["id"]
                self.test_data["property_code"] = data["property_code"]
                self.print_success(f"Property created successfully! ID: {data['id']}, Code: {data['property_code']}")
                return True
            else:
                self.print_error(f"Failed to create property: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Create property error: {str(e)}")
            return False
    
    def test_get_property(self):
        """Test getting the created property"""
        self.print_step(6, "Getting Created Property")
        
        try:
            property_id = self.test_data["property_id"]
            response = self.session.get(f"{BASE_URL}/properties/{property_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Property retrieved successfully! Code: {data['property_code']}")
                self.print_info(f"Land details: {len(data.get('land_details', []))} records")
                self.print_info(f"Building details: {len(data.get('building_details', []))} records")
                self.print_info(f"Google maps: {len(data.get('google_maps', []))} records")
                return True
            else:
                self.print_error(f"Failed to get property: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Get property error: {str(e)}")
            return False
    
    def test_get_properties_list(self):
        """Test getting properties list with filters"""
        self.print_step(7, "Getting Properties List")
        
        try:
            # Test basic list
            response = self.session.get(f"{BASE_URL}/properties/")
            
            if response.status_code == 200:
                data = response.json()
                properties = data.get("properties", [])
                total = data.get("total", 0)
                self.print_success(f"Properties list retrieved successfully! Total: {total}")
                
                # Test search filter
                property_code = self.test_data["property_code"]
                response = self.session.get(f"{BASE_URL}/properties/?search={property_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    filtered_properties = data.get("properties", [])
                    self.print_success(f"Search filter working! Found {len(filtered_properties)} properties")
                
                return True
            else:
                self.print_error(f"Failed to get properties list: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Get properties list error: {str(e)}")
            return False
    
    def test_property_statistics(self):
        """Test property statistics"""
        self.print_step(8, "Getting Property Statistics")
        
        try:
            response = self.session.get(f"{BASE_URL}/properties/statistics/")
            
            if response.status_code == 200:
                data = response.json()
                total_properties = data.get("total_properties", 0)
                self.print_success(f"Statistics retrieved successfully! Total properties: {total_properties}")
                self.print_info(f"By property type: {data.get('by_property_type', {})}")
                self.print_info(f"By ownership title: {data.get('by_ownership_title', {})}")
                return True
            else:
                self.print_error(f"Failed to get statistics: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Get statistics error: {str(e)}")
            return False
    
    def test_add_land_detail(self):
        """Test adding additional land detail"""
        self.print_step(9, "Adding Additional Land Detail")
        
        try:
            property_id = self.test_data["property_id"]
            land_detail_data = {
                "land_size": 200.00,
                "front": 15.00,
                "back": 15.00,
                "length": 13.33,
                "width": 15.00,
                "flat_unit_type": "Garden",
                "number_of_lot": 2
            }
            
            response = self.session.post(f"{BASE_URL}/properties/{property_id}/land-details", json=land_detail_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["land_detail_id"] = data["id"]
                self.print_success(f"Land detail added successfully! ID: {data['id']}")
                return True
            else:
                self.print_error(f"Failed to add land detail: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Add land detail error: {str(e)}")
            return False
    
    def test_add_building_detail(self):
        """Test adding additional building detail"""
        self.print_step(10, "Adding Additional Building Detail")
        
        try:
            property_id = self.test_data["property_id"]
            building_detail_data = {
                "source_type": "Agency",
                "agency_name": "CPL Real Estate",
                "description": "Swimming Pool",
                "total_building_area": 50.00,
                "building_width": 10.00,
                "building_length": 5.00,
                "number_of_floors": 1,
                "estimated_size": 50.00,
                "remark": "Additional facility"
            }
            
            response = self.session.post(f"{BASE_URL}/properties/{property_id}/buildings", json=building_detail_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_data["building_detail_id"] = data["id"]
                self.print_success(f"Building detail added successfully! ID: {data['id']}")
                return True
            else:
                self.print_error(f"Failed to add building detail: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Add building detail error: {str(e)}")
            return False
    
    def test_update_property(self):
        """Test updating property"""
        self.print_step(11, "Updating Property")
        
        try:
            property_id = self.test_data["property_id"]
            update_data = {
                "information_property": "Updated test property information",
                "remark": "Property updated successfully"
            }
            
            response = self.session.put(f"{BASE_URL}/properties/{property_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Property updated successfully! Updated at: {data['updated_at']}")
                return True
            else:
                self.print_error(f"Failed to update property: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Update property error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Property Evaluation System Tests")
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            self.test_login,
            self.test_get_customers,
            self.test_get_loan_requests,
            self.test_get_locations,
            self.test_create_property,
            self.test_get_property,
            self.test_get_properties_list,
            self.test_property_statistics,
            self.test_add_land_detail,
            self.test_add_building_detail,
            self.test_update_property
        ]
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(tests, 1):
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
                    print(f"⚠️  Test {i} failed, but continuing with remaining tests...")
            except Exception as e:
                failed += 1
                self.print_error(f"Test {i} crashed: {str(e)}")
                print(f"⚠️  Continuing with remaining tests...")
            
            time.sleep(1)  # Small delay between tests
        
        # Final summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if failed == 0:
            print("\n🎉 All tests passed! Property Evaluation System is working correctly!")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    tester = PropertySystemTester()
    tester.run_all_tests() 