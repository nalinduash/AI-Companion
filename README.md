## Demo
https://github.com/user-attachments/assets/f9674125-8f00-4fd7-928f-ceec68499adc


## 🚀 How to Run

1. **Install UV Package Manager**
2. **Sync Backend Dependencies:**
   ```bash
   cd backend
   uv sync
   ```
3. **Download `llama.cpp` (Prism) and `Bonsai-8B`:**
   - [llama.cpp Releases](https://github.com/PrismML-Eng/llama.cpp/releases) (Choose correct version for your OS and Hardware)
   - [Bonsai-8B Model](https://huggingface.co/prism-ml/Bonsai-8B-gguf/blob/main/Bonsai-8B-Q1_0.gguf)
4. **Extract `llamacpp-prism` and move `Bonsai-8B-Q1_0.gguf` into it.**

5. **Run Program:**

   **5.1. Go to `llama-cpp` folder and run LLama-CPP server on port 8081:**

   ```bash
   ./llama-server -m ./Bonsai-8B-Q1_0.gguf -ngl 99 -c 2048 --port 8081 --host 0.0.0.0 --log-disable
   ```

   **5.2. Run Backend:**

   ```bash
   cd backend
   uv run main.py
   ```

   **5.3. Run Frontend:**

   ```bash
   cd frontend
   npm run dev
   ```

6. **Open it in web browser:**
   - [http://localhost:5173](http://localhost:5173)


Note:

- This may take several minutes to run for the first time due to downloading the model.
- This is tested only on linux(Nobara 43) yet.
- You may need to change here-and-there if you are running this on a different OS.
- I found that this works best with chrome browser. Firefox seems to pickup it's own voice and do a feedback loop.
