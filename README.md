## Demo

https://github.com/user-attachments/assets/f9674125-8f00-4fd7-928f-ceec68499adc

## Notice: This is currently wrking only for Linux with CUDA supported cards(RTX family). For other operating systems and hardwares, you might need to adjust settings manually. We hope to make this cross-platform in the future.

## 🚀 How to Run

1. **Install Python, Git**

2. **Clone Repo**

   ```bash
   git clone https://github.com/nalinduash/AI-Companion.git
   ```

3. **Install dependencies**

   ```bash
   python install.py
   ```

4. **Run Program:**

   ```python
   python run.py
   ```

5. **Open it in web browser:**
   - [http://localhost:5173](http://localhost:5173)

Note:

- This may take several minutes to run for the first time due to downloading the model.
- This is tested only on linux(Fedora 44) yet.
- I found that this works best with chrome browser. Firefox seems to pickup it's own voice and do a feedback loop.
