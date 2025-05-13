"""
Health check endpoint for the Python orchestrator.
"""
import json
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Global variable to track service status
_SERVICE_STATUS = "ok"
_VERSION = "1.0.0"  # Update this as needed


def set_service_status(status):
    """
    Set the current service status
    """
    global _SERVICE_STATUS
    _SERVICE_STATUS = status


def set_version(version):
    """
    Set the service version
    """
    global _VERSION
    _VERSION = version


class HealthHandler(BaseHTTPRequestHandler):
    """
    HTTP handler for health check requests
    """

    def do_GET(self):
        """
        Handle GET requests to the health check endpoint
        """
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            health_data = {
                "status": _SERVICE_STATUS,
                "timestamp": datetime.now().isoformat(),
                "version": _VERSION,
            }

            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_health_server(port=8080):
    """
    Start the health check server in a separate thread

    Args:
        port: Port number to listen on (default: 8080)

    Returns:
        server: The HTTPServer instance that was started
        thread: The thread running the server
    """
    server = HTTPServer(("0.0.0.0", port), HealthHandler)

    def run_server():
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    print(f"Health check server started on port {port}")
    return server, thread


def stop_health_server(server):
    """
    Stop the health check server

    Args:
        server: The HTTPServer instance to stop
    """
    if server:
        server.shutdown()
        print("Health check server stopped")
