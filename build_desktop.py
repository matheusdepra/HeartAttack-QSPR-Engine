import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def get_target_triple():
    # Try rustc first
    try:
        output = subprocess.check_output(["rustc", "-Vv"], text=True)
        for line in output.splitlines():
            if line.startswith("host:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    
    # Fallback to manual mapping based on OS and architecture
    sys_type = platform.system()
    machine = platform.machine()
    
    if sys_type == "Darwin":
        if machine == "arm64":
            return "aarch64-apple-darwin"
        else:
            return "x86_64-apple-darwin"
    elif sys_type == "Windows":
        if machine in ["AMD64", "x86_64"]:
            return "x86_64-pc-windows-msvc"
        elif machine == "ARM64":
            return "aarch64-pc-windows-msvc"
    elif sys_type == "Linux":
        if machine in ["x86_64", "amd64"]:
            return "x86_64-unknown-linux-gnu"
            
    raise Exception(f"Unsupported compilation platform: {sys_type} {machine}")

def build_desktop():
    print("🚀 Starting CardioQSPR Desktop Build Process...")
    
    # 1. Generate Icons if not already done
    icons_dir = ROOT_DIR / "src-tauri" / "icons"
    logo_path = Path("/Users/matheusdepra/.gemini/antigravity-ide/brain/0031be42-6dd3-4177-aa22-459732023f44/cardio_logo_1784375464768.png")
    
    if not (icons_dir / "icon.ico").exists() and logo_path.exists():
        print("🎨 Converting logo to genuine PNG format...")
        temp_logo = ROOT_DIR / "src-tauri" / "temp_logo.png"
        os.makedirs(ROOT_DIR / "src-tauri", exist_ok=True)
        try:
            from PIL import Image
            with Image.open(logo_path) as img:
                img.save(temp_logo, "PNG")
            logo_to_use = temp_logo
        except Exception as e:
            print(f"⚠️ Failed to convert logo using PIL: {e}")
            logo_to_use = logo_path
            
        print("🎨 Generating Tauri icons from application logo...")
        os.makedirs(icons_dir, exist_ok=True)
        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
        try:
            subprocess.run([
                npx_cmd, "-y", "@tauri-apps/cli@2", "icon", str(logo_to_use),
                "--output", str(icons_dir)
            ], check=True)
            print("✅ Icons generated successfully.")
        except Exception as e:
            print(f"⚠️ Failed to generate icons automatically: {e}")
        finally:
            if temp_logo.exists():
                try:
                    os.remove(temp_logo)
                except Exception:
                    pass

    
    # 2. Build Frontend React Assets
    frontend_dir = ROOT_DIR / "frontend"
    print("🎨 Compiling React Frontend static assets...")
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)
        
    # We build the React production bundle, setting VITE_API_HOST environment variable
    # so the frontend knows how to communicate with local FastAPI server
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_HOST"] = "http://localhost:5555"
    subprocess.run([npm_cmd, "run", "build"], cwd=frontend_dir, env=frontend_env, check=True)
    print("✅ Frontend compiled successfully.")
    
    # 3. Check and Install PyInstaller in active venv
    venv_bin = "Scripts" if platform.system() == "Windows" else "bin"
    venv_pyinstaller = ROOT_DIR / "venv" / venv_bin / "pyinstaller"
    if platform.system() == "Windows":
        venv_pyinstaller = Path(str(venv_pyinstaller) + ".exe")
        
    pyinstaller_path = shutil.which("pyinstaller")
    
    if venv_pyinstaller.exists():
        pyinstaller_cmd = str(venv_pyinstaller)
    elif pyinstaller_path:
        pyinstaller_cmd = pyinstaller_path
    else:
        print("🐍 PyInstaller not found. Installing in active Python virtualenv...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        pyinstaller_cmd = str(venv_pyinstaller) if venv_pyinstaller.exists() else "pyinstaller"
        
    # 4. Compile FastAPI backend into a single executable
    print("🐍 Compiling FastAPI backend with PyInstaller...")
    
    # Hidden imports and package collection configurations
    pyinstaller_args = [
        pyinstaller_cmd,
        "--name", "api",
        "--onefile",
        "--clean",
        "--collect-all", "rdkit",
        "--collect-all", "thermo",
        "--collect-all", "chemicals",
        "--collect-all", "fluids",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        str(ROOT_DIR / "src" / "api.py")
    ]
    
    subprocess.run(pyinstaller_args, check=True)
    print("✅ Backend compiled successfully.")
    
    # 5. Position PyInstaller binary as a sidecar for Tauri
    triple = get_target_triple()
    binary_ext = ".exe" if platform.system() == "Windows" else ""
    src_binary = ROOT_DIR / "dist" / f"api{binary_ext}"
    
    target_dir = ROOT_DIR / "src-tauri" / "binaries"
    os.makedirs(target_dir, exist_ok=True)
    
    dest_binary = target_dir / f"api-{triple}{binary_ext}"
    print(f"🚚 Copying compiled backend binary to Tauri sidecar path: {dest_binary}")
    shutil.copy2(src_binary, dest_binary)
    print("✅ Backend sidecar setup completed.")
    
    # 6. Execute Tauri build to bundle everything into native installers (.msi / .dmg)
    print("🦀 Running Tauri build compiler...")
    npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
    subprocess.run([
        npx_cmd, "-y", "@tauri-apps/cli@2", "build"
    ], cwd=ROOT_DIR, check=True)
    print("🎉 CardioQSPR Desktop Application successfully compiled and packaged!")

if __name__ == "__main__":
    try:
        build_desktop()
    except Exception as e:
        print(f"❌ Error during desktop build: {e}", file=sys.stderr)
        sys.exit(1)
