import os
import http.server
import socketserver
import requests
import json
from urllib.parse import urlparse

def get_deepseek_response(api_key, prompt):
    """Send prompt to DeepSeek API and return the response"""
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling DeepSeek API: {e}")
        return None

def extract_html_from_response(api_response):
    """Extract HTML content from DeepSeek API response"""
    if api_response and 'choices' in api_response and len(api_response['choices']) > 0:
        content = api_response['choices'][0]['message']['content']
        
        # Extract HTML from code blocks if present
        if '```html' in content:
            start = content.find('```html') + 7
            end = content.find('```', start)
            return content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            return content[start:end].strip()
        else:
            return content.strip()
    
    return None

def create_website():
    """Main function to create and serve the website"""
    
    # Get API key from environment variable
    api_key = os.getenv('deepseek_api_key')
    if not api_key:
        print("Error: deepseek_api_key environment variable not set")
        return
    
    # Create the prompt for DeepSeek
    prompt = """
    Create a professional, responsive HTML website for a company called "Primate" that has two automated trading system products: "Tripper" and "Camper".
    
    Requirements:
    - Professional, modern UI with grey, black, white, and light blue color scheme
    - Fully responsive and mobile-friendly
    - Dropdown navigation menu with options: Home, Products (with Tripper and Camper dropdown), About, Contact
    - Under the Tripper tab, show performance over time with mock data (charts/graphs showing ROI progression)
    - Include sections for both products with their descriptions
    - Contact page/form
    - Use mock performance data for demonstration
    
    Design specifications:
    - Color scheme: grey, black, white, and light blue (#3498db or similar)
    - Professional financial/trading company aesthetic
    - Clean, modern typography
    - Responsive grid layout
    
    Please output ONLY the HTML code with embedded CSS and JavaScript, no explanations or markdown formatting.
    """
    
    print("Generating website with DeepSeek API...")
    
    # Get HTML from DeepSeek API
    response = get_deepseek_response(api_key, prompt)
    if not response:
        print("Failed to get response from DeepSeek API")
        return
    
    html_content = extract_html_from_response(response)
    
    if not html_content:
        print("Failed to extract HTML from API response")
        print("Raw response:", json.dumps(response, indent=2))
        return
    
    # Write HTML to file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Website generated successfully! Written to index.html")
    
    # Start web server
    start_web_server()

def start_web_server(port=8000):
    """Start a simple HTTP server to serve the website"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Web server running at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    create_website()
