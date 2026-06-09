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


LLM_MODEL_URL = "https://huggingface.co/prism-ml/Bonsai-8B-gguf/resolve/main/Bonsai-8B-Q1_0.gguf"
KOKORO_TTS_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2"
PARAKEET_STT_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8.tar.bz2"

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

    # 1. Detect OS and Graphics card
    print("--- 1) Detecting OS and Graphics Card ---")
    sys_info = detect_system()
    print(f"Operating System: {sys_info['os'].capitalize()}")
    print(f"Architecture:     {sys_info['arch']}")
    print(f"Graphics Card:    {sys_info['gpu']}")
    print(f"Hardware Mode:    {'CUDA (GPU acceleration enabled)' if sys_info['use_cuda'] else 'Vulkan (GPU acceleration enabled)' if sys_info['use_vulkan'] else 'CPU only / Metal'}")

    # 2. Install UV Package manager
    print("\n--- 2) Installing/Verifying UV Package Manager ---")
    if not install_uv():
        print("Failed to setup UV package manager.")
        sys.exit(1)

    uv_path = get_uv_path() 
    if not uv_path:
        print("Error: uv executable not found after install.")
        sys.exit(1)

    # 3. Backend Dependencies uv sync
    print("\n--- 3) Syncing Backend Dependencies ---")
    backend_dir = os.path.join(script_dir, 'backend')
    if not os.path.exists(backend_dir):
        print(f"Error: backend folder not found at {backend_dir}")
        sys.exit(1)
    
    try:
        print(f"Running '{uv_path} sync' in backend...")
        subprocess.run([uv_path, 'sync'], cwd=backend_dir, check=True)
    except Exception as e:
        print(f"Error syncing backend: {e}")
        sys.exit(1)

    # 4. Setup LLM
    print("\n--- 4) Setting up LLM ---")
    llm_dir = os.path.join(script_dir, 'llm')
    os.makedirs(llm_dir, exist_ok=True)

    # 4.1 & 4.2: Download Llama-cpp and extract to llm/
    download_url = get_download_url(sys_info)
    archive_ext = ".zip" if download_url.endswith(".zip") else ".tar.gz"
    archive_path = os.path.join(llm_dir, f"llama-cpp-bin{archive_ext}")

    exe_name = "llama-server.exe" if sys_info['os'] == 'windows' else "llama-server"
    if os.path.exists(os.path.join(llm_dir, exe_name)):
        print("llama-cpp executable already exists in llm/. Skipping download.")
    else:
        try:
            download_file(download_url, archive_path)
            extract_and_flatten(archive_path, llm_dir)
            if os.path.exists(archive_path):
                os.remove(archive_path)
            print("llama-cpp binaries set up successfully.")
        except Exception as e:
            print(f"Failed to set up llama-cpp: {e}")
            sys.exit(1)

    # 4.3: Download Bonsai-8B model
    model_path = os.path.join(llm_dir, "Bonsai-8B-Q1_0.gguf")

    if os.path.exists(model_path):
        print("Bonsai-8B model already exists in llm/. Skipping download.")
    else:
        try:
            download_file(LLM_MODEL_URL, model_path)
            print("Bonsai-8B model downloaded successfully.")
        except Exception as e:
            print(f"Failed to download model: {e}")
            sys.exit(1)

    # 4.4: Setup TTS (Kokoro)
    print("\n--- 4.4) Setting up Kokoro TTS ---")
    tts_dir = os.path.join(script_dir, 'backend', 'models', 'tts')
    os.makedirs(tts_dir, exist_ok=True)
    
    if os.path.exists(os.path.join(tts_dir, "model.onnx")):
        print("Kokoro TTS model already exists in backend/models/tts/. Skipping download.")
    else:
        archive_path = os.path.join(tts_dir, "kokoro-en-v0_19.tar.bz2")
        try:
            download_file(KOKORO_TTS_URL, archive_path)
            extract_and_flatten(archive_path, tts_dir)
            if os.path.exists(archive_path):
                os.remove(archive_path)
            print("Kokoro TTS model set up successfully.")
        except Exception as e:
            print(f"Failed to set up Kokoro TTS: {e}")
            sys.exit(1)

    # 4.5: Setup STT (Parakeet)
    print("\n--- 4.5) Setting up Parakeet STT ---")
    stt_dir = os.path.join(script_dir, 'backend', 'models', 'stt')
    os.makedirs(stt_dir, exist_ok=True)

    if os.path.exists(os.path.join(stt_dir, "model.int8.onnx")):
        print("Parakeet STT model already exists in backend/models/stt/. Skipping download.")
    else:
        archive_path = os.path.join(stt_dir, "sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8.tar.bz2")
        try:
            download_file(PARAKEET_STT_URL, archive_path)
            extract_and_flatten(archive_path, stt_dir)
            if os.path.exists(archive_path):
                os.remove(archive_path)
            print("Parakeet STT model set up successfully.")
        except Exception as e:
            print(f"Failed to set up Parakeet STT: {e}")
            sys.exit(1)

    # 5. Frontend Dependencies npm install
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
