
import requests
import base64
import json

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"

def test_verify_product():
    """Test the product verification endpoint"""
    
    # Sample data - replace with actual values
    test_data = {
        "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",  # Sample base64 image
        "barcode": "barcode",
        "weight": 250.5,
        "battery_percentage": 85
    }
    
    try:
        response = requests.post(
            'https://e-bag-test.replit.app/verify-product',
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if "WEIGHT_MISMATCH" in response.json()["status"]:
            print("Test passed: Weight mismatch detected")
        
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_verify_product()
