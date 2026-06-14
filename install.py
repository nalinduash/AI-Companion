#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import urllib.request
import zipfile
import tarfile
import json
import re
import argparse

LLAMA_CPP_RELEASE_VERSION = "b9581"
LLAMA_CPP_URLS = {
    'darwin': {
        'arm64': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-macos-arm64.tar.gz',
        'x64': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-macos-x64.tar.gz'
    },
    'windows': {
        'cuda': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-win-cuda-12.4-x64.zip',
        'vulkan': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-win-vulkan-x64.zip',
        'cpu': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-win-cpu-x64.zip',
        'arm64': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-win-cpu-arm64.zip'
    },
    'linux': {
        # There no binary for CUDA in official Llama-cpp. So we use Prism fork
        'cuda': 'https://github.com/PrismML-Eng/llama.cpp/releases/download/prism-b8846-d104cf1/llama-prism-b8846-d104cf1-bin-linux-cuda-12.8-x64.tar.gz',
        # Ubuntu versions support other distros as well
        'vulkan': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-ubuntu-vulkan-x64.tar.gz',
        'vulkan_arm64': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-ubuntu-vulkan-arm64.tar.gz',
        'cpu': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-ubuntu-x64.tar.gz',
        'arm64': f'https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_CPP_RELEASE_VERSION}/llama-{LLAMA_CPP_RELEASE_VERSION}-bin-ubuntu-arm64.tar.gz'
    }
}

METADATA_FILE = ".install_metadata.json"

MODELS_REGISTRY = [
    {
        "id": "bonsai-llm",
        "name": "Bonsai-8B LLM Model",
        "url": "https://huggingface.co/prism-ml/Bonsai-8B-gguf/resolve/main/Bonsai-8B-Q1_0.gguf",
        "dest_dir": "llm",
        "exist_file": "Bonsai-8B-Q1_0.gguf",
        "extract": False
    },
    {
        "id": "kokoro-tts",
        "name": "Kokoro TTS Model",
        "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2",
        "dest_dir": os.path.join("backend", "models", "tts"),
        "exist_file": "model.onnx",
        "extract": True
    },
    {
        "id": "parakeet-stt",
        "name": "Parakeet STT Model",
        "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8.tar.bz2",
        "dest_dir": os.path.join("backend", "models", "stt"),
        "exist_file": "model.int8.onnx",
        "extract": True
    }
]

def load_metadata(script_dir):
    metadata_path = os.path.join(script_dir, METADATA_FILE)
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load metadata file: {e}")
    return {"models": {}}

def save_metadata(script_dir, metadata):
    metadata_path = os.path.join(script_dir, METADATA_FILE)
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save metadata file: {e}")

def update_codebase(script_dir):
    git_dir = os.path.join(script_dir, ".git")
    if not os.path.exists(git_dir):
        return

    print("\n--- Checking for Codebase Updates (git pull) ---")
    git_bin = shutil.which("git")
    if not git_bin:
        print("git command not found. Skipping auto-update of code.")
        return

    try:
        # Check current HEAD commit hash
        old_commit = subprocess.run(
            [git_bin, "rev-parse", "HEAD"],
            cwd=script_dir,
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        # Run git pull
        print("Running git pull...")
        result = subprocess.run([git_bin, "pull"], cwd=script_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: git pull failed:\n{result.stderr}")
            return

        new_commit = subprocess.run(
            [git_bin, "rev-parse", "HEAD"],
            cwd=script_dir,
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        if old_commit != new_commit:
            print("Codebase updated successfully.")
            # Check if this script (install.py) itself was modified
            diff_res = subprocess.run(
                [git_bin, "diff", "--name-only", old_commit, new_commit],
                cwd=script_dir,
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = diff_res.stdout.splitlines()
            if "install.py" in changed_files:
                print("install.py was updated. Restarting script to apply new installation logic...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Codebase is already up to date.")
    except Exception as e:
        print(f"Warning: An error occurred during git pull: {e}")


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

def get_download_url(sys_info):
    os_name = sys_info['os']
    arch = sys_info['arch']
    use_cuda = sys_info['use_cuda']
    use_vulkan = sys_info.get('use_vulkan', False)

    if os_name == 'darwin':
        if arch == 'arm64':
            return LLAMA_CPP_URLS['darwin']['arm64']
        else:
            return LLAMA_CPP_URLS['darwin']['x64']
    elif os_name == 'windows':
        if use_cuda and arch == 'x64':
            return LLAMA_CPP_URLS['windows']['cuda']
        elif use_vulkan and arch == 'x64':
            return LLAMA_CPP_URLS['windows']['vulkan']
        elif arch == 'arm64':
            return LLAMA_CPP_URLS['windows']['arm64']
        else:
            return LLAMA_CPP_URLS['windows']['cpu']
    elif os_name == 'linux':
        if use_cuda and arch == 'x64':
            return LLAMA_CPP_URLS['linux']['cuda']
        elif use_vulkan:
            if arch == 'arm64':
                return LLAMA_CPP_URLS['linux']['vulkan_arm64']
            else:
                return LLAMA_CPP_URLS['linux']['vulkan']
        elif arch == 'arm64':
            return LLAMA_CPP_URLS['linux']['arm64']
        else:
            return LLAMA_CPP_URLS['linux']['cpu']

    raise ValueError(f"Unsupported system configuration: OS={os_name}, Arch={arch}")

def get_uv_path():
    uv_bin = shutil.which('uv')
    if uv_bin:
        return uv_bin

    home = os.path.expanduser("~")
    if platform.system().lower() == 'windows':
        default_paths = [
            os.path.join(os.environ.get('USERPROFILE', home), '.local', 'bin', 'uv.exe'),
            os.path.join(os.environ.get('APPDATA', ''), 'uv', 'uv.exe'),
        ]
    else:
        default_paths = [
            os.path.join(home, '.local', 'bin', 'uv'),
            os.path.join(home, '.cargo', 'bin', 'uv'),
        ]

    for p in default_paths:
        if os.path.exists(p) and os.path.isfile(p):
            return p

    return None

def install_uv():
    uv_path = get_uv_path()
    if uv_path:
        print(f"UV is already installed at: {uv_path}")
        return True

    print("UV package manager not found. Installing UV...")
    os_name = platform.system().lower()
    try:
        if os_name in ('linux', 'darwin'):
            cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
            subprocess.run(cmd, shell=True, check=True)
        elif os_name == 'windows':
            # Official install command
            cmd = 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' 
            subprocess.run(cmd, shell=True, check=True)
        else:
            print(f"Cannot auto-install UV on unsupported OS: {os_name}")
            return False
    except Exception as e:
        print(f"Error executing UV installation command: {e}")
        return False

    uv_path = get_uv_path()
    if uv_path:
        print(f"Successfully installed UV at: {uv_path}")
        # Add the parent directory containing uv to PATH temporarily
        uv_dir = os.path.dirname(uv_path)
        if uv_dir not in os.environ["PATH"]:
            os.environ["PATH"] = uv_dir + os.pathsep + os.environ["PATH"]
        return True
    else:
        print("UV installation finished, but executable not found in default paths.")
        print("Please restart your shell or add UV to PATH manually.")
        return False

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    def report_hook(block_num, block_size, total_size):
        read_so_far = block_num * block_size
        if total_size > 0:
            percent = min(100, read_so_far * 100 // total_size)
            sys.stdout.write(f"\rProgress: {percent}% ({read_so_far // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
        else:
            sys.stdout.write(f"\rProgress: {read_so_far // (1024*1024)}MB downloaded")
        sys.stdout.flush()

    try:
        # User-agent header to avoid getting blocked by HuggingFace/Github
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            total_size = int(response.info().get('Content-Length', -1))
            block_size = 8192
            block_num = 0
            while True:
                block = response.read(block_size)
                if not block:
                    break
                out_file.write(block)
                block_num += 1
                report_hook(block_num, block_size, total_size)
        print("\nDownload complete.")
    except Exception as e:
        print(f"\nError downloading {url}: {e}")
        raise

def extract_and_flatten(archive_path, dest_dir):
    tmp_dir = os.path.join(dest_dir, "tmp_extract")
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"Extracting {archive_path}...")
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
    elif archive_path.endswith(".tar.gz") or archive_path.endswith(".tgz"):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(tmp_dir)
    elif archive_path.endswith(".tar.bz2") or archive_path.endswith(".tbz2") or archive_path.endswith(".bz2"):
        with tarfile.open(archive_path, 'r:bz2') as tar_ref:
            tar_ref.extractall(tmp_dir)
    else:
        raise ValueError(f"Unknown archive format: {archive_path}")

    # Locate source files (flat or single subfolder nested)
    items = os.listdir(tmp_dir)
    source_dir = tmp_dir
    if len(items) == 1 and os.path.isdir(os.path.join(tmp_dir, items[0])):
        source_dir = os.path.join(tmp_dir, items[0])

    # Move items to dest_dir
    for item in os.listdir(source_dir):
        src_item = os.path.join(source_dir, item)
        dst_item = os.path.join(dest_dir, item)
        if os.path.exists(dst_item):
            if os.path.isdir(dst_item):
                shutil.rmtree(dst_item)
            else:
                os.remove(dst_item)
        shutil.move(src_item, dst_item)

    shutil.rmtree(tmp_dir)

    # Set executable permissions on Linux/macOS
    if platform.system().lower() in ('linux', 'darwin'):
        for item in os.listdir(dest_dir):
            item_path = os.path.join(dest_dir, item)
            if os.path.isfile(item_path) and (item.startswith("llama-") or "." not in item):
                try:
                    os.chmod(item_path, 0o755)
                    print(f"Set executable permission on {item}")
                except Exception as e:
                    print(f"Warning: Could not set executable permission on {item}: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Parse command line arguments
    parser = argparse.ArgumentParser(description="Install and update AI Companion dependencies and models.")
    parser.add_argument("-f", "--force", action="store_true", help="Force re-download of all models and binaries.")
    args = parser.parse_args()

    # 2. Check for codebase updates
    update_codebase(script_dir)

    # Load metadata tracker
    metadata = load_metadata(script_dir)

    # 3. Detect OS and Graphics card
    print("\n--- 1) Detecting OS and Graphics Card ---")
    sys_info = detect_system()
    print(f"Operating System: {sys_info['os'].capitalize()}")
    print(f"Architecture:     {sys_info['arch']}")
    print(f"Graphics Card:    {sys_info['gpu']}")
    print(f"Hardware Mode:    {'CUDA (GPU acceleration enabled)' if sys_info['use_cuda'] else 'Vulkan (GPU acceleration enabled)' if sys_info['use_vulkan'] else 'CPU only / Metal'}")

    # 4. Install UV Package manager
    print("\n--- 2) Installing/Verifying UV Package Manager ---")
    if not install_uv():
        print("Failed to setup UV package manager.")
        sys.exit(1)

    uv_path = get_uv_path() 
    if not uv_path:
        print("Error: uv executable not found after install.")
        sys.exit(1)

    # 5. Sync backend dependencies
    print("\n--- 3) Syncing Backend Dependencies ---")
    backend_dir = os.path.join(script_dir, 'backend')
    if not os.path.exists(backend_dir):
        print(f"Error: backend folder not found at {backend_dir}")
        sys.exit(1)
    
    use_cuda = sys_info['use_cuda']
    if use_cuda:
        source_toml = os.path.join(backend_dir, 'pyproject-cuda.toml')
        print("CUDA support detected. Preparing pyproject-cuda.toml...")
    else:
        source_toml = os.path.join(backend_dir, 'pyproject-cpu.toml')
        print("No CUDA support detected (CPU/Vulkan/macOS). Preparing pyproject-cpu.toml...")

    dest_toml = os.path.join(backend_dir, 'pyproject.toml')
    if not os.path.exists(source_toml):
        print(f"Error: Source TOML file not found at {source_toml}")
        sys.exit(1)

    try:
        shutil.copy2(source_toml, dest_toml)
        print(f"Successfully copied {os.path.basename(source_toml)} to {os.path.basename(dest_toml)}")
    except Exception as e:
        print(f"Error preparing pyproject.toml: {e}")
        sys.exit(1)

    try:
        print(f"Running '{uv_path} sync' in backend...")
        subprocess.run([uv_path, 'sync'], cwd=backend_dir, check=True)
    except Exception as e:
        print(f"Error syncing backend: {e}")
        sys.exit(1)

    # 6. Setting up Models and Binaries
    print("\n--- 4) Setting up Models and Binaries ---")
    
    # Resolve system-specific llama-cpp URL and executable
    llama_url = get_download_url(sys_info)
    llama_exe = "llama-server.exe" if sys_info['os'] == 'windows' else "llama-server"

    # Unified installation checklist
    installation_list = [
        {
            "id": "llama-cpp",
            "name": f"Llama-cpp Binaries (version {LLAMA_CPP_RELEASE_VERSION})",
            "url": llama_url,
            "dest_dir": "llm",
            "exist_file": llama_exe,
            "extract": True
        }
    ] + MODELS_REGISTRY

    # Process each item in the registry
    for item in installation_list:
        abs_dest_dir = os.path.join(script_dir, item['dest_dir'])
        abs_exist_file = os.path.join(abs_dest_dir, item['exist_file'])

        item_id = item['id']
        current_url = item['url']
        installed_url = metadata.get("models", {}).get(item_id, "")

        # Determine download trigger conditions:
        # 1. File doesn't exist
        # 2. File exists, but metadata URL is present AND it differs (an update was requested via code URL change)
        # 3. User requested a force update
        file_exists = os.path.exists(abs_exist_file)
        should_download = not file_exists or (installed_url and installed_url != current_url) or args.force

        if should_download:
            print(f"Downloading/updating {item['name']}...")
            os.makedirs(abs_dest_dir, exist_ok=True)

            if item['extract']:
                # Deduce extension based on URL
                if current_url.endswith(".zip"):
                    archive_ext = ".zip"
                elif current_url.endswith(".tar.gz") or current_url.endswith(".tgz"):
                    archive_ext = ".tar.gz"
                elif current_url.endswith(".tar.bz2") or current_url.endswith(".tbz2") or current_url.endswith(".bz2"):
                    archive_ext = ".tar.bz2"
                else:
                    archive_ext = ".archive"
                download_dest = os.path.join(abs_dest_dir, f"temp_{item_id}{archive_ext}")
            else:
                download_dest = abs_exist_file

            try:
                download_file(current_url, download_dest)
                if item['extract']:
                    extract_and_flatten(download_dest, abs_dest_dir)
                    if os.path.exists(download_dest):
                        os.remove(download_dest)
                
                # Save status in metadata
                if "models" not in metadata:
                    metadata["models"] = {}
                metadata["models"][item_id] = current_url
                save_metadata(script_dir, metadata)
                print(f"Successfully set up {item['name']}.")
            except Exception as e:
                print(f"Error setting up {item['name']}: {e}")
                sys.exit(1)
        else:
            print(f"-> {item['name']} is already up to date.")

    # 7. Frontend Dependencies npm install
    print("\n--- 5) Installing Frontend Dependencies ---")
    frontend_dir = os.path.join(script_dir, 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"Error: frontend folder not found at {frontend_dir}")
        sys.exit(1)

    try:
        print("Running 'npm install' in frontend...")
        if sys_info['os'] == 'windows':
            subprocess.run('npm install', cwd=frontend_dir, shell=True, check=True)
        else:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print("Frontend dependencies installed successfully.")
    except Exception as e:
        print(f"Error running npm install: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("Installation completed successfully!")
    print("To run the application, use: python run.py")
    print("==================================================")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation aborted by user.")
        sys.exit(1)

# Model Update Check Mechanism:
# 1. All installable assets (models, binaries) are defined in MODELS_REGISTRY or dynamically resolved at runtime.
# 2. The script maintains '.install_metadata.json' mapping each asset ID to its downloaded source URL.
# 3. For each asset, the script checks:
#    - If its target 'exist_file' is missing locally.
#    - If the URL in the metadata file differs from the current registry URL (indicating a model update/change).
#    - If the user explicitly passed the '--force' flag to force a re-download.
# 4. If any condition is met, the asset is downloaded, extracted (if required), and the metadata file is updated.
# 5. This allows automatic, transparent updates when code URLs change, without re-downloading unchanged files.


