from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import sys
import time
from urllib.parse import parse_qs, urlparse

# Add parent directory to PYTHONPATH for importing agents
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

try:
    from agents.conversation import AgentConversation
    from backend.view import UserInfo
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)

class SimulationHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        
    def do_GET(self):
        if self.path == '/':
            # Serve the index.html file
            self._serve_file('insurance-dashboard-app/index.html', 'text/html')
        elif self.path.endswith('.js'):
            # Serve JavaScript files
            self._serve_file(f'insurance-dashboard-app{self.path}', 'application/javascript')
        elif self.path.endswith('.css'):
            # Serve CSS files
            self._serve_file(f'insurance-dashboard-app{self.path}', 'text/css')
        else:
            # Default response for unknown paths
            self._set_headers()
            self.wfile.write(json.dumps({'message': 'Insurance Simulation API'}).encode())

    def _serve_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as file:
                self._set_headers(content_type)
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')

    def do_POST(self):
        if self.path == '/api/simulate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse the JSON data
                data = json.loads(post_data.decode('utf-8'))
                
                # Process simulation
                result = self._run_simulation(data)
                
                # Return the result
                self._set_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _run_simulation(self, data):
        """Run simulation for each user profile in the data"""
        if 'profiles' not in data:
            return {'error': 'No user profiles provided'}
        
        user_profiles = data['profiles']
        max_turns = data.get('max_turns', 5)
        
        # Store simulation results
        results = {
            'summary': {
                'total_samples': len(user_profiles),
                'success_count': 0,
                'success_rate': 0,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'conversations': []
        }
        
        # Process each user profile
        for i, user_info_dict in enumerate(user_profiles):
            try:
                # Create UserInfo object
                user_info = UserInfo(**user_info_dict)
                
                # Create conversation agent
                conversation = AgentConversation(user_info, max_turns=max_turns)
                
                # Run simulation
                conversation.simulate_conversation()
                
                # Get enhanced log
                enhanced_data = conversation.get_enhanced_log()
                results['conversations'].append(enhanced_data)
                
                # Update success counter
                if conversation.success:
                    results['summary']['success_count'] += 1
            except Exception as e:
                print(f"Error processing user {i+1}: {e}")
                results['conversations'].append({
                    'error': str(e),
                    'user_info': user_info_dict.get('user', {}).get('name', f'User {i+1}')
                })
        
        # Calculate success rate
        total = results['summary']['total_samples']
        success_count = results['summary']['success_count']
        results['summary']['success_rate'] = (success_count / total * 100) if total > 0 else 0
        
        return results

def run(server_class=HTTPServer, handler_class=SimulationHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run() 