#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import json
import re
import asyncio
import signal

# Force Python subprocesses to output logs of the services
os.environ["PYTHONUNBUFFERED"] = "1"

# Detect OS, Architecture, GPU info, CUDA/Vulkan info
def detect_system():
    os_name = platform.system().lower()
    arch = platform.machine().lower()
    if arch in ('amd64', 'x86_64'):
        arch_clean = 'x64'
    elif arch in ('arm64', 'aarch64'):
        arch_clean = 'arm64'
    else:
        arch_clean = arch

    gpu_name = "CPU only"
    use_cuda = False
    use_vulkan = False
    cuda_version = None

    # Get nvidia-smi path
    nvidia_smi_path = shutil.which('nvidia-smi')
    if not nvidia_smi_path and os_name == 'windows':
        win_path = r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        if os.path.exists(win_path):
            nvidia_smi_path = win_path

    if nvidia_smi_path:
        try:
            # Get Name
            res_name = subprocess.run(
                [nvidia_smi_path, '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True, text=True, check=True
            )
            gpu_name = res_name.stdout.strip().split('\n')[0]

            # Get CUDA Version from full nvidia-smi output
            res_full = subprocess.run([nvidia_smi_path], capture_output=True, text=True, check=True)
            match = re.search(r"CUDA Version:\s*([\d.]+)", res_full.stdout)
            if match:
                cuda_version = float(match.group(1))
            
            # Nvidia (cuda 12+ supported) -> CUDA variation
            # Nvidia other -> Vulkan variation
            if cuda_version and cuda_version >= 12.0:
                use_cuda = True
            else:
                use_vulkan = True
        except Exception:
            pass

    # Linux AMD/Intel/Nvidia detection via lspci
    if os_name == 'linux' and not use_cuda and not use_vulkan:
        lspci_path = shutil.which('lspci')
        if lspci_path:
            try:
                res = subprocess.run([lspci_path], capture_output=True, text=True, check=True)
                gpus = []
                for line in res.stdout.splitlines():
                    if any(k in line.lower() for k in ('vga', '3d', 'display')):
                        gpus.append(line)
                
                # Check for Nvidia (if nvidia-smi failed ealier)
                found_gpu = False
                for g in gpus:
                    g_lower = g.lower()
                    if 'nvidia' in g_lower:
                        gpu_name = g.split(':')[-1].strip()
                        # If nvidia-smi isn't working/installed, fallback to Vulkan for safety
                        use_vulkan = True
                        found_gpu = True
                        break
                
                if not found_gpu:
                    # Check for AMD or Intel
                    for g in gpus:
                        g_lower = g.lower()
                        if 'amd' in g_lower or 'radeon' in g_lower or 'intel' in g_lower or 'arc' in g_lower:
                            gpu_name = g.split(':')[-1].strip()
                            use_vulkan = True
                            found_gpu = True
                            break
            except Exception:
                pass

    # Windows fallback: check using PowerShell (if not already handled by nvidia-smi)
    if os_name == 'windows' and not use_cuda and not use_vulkan:
        try:
            cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_VideoController | Select-Object Name | ConvertTo-Json"'
            res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                if not isinstance(data, list):
                    data = [data]
                gpus = []
                for gpu in data:
                    name = gpu.get('Name', '')
                    if not name:
                        continue
                    gpus.append(name)
                
                # Check for Nvidia first
                found_gpu = False
                for name in gpus:
                    n_lower = name.lower()
                    if 'nvidia' in n_lower:
                        gpu_name = name
                        # If nvidia-smi isn't working/installed, fallback to Vulkan for safety
                        use_vulkan = True
                        found_gpu = True
                        break
                
                if not found_gpu:
                    # Check for AMD or Intel
                    for name in gpus:
                        n_lower = name.lower()
                        if 'amd' in n_lower or 'radeon' in n_lower or 'intel' in n_lower or 'arc' in n_lower:
                            gpu_name = name
                            use_vulkan = True
                            found_gpu = True
                            break
        except Exception:
            pass

    return {
        'os': os_name,
        'arch': arch_clean,
        'gpu': gpu_name,
        'use_cuda': use_cuda,
        'use_vulkan': use_vulkan,
        'cuda_version': cuda_version
    }

def setup_cuda_paths():
    """Locates CUDA/cuDNN library directories in backend/.venv and injects them into environment variables."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os_name = platform.system().lower()
    
    venv_dir = os.path.join(script_dir, "backend", ".venv")

    site_packages = None
    if os_name == 'windows':
        site_packages = os.path.join(venv_dir, "Lib", "site-packages")
    else:
        # On Linux/macOS, site-packages is typically in .venv/lib/python3.X/site-packages
        venv_lib = os.path.join(venv_dir, "lib")
        if os.path.exists(venv_lib):
            py_dirs = [d for d in os.listdir(venv_lib) if d.startswith("python")]
            if py_dirs:
                site_packages = os.path.join(venv_lib, py_dirs[0], "site-packages")

    nvidia_base = os.path.join(site_packages, "nvidia")
    if not os.path.exists(nvidia_base):
        print(f"[System] Warning: {nvidia_base} not found. Skipping CUDA path injection.")
        return

    # Collect DLL/shared library directories
    nvidia_paths = []
    for folder in os.listdir(nvidia_base):
        folder_path = os.path.join(nvidia_base, folder)
        if not os.path.isdir(folder_path):
            continue
        
        # On Windows, DLLs are under 'bin' and/or 'lib'. On Linux/macOS, shared libraries are under 'lib'.
        sub_dir = "bin" if os_name == "windows" else "lib"
        lib_path = os.path.join(folder_path, sub_dir)
        if os.path.exists(lib_path):
            nvidia_paths.append(lib_path)

    if not nvidia_paths:
        return

    # Inject paths into the environment
    if os_name == 'windows':
        existing_path = os.environ.get("PATH", "")
        paths_to_add = [p for p in nvidia_paths if p not in existing_path]
        if paths_to_add:
            new_path = os.pathsep.join(paths_to_add)
            if existing_path:
                os.environ["PATH"] = f"{new_path}{os.pathsep}{existing_path}"
            else:
                os.environ["PATH"] = new_path
            
            # Also register them for the current python process
            for p in paths_to_add:
                try:
                    os.add_dll_directory(p)
                except Exception:
                    pass
            
            print("[System] Injected CUDA paths into PATH:")
            for path in paths_to_add:
                print(f"  -> {path}")
    else:
        existing_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
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
    # Detect system details
    try:
        sys_info = detect_system()
    except Exception as e:
        print(f"[System] Warning: Could not detect system info: {e}")
        sys.exit(1)

    # Determine LLM GPU layers offload
    # macOS (Metal), CUDA, and Vulkan support GPU offloading
    use_gpu = sys_info.get('use_cuda') or sys_info.get('use_vulkan') or (sys_info.get('os') == 'darwin')
    ngl_value = 99 if use_gpu else 0

    # Determine LLM executable (llama-server.exe for Windows, otherwise ./llama-server)
    llama_server_name = "llama-server.exe" if sys_info.get('os') == 'windows' else "./llama-server"

    # Define the services to run with their command and working directory
    services = {
        "Frontend": {
            "command": "npm run dev",
            "cwd": "frontend"
        },
        "Backend": {
            "command": "uv run --offline main.py",
            "cwd": "backend"
        },
        "LLM": {
            "command": f"{llama_server_name} -m gemma-4-E2B-it-Q4_K_M.gguf -ngl {ngl_value} -c 2048 --port 8081 --host 0.0.0.0 --log-disable",
            "cwd": "llm"
        }
    }

    # 1. Setup GPU libraries
    setup_cuda_paths()

    # 2. Spawn concurrent services
    tasks = []
    for name, config in services.items():
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
