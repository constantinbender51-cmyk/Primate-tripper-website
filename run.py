import os
import http.server
import socketserver
import google.generativeai as genai

def get_gemini_response(api_key, prompt):
    """Send prompt to Gemini API and return the response"""
    try:
        print("calling Gemini...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create the model - using Gemini Flash 2.5
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

def extract_html_from_response(api_response):
    """Extract HTML content from Gemini API response"""
    if not api_response:
        return None
    
    content = api_response.strip()
    
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
        return content

def create_website():
    """Main function to create and serve the website"""
    
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google AI Studio API key as environment variable")
        return
    
    # Create the prompt for Gemini
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
    - Include interactive elements for the performance charts
    
    Please output ONLY the HTML code with embedded CSS and JavaScript, no explanations or markdown formatting.
    Return complete, valid HTML5 document.
    """
    
    print("Generating website with Gemini API...")
    
    # Get HTML from Gemini API
    html_content = get_gemini_response(api_key, prompt)
    
    if not html_content:
        print("Failed to get response from Gemini API")
        return
    
    # Clean and extract HTML
    final_html = extract_html_from_response(html_content)
    
    if not final_html:
        print("Failed to extract HTML from API response")
        return
    
    # Write HTML to file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
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
