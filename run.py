import subprocess
import os
import sys
import time
from pathlib import Path

def run_platform():
    root_dir = Path(__file__).parent.absolute()
    
    # 1. Start Backend (FastAPI)
    print("🚀 Starting CardioQSPR Backend (FastAPI)...")
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = str(root_dir / "src")
    
    backend_proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "api:app", 
            "--reload", 
            "--reload-dir", ".",  # Watch only the src directory
            "--host", "0.0.0.0", 
            "--port", "5555"
        ],
        cwd=root_dir / "src",
        env=backend_env
    )
    
    # Wait a bit for backend (reduced as frontend is now asynchronous)
    time.sleep(1)
    
    # 2. Start Frontend (Vite)
    print("🎨 Starting CardioQSPR Frontend (Vite)...")
    frontend_dir = root_dir / "frontend"
    
    # Find npm in standard Mac paths if not in PATH
    npm_path = "npm"
    possible_paths = ["/opt/homebrew/bin/npm", "/usr/local/bin/npm"]
    for p in possible_paths:
        if os.path.exists(p):
            npm_path = p
            break

    frontend_proc = subprocess.Popen(
        [npm_path, "run", "dev"],
        cwd=frontend_dir
    )
    
    print("\n✅ CardioQSPR Platform is running!")
    print("🔗 Backend API: http://localhost:5555/docs")
    print("🔗 Frontend UI: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    run_platform()
