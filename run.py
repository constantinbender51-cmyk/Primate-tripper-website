import os
import http.server
import socketserver
import google.generativeai as genai

def get_gemini_response(api_key, prompt):
    """Send prompt to Gemini API and return the response"""
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create the model - using Gemini Flash Lite
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        print("Sending request to Gemini API...")
        # Generate content
        response = model.generate_content(prompt)
        print("✅ Successfully received response from Gemini API")
        return response.text
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return None

def extract_html_from_response(api_response):
    """Extract HTML content from Gemini API response"""
    if not api_response:
        print("❌ No API response received")
        return None
    
    print(f"📄 Raw response length: {len(api_response)} characters")
    print(f"📝 First 500 chars of response: {api_response[:500]}...")
    
    content = api_response.strip()
    
    # Extract HTML from code blocks if present
    if '```html' in content:
        start = content.find('```html') + 7
        end = content.find('```', start)
        html_content = content[start:end].strip()
        print("✅ Extracted HTML from ```html code block")
    elif '```' in content:
        start = content.find('```') + 3
        end = content.find('```', start)
        html_content = content[start:end].strip()
        print("✅ Extracted HTML from ``` code block")
    else:
        html_content = content
        print("✅ Using raw response as HTML")
    
    print(f"🔄 Final HTML length: {len(html_content)} characters")
    print(f"👀 First 200 chars of HTML: {html_content[:200]}...")
    
    return html_content

def create_website():
    """Main function to create and serve the website"""
    
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
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
    
    print("🚀 Generating website with Gemini API...")
    
    # Get HTML from Gemini API
    html_content = get_gemini_response(api_key, prompt)
    
    if not html_content:
        print("❌ Failed to get response from Gemini API")
        return
    
    # Clean and extract HTML
    final_html = extract_html_from_response(html_content)
    
    if not final_html:
        print("❌ Failed to extract HTML from API response")
        return
    
    # Write HTML to file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("✅ Website generated successfully! Written to index.html")
    
    # Verify file was written
    if os.path.exists('index.html'):
        file_size = os.path.getsize('index.html')
        print(f"📁 File verification: index.html exists, size: {file_size} bytes")
    else:
        print("❌ File verification: index.html was not created!")
        return
    
    # Start web server
    start_web_server()

def start_web_server(port=8000):
    """Start a simple HTTP server to serve the website"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verify the file exists before starting server
    if not os.path.exists('index.html'):
        print("❌ Cannot start server: index.html not found!")
        return
        
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 Web server running at http://localhost:{port}")
        print("📍 Serving from directory:", os.getcwd())
        print("📄 Available files:", [f for f in os.listdir('.') if f.endswith('.html')])
        print("🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Shutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    create_website()
