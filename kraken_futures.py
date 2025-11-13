import os
import http.server
import socketserver
import google.generativeai as genai
import json
from datetime import datetime

# Import the Kraken Futures library
from kraken_futures import KrakenFuturesApi

def fetch_kraken_data():
    """Fetch all account data from Kraken Futures and save to kraken.json"""
    try:
        # Get API keys from environment
        api_key = os.getenv('KRAKEN_API_KEY')
        api_secret = os.getenv('KRAKEN_SECRET_KEY')
        
        if not api_key or not api_secret:
            print("❌ Kraken API keys not found in environment variables")
            return None
        
        print("🔗 Connecting to Kraken Futures API...")
        api = KrakenFuturesApi(api_key, api_secret)
        
        # Fetch comprehensive account data
        print("📊 Fetching account data...")
        kraken_data = {}
        
        # Account information
        kraken_data['accounts'] = api.get_accounts()
        print("✅ Fetched account balances")
        
        # Open positions
        kraken_data['open_positions'] = api.get_open_positions()
        print("✅ Fetched open positions")
        
        # Recent orders
        kraken_data['recent_orders'] = api.get_recent_orders({'limit': 50})  # Last 50 orders
        print("✅ Fetched recent orders")
        
        # Open orders
        kraken_data['open_orders'] = api.get_open_orders()
        print("✅ Fetched open orders")
        
        # Recent fills/trades
        kraken_data['fills'] = api.get_fills({'limit': 50})  # Last 50 fills
        print("✅ Fetched recent fills")
        
        # Add timestamp
        kraken_data['timestamp'] = datetime.now().isoformat()
        kraken_data['data_points'] = len(kraken_data)
        
        # Write to kraken.json
        with open('kraken.json', 'w', encoding='utf-8') as f:
            json.dump(kraken_data, f, indent=2)
        
        print(f"✅ Kraken data saved to kraken.json ({len(json.dumps(kraken_data))} bytes)")
        return kraken_data
        
    except Exception as e:
        print(f"❌ Error fetching Kraken data: {e}")
        return None

def get_gemini_response(api_key, prompt):
    """Send prompt to Gemini API and return the response"""
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create the model - using correct Gemini 2.5 Flash Lite
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        print("🚀 Sending request to Gemini API...")
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
    
    return html_content

def create_website():
    """Main function to create and serve the website"""
    
    # Get Google API key from environment variable
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        return
    
    # Fetch Kraken data first
    kraken_data = fetch_kraken_data()
    if not kraken_data:
        print("❌ Failed to fetch Kraken data, using fallback data")
        # Create minimal fallback data
        kraken_data = {
            'accounts': {'error': 'No Kraken data available'},
            'open_positions': {'error': 'No position data'},
            'timestamp': datetime.now().isoformat()
        }
        with open('kraken.json', 'w', encoding='utf-8') as f:
            json.dump(kraken_data, f, indent=2)
    
    # Read the kraken.json file content for the prompt
    with open('kraken.json', 'r', encoding='utf-8') as f:
        kraken_json_content = f.read()
    
    # Create the prompt for Gemini with Kraken data
    prompt = f"""
    Create a professional, responsive HTML website for a company called "Primate" that has two automated trading system products: "Tripper" and "Camper".

    CRITICAL REQUIREMENT: 
    - This website must display real trading data from Kraken Futures API
    - The data is available in a file called 'kraken.json' in the same directory
    - The JSON data structure includes: accounts, open_positions, recent_orders, open_orders, fills
    - Create comprehensive visualizations and displays for this trading data

    KRAKEN DATA STRUCTURE (for reference):
    {kraken_json_content[:2000]}... [truncated]

    Website Requirements:
    - Professional, modern UI with grey, black, white, and light blue color scheme
    - Fully responsive and mobile-friendly
    - Dropdown navigation menu with options: Home, Products (with Tripper and Camper dropdown), Trading Dashboard, About, Contact
    - Under the Trading Dashboard, display comprehensive Kraken account data including:
        * Account balances and equity
        * Open positions with current P/L
        * Recent order history
        * Open orders
        * Recent trade fills
        * Performance charts and metrics
    - Include sections for both Tripper and Camper products with their descriptions
    - Contact page/form
    - Use the actual Kraken data for all trading displays

    Design specifications:
    - Color scheme: grey, black, white, and light blue (#3498db or similar)
    - Professional financial/trading company aesthetic
    - Clean, modern typography
    - Responsive grid layout
    - Include interactive charts and data visualizations
    - Create a comprehensive trading dashboard

    IMPORTANT: The HTML should be designed to read and display data from 'kraken.json'
    Use JavaScript to fetch and parse the JSON file and update the dashboard displays.

    Please output ONLY the HTML code with embedded CSS and JavaScript, no explanations or markdown formatting.
    Return complete, valid HTML5 document.
    """
    
    print("🌐 Generating website with real Kraken trading data...")
    
    # Get HTML from Gemini API
    html_content = get_gemini_response(google_api_key, prompt)
    
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
    
    # Verify files were written
    if os.path.exists('index.html'):
        file_size = os.path.getsize('index.html')
        print(f"📁 File verification: index.html exists, size: {file_size} bytes")
    
    if os.path.exists('kraken.json'):
        file_size = os.path.getsize('kraken.json')
        print(f"📊 Data verification: kraken.json exists, size: {file_size} bytes")
    
    # Start web server on port 8080
    start_web_server()

def start_web_server(port=8080):
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
        print("📄 Available files:", [f for f in os.listdir('.') if f.endswith(('.html', '.json'))])
        print("🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Shutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    create_website()
