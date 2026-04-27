import os
import tarfile
import urllib.request
import shutil

class ModelDownloaderService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelDownloaderService, cls).__new__(cls)
        return cls._instance

    def ensure_models(self):
        self._download_and_extract(
            url="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8.tar.bz2",
            directory="models/stt",
            condition_file="sherpa-onnx-nemo-parakeet_tdt_ctc_110m-en-36000-int8/model.int8.onnx"
        )
        self._download_and_extract(
            url="https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2",
            directory="models/tts",
            condition_file="kokoro-en-v0_19/model.onnx"
        )

    def _download_and_extract(self, url: str, directory: str, condition_file: str, force: bool = False):
        """
        Downloads and extracts a model if it doesn't exist.
        """
        os.makedirs(directory, exist_ok=True)
        condition_path = os.path.join(directory, condition_file)
        archive_name = url.split("/")[-1]
        archive_path = os.path.join(directory, archive_name)

        if force:
            print(f"Downloaded Service: Cleaning {directory}")
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

        # Flow:
        # 1. If condition file found, do nothing.
        if os.path.exists(condition_path):
            print("Downloaded Service: Model already exists.")
            return

        # 2. If compressed archive found, extract it.
        # 3. If both not found, download and extract.
        if not os.path.exists(archive_path):
            print(f"Downloaded Service: Downloading to {archive_path}...")
            urllib.request.urlretrieve(url, archive_path)
            print("Downloaded Service: Download complete.")

        print(f"Downloaded Service: Extracting {archive_path}...")
        with tarfile.open(archive_path) as tar:
            tar.extractall(path=directory)
        print("Downloaded Service: Extraction complete.")
