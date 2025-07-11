import requests
import subprocess
import time

def is_ollama_running(ollama_url="http://localhost:11434"):
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_ollama_server():
    """
    Starts the Ollama server in a new PowerShell window.
    """
    subprocess.Popen(
        ["powershell.exe", "-NoExit", "ollama", "serve"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("Starting Ollama server...")

def wait_for_ollama(timeout=30):
    print("Waiting for Ollama to be ready...")
    for _ in range(timeout):
        if is_ollama_running():
            print("Ollama is running.")
            return True
        time.sleep(1)
    print("Ollama did not start in time.")
    return False

def print_available_ollama_models(ollama_url="http://localhost:11434"):
    """
    Prints out available Ollama models by querying the /api/tags endpoint.
    """
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                print("Available Ollama models:")
                for model in models:
                    print(f"- {model.get('name', 'unknown')}")
            else:
                print("No models found.")
        else:
            print(f"Failed to get models. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching models: {e}")
