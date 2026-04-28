import os
import sys

def setup_cuda_paths():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_lib = os.path.join(script_dir, ".venv", "lib")

    if os.path.exists(venv_lib):
        py_dirs = [d for d in os.listdir(venv_lib) if d.startswith("python")]
        if py_dirs:
            site_packages = os.path.join(venv_lib, py_dirs[0], "site-packages")

            nvidia_paths = [
                os.path.join(site_packages, "nvidia", "cublas", "lib"),
                os.path.join(site_packages, "nvidia", "cudnn", "lib"),
                os.path.join(site_packages, "nvidia", "cuda_runtime", "lib"),
                os.path.join(site_packages, "nvidia", "cuda_nvrtc", "lib"),
            ]

            existing_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
            new_paths = [p for p in nvidia_paths if os.path.exists(p)]

            if new_paths:
                missing_paths = [p for p in new_paths if p not in existing_ld_path]
                if missing_paths:
                    os.environ["LD_LIBRARY_PATH"] = ":".join(
                        missing_paths + ([existing_ld_path] if existing_ld_path else [])
                    )
                    os.execv(sys.executable, [sys.executable] + sys.argv)