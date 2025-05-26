#!/usr/bin/env python3
import subprocess
import time
import threading
import sys
import os
import signal

server_process = None

def run_server():
    global server_process
    print("Starting server...")
    server_process = subprocess.Popen([sys.executable, "server.py"])
    server_process.wait()

def run_client():
    print("Waiting 3 seconds for server to start...")
    time.sleep(3)
    print("Starting client attack...")
    subprocess.run([sys.executable, "client.py"])

def cleanup():
    global server_process
    if server_process:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    print("Smart's Attack Demo")
    print("This demo shows how Smart's Attack can break ECC with trace of Frobenius = 1")
    print("=" * 70)
    
    try:
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        run_client()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    finally:
        cleanup()
    
    print("\nDemo completed!")
