## Demo

[![Watch the Demo Video](https://youtube.com)](https://www.youtube.com/watch?v=6-9_RBeHZwA)

## Notice: This is working for Linux/Windows and MacOS. This support both CUDA cards(RTX family) and Non-CUDA cards(via vulkan).

## Notice: Even 4GB graphics card can get response time less than 1 second.

## Notice (Only for Windows users): You may have to disable `Smart App Control` as it blocks UV package manager.

## 🚀 How to Run

1. **Install Python, Git**

2. **Clone Repo**

   ```bash
   git clone https://github.com/nalinduash/AI-Companion.git
   ```

3. **Install dependencies**

   ```python
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
- This is tested only on `Linux(Fedora 44)` and `Windows 11` yet.
- I found that this works best with `Google Chrome browser`. Firefox seems to pickup it's own voice and do a feedback loop.
