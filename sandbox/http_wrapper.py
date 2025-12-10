#!/usr/bin/env python3
"""
HTTP Wrapper for sandbox-mcp
Provides an HTTP API interface to the sandbox-mcp stdio server
"""
import json
import subprocess
import threading
import queue
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Global process and queues for sandbox-mcp communication
sandbox_process = None
request_queue = queue.Queue()
response_queue = queue.Queue()

def start_sandbox_process():
    """Start the sandbox-mcp process in stdio mode"""
    global sandbox_process
    sandbox_process = subprocess.Popen(
        ['/usr/local/bin/sandbox-mcp', '--stdio'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    print(f"Started sandbox-mcp process with PID: {sandbox_process.pid}", file=sys.stderr)
    return sandbox_process

def send_mcp_request(method, params=None):
    """Send a request to sandbox-mcp and get response"""
    global sandbox_process
    
    if sandbox_process is None or sandbox_process.poll() is not None:
        sandbox_process = start_sandbox_process()
    
    request_id = threading.get_ident()
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    try:
        # Send request
        sandbox_process.stdin.write(json.dumps(request) + '\n')
        sandbox_process.stdin.flush()
        
        # Read response
        response_line = sandbox_process.stdout.readline()
        if response_line:
            return json.loads(response_line)
        return {"error": "No response from sandbox-mcp"}
    except Exception as e:
        return {"error": str(e)}

class SandboxHandler(BaseHTTPRequestHandler):
    """HTTP handler for sandbox-mcp requests"""
    
    def log_message(self, format, *args):
        """Override to use stderr for logging"""
        print(f"{self.address_string()} - {format % args}", file=sys.stderr)
    
    def send_json_response(self, data, status=200):
        """Send a JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_json_response({
                'status': 'healthy',
                'service': 'sandbox-mcp',
                'message': 'Sandbox MCP HTTP wrapper is running'
            })
        elif self.path == '/tools':
            # List available sandbox tools
            response = send_mcp_request("tools/list")
            self.send_json_response(response)
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_json_response({'error': 'Invalid JSON'}, 400)
            return
        
        if self.path == '/execute':
            # Execute code in sandbox
            sandbox_type = data.get('sandbox', 'python')
            code = data.get('code', '')
            
            response = send_mcp_request("tools/call", {
                "name": f"run_{sandbox_type}",
                "arguments": {
                    "code": code
                }
            })
            self.send_json_response(response)
        
        elif self.path == '/call':
            # Generic MCP tool call
            method = data.get('method', 'tools/list')
            params = data.get('params', {})
            response = send_mcp_request(method, params)
            self.send_json_response(response)
        
        else:
            self.send_json_response({'error': 'Not found'}, 404)

def main():
    """Main entry point"""
    print("Starting Sandbox MCP HTTP Wrapper...", file=sys.stderr)
    
    # Start sandbox-mcp process
    start_sandbox_process()
    
    # Start HTTP server
    server = HTTPServer(('0.0.0.0', 8001), SandboxHandler)
    print("Sandbox MCP HTTP Wrapper listening on port 8001", file=sys.stderr)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        if sandbox_process:
            sandbox_process.terminate()
        server.shutdown()

if __name__ == '__main__':
    main()
