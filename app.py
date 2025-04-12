from flask import Flask, render_template, request
import subprocess
import os
import socket
import webbrowser

app = Flask(__name__)
process = None

DEFAULT_PORT = "8000"

def get_ip_address():
    """Returns the local IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

@app.route('/', methods=['GET', 'POST'])
def index():
    global process
    message = ''
    ip_address = get_ip_address()  # Get the IP address
    port = request.form.get('port', DEFAULT_PORT)
    folder_path = request.form.get('path', '')  # No default path, user must input

    # Normalize and convert the folder path to absolute
    if folder_path:
        folder_path = os.path.normpath(folder_path)  # Normalize path (handle backslashes on Windows)
        folder_path = os.path.abspath(folder_path)  # Convert to absolute path

        # Check if the path exists
        if not os.path.isdir(folder_path):
            message = f"❌ Path does not exist: {folder_path}"

    if request.method == 'POST':
        action = request.form['action']

        if action == 'Start':
            # Only start the server if it's not already running
            if process is None:
                if not folder_path or not os.path.isdir(folder_path):
                    message = f"❌ Path does not exist: {folder_path}"
                else:
                    try:
                        process = subprocess.Popen(
                            ['python', '-m', 'http.server', port, '--bind', ip_address],
                            cwd=folder_path
                        )
                        message = f"✅ Server started on http://{ip_address}:{port}"
                        webbrowser.open(f"http://{ip_address}:{port}")  # Auto open in browser
                    except Exception as e:
                        message = f"❌ Failed to start server: {e}"
            else:
                message = "⚠️ Server is already running."

        elif action == 'Stop':
            # Stop the server if it's running
            if process is not None:
                process.terminate()
                process.wait()  # Ensure the process terminates correctly
                process = None
                message = "🛑 Server stopped."
            else:
                message = "⚠️ No server is currently running."

    return render_template('index.html', message=message, port=port, folder_path=folder_path, ip_address=ip_address)

if __name__ == '__main__':
    app.run(debug=False)  # Turn off debugging for production
