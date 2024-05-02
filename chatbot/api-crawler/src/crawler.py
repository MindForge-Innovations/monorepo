import requests
import json  
import time  
import numpy as np

def fetch_API_doc(url: str, fileName: str):
    """
    gets openAPI documentation for the given URL and writes the result in a file as JSON list.

    Parameters:
        url (str): The starting URL to fetch data.
    """
   
    try:
        # Initialize an empty list to store JSON objects
        json_list = []
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            services = data.get('services', [])  # Extract 'services' list
            for service in services:
                service_url = service.get('url')  # Extract 'url' field from each service
                if service_url:
                    # Construct URL to fetch openapi.json
                    service_url = service_url + "openapi.json"
                    # Make a GET request to the service_url
                    service_response = requests.get(service_url)
                    if service_response.status_code == 200:
                        json_list.append(service_response.json())
                        print(f"Successfully fetched JSON for URL: {service_url}")
                    else:
                        print(f"Failed to fetch JSON for URL: {service_url}, Status code: {service_response.status_code}")
            
            # Save the JSON output in a file
            with open(f"{fileName}.json", "w") as f:
                json.dump(json_list, f, indent=4)
            print("JSON output saved successfully.")

        else:
            print(f"Failed to crawl: {url}, Status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to crawl: {url}, Error: {e}")

if __name__ == "__main__":
    starting_url = "https://backend-core-engine-swiss-ai-center.kube.isc.heia-fr.ch/services?&order_by=name&order=asc&with_count=True&status=AVAILABLE"
    fetch_API_doc(starting_url,"APIdocumentation")
