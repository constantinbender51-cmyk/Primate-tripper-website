import os
import http.server
import socketserver
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import time
import threading

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
    """Extract HTML content from Gemini API response - handles both code blocks and pure HTML"""
    if not api_response:
        print("❌ No API response received")
        return None
    
    print(f"📄 Raw response length: {len(api_response)} characters")
    
    content = api_response.strip()
    
    # Method 1: Extract from HTML code blocks
    if '```html' in content:
        start = content.find('```html') + 7
        end = content.find('```', start)
        html_content = content[start:end].strip()
        print("✅ Extracted HTML from ```html code block")
    
    # Method 2: Extract from generic code blocks
    elif '```' in content:
        start = content.find('```') + 3
        end = content.find('```', start)
        html_content = content[start:end].strip()
        print("✅ Extracted HTML from ``` code block")
    
    # Method 3: Extract pure HTML document (look for <html tag)
    elif '<html' in content.lower():
        start = content.lower().find('<html')
        # Find the closing </html> tag
        html_end = content.lower().rfind('</html>')
        if html_end != -1:
            html_content = content[start:html_end + 7].strip()  # +7 to include </html>
            print("✅ Extracted pure HTML document (found <html> and </html> tags)")
        else:
            # If no closing tag, take everything from <html onwards
            html_content = content[start:].strip()
            print("✅ Extracted HTML starting from <html tag (no closing tag found)")
    
    # Method 4: Final fallback - use entire response
    else:
        html_content = content
        print("✅ Using entire response as HTML (no code blocks or HTML tags detected)")
    
    print(f"🔄 Final HTML length: {len(html_content)} characters")
    
    # Verify we have valid HTML
    if '<!DOCTYPE' in html_content.upper() or '<HTML' in html_content.upper():
        print("📋 HTML validation: Document has proper DOCTYPE or HTML structure")
    elif '<head' in html_content.lower() or '<body' in html_content.lower():
        print("📋 HTML validation: Document has head/body structure")
    else:
        print("⚠️  HTML validation: No clear HTML structure detected")
    
    return html_content

def generate_website():
    """Generate the website with current Kraken data"""
    # Get Google API key from environment variable
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        return False
    
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
    output HTML nothing else
    create a website for a company called primate which automates trading systems technical information about tripper the only currently live deployed algorithm can be found in the file kraken.json which contains the following: {kraken_json_content}
    create a mobile friendly website designed around the data inside kraken.json
    """
    
    print("🌐 Generating website with real Kraken trading data...")
    
    # Print the entire prompt with delays between lines
    print("\n" + "="*80)
    print("PROMPT SENT TO GEMINI:")
    print("="*80)
    
    prompt_lines = prompt.split('\n')
    for i, line in enumerate(prompt_lines):
        print(line)
        if i < len(prompt_lines) - 1:  # Don't sleep after the last line
            time.sleep(0.1)
    
    print("="*80)
    print("END OF PROMPT")
    print("="*80 + "\n")
    
    # Get HTML from Gemini API
    html_content = get_gemini_response(google_api_key, prompt)
    
    if not html_content:
        print("❌ Failed to get response from Gemini API")
        return False
    
    # Clean and extract HTML
    final_html = extract_html_from_response(html_content)
    
    if not final_html:
        print("❌ Failed to extract HTML from API response")
        return False
    
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
    
    return True

def calculate_next_hour():
    """Calculate seconds until next full hour"""
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    seconds_until_next_hour = (next_hour - now).total_seconds()
    return seconds_until_next_hour

def update_loop():
    """Main update loop that runs every full hour"""
    print("🔄 Starting hourly update loop...")
    
    while True:
        # Generate website immediately on first run
        success = generate_website()
        if success:
            print(f"✅ Website update completed at {datetime.now()}")
        else:
            print(f"❌ Website update failed at {datetime.now()}")
        
        # Calculate sleep time until next full hour
        sleep_seconds = calculate_next_hour()
        next_update = datetime.now() + timedelta(seconds=sleep_seconds)
        print(f"⏰ Next update scheduled for: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💤 Sleeping for {sleep_seconds:.0f} seconds...")
        
        # Sleep until next full hour
        time.sleep(sleep_seconds)

def start_web_server(port=8080):
    """Start a simple HTTP server to serve the website"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Verify the files exist before starting server
    if not os.path.exists('index.html'):
        print("❌ Cannot start server: index.html not found!")
        return
        
    if not os.path.exists('kraken.json'):
        print("❌ Cannot start server: kraken.json not found!")
        return
        
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 Web server running at http://localhost:{port}")
        print("📍 Serving from directory:", os.getcwd())
        print("📄 Available files:", [f for f in os.listdir('.') if f.endswith(('.html', '.json'))])
        print("🔗 kraken.json will be available at: http://localhost:8080/kraken.json")
        print("📊 The HTML page can fetch data from this URL")
        print("🛑 Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Shutting down web server...")
            httpd.shutdown()

if __name__ == "__main__":
    # Start web server in a separate thread
    server_thread = threading.Thread(target=start_web_server, daemon=True)
    server_thread.start()
    
    # Start the hourly update loop in main thread
    update_loop()
