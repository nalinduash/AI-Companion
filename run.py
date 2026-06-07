import asyncio
import sys
import signal
import os

# Force Python subprocesses to output logs of the services
os.environ["PYTHONUNBUFFERED"] = "1"

# Define the services to run with their command and working directory
SERVICES = {
    "Frontend": {
        "command": "npm run dev",
        "cwd": "frontend"
    },
    "Backend": {
        "command": "uv run main.py",
        "cwd": "backend"
    },
    "LLM": {
        "command": "./llama-server -m ./Bonsai-8B-Q1_0.gguf -ngl 99 -c 2048 --port 8081 --host 0.0.0.0 --log-disable",
        "cwd": "llm"
    }
}

def setup_cuda_paths():
    """Locates CUDA/cuDNN library directories in backend/.venv and injects them into LD_LIBRARY_PATH."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_lib = os.path.join(script_dir, "backend", ".venv", "lib")

    if not os.path.exists(venv_lib):
        print(f"[System] Warning: {venv_lib} not found. Skipping CUDA path injection.")
        return

    # Handle different Python directory names dynamically (e.g., python3.10, python3.12)
    py_dirs = [d for d in os.listdir(venv_lib) if d.startswith("python")]
    if not py_dirs:
        return

    site_packages = os.path.join(venv_lib, py_dirs[0], "site-packages")
    nvidia_base = os.path.join(site_packages, "nvidia")

    if not os.path.exists(nvidia_base):
        print(f"[System] Warning: {nvidia_base} not found in site-packages.")
        return

    # Dynamically find any folder under 'nvidia' that has a 'lib' directory
    nvidia_paths = []
    for folder in os.listdir(nvidia_base):
        lib_path = os.path.join(nvidia_base, folder, "lib")
        if os.path.exists(lib_path):
            nvidia_paths.append(lib_path)

    if nvidia_paths:
        existing_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
        # Add only new paths that aren't already declared
        paths_to_add = [p for p in nvidia_paths if p not in existing_ld_path]
        if paths_to_add:
            new_ld_path = ":".join(paths_to_add)
            if existing_ld_path:
                os.environ["LD_LIBRARY_PATH"] = f"{new_ld_path}:{existing_ld_path}"
            else:
                os.environ["LD_LIBRARY_PATH"] = new_ld_path
            
            print("[System] Injected CUDA paths into LD_LIBRARY_PATH:")
            for path in paths_to_add:
                print(f"  -> {path}")

async def read_stream(stream, prefix):
    """Reads a stream line by line and prints it with a clean prefix."""
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode('utf-8', errors='replace').rstrip()
            print(f"[{prefix}] {decoded}")
    except asyncio.CancelledError:
        pass

async def run_service(name, config):
    """Starts a process in its respective working directory and manages its lifecycle."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.path.join(script_dir, config["cwd"])
    command = config["command"]

    print(f"[System] Starting {name} in {cwd}...")
    
    try:
        # Start the subprocess with the updated environment and correct directory context
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
            env=os.environ  # Subprocess inherits the injected LD_LIBRARY_PATH and PYTHONUNBUFFERED
        )
    except Exception as e:
        print(f"[System] Failed to start {name}: {e}")
        return
    
    try:
        log_task = asyncio.create_task(read_stream(process.stdout, name))
        await process.wait()
        await log_task
    except asyncio.CancelledError:
        print(f"[System] Stopping {name}...")
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            print(f"[System] {name} did not stop gracefully. Force killing...")
            process.kill()
        except Exception:
            pass

async def main():
    # 1. Setup GPU libraries
    setup_cuda_paths()

    # 2. Spawn concurrent services
    tasks = []
    for name, config in SERVICES.items():
        tasks.append(asyncio.create_task(run_service(name, config)))
    
    loop = asyncio.get_running_loop()
    
    def stop_all():
        print("\n[System] Shutting down all services...")
        for task in tasks:
            task.cancel()

    # Register OS signals for a clean shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_all)
        except NotImplementedError:
            pass

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt:
        stop_all()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass