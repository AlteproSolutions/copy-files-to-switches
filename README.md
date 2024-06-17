# Copy files to switches

A script for copying files to multiple switches effortlessly.

## How to Use

1. **Navigate to the repository:**

    ```bash
    cd path_to_repo/copy-files-to-switches/
    ```

2. **Create a Python virtual environment:**

    ```bash
    python3 -m venv .venv
    ```

3. **Activate the virtual environment:**

    Linux:

    ```bash
    source .venv/bin/activate
    ```

    Windows:

    ```powershell
    .venv/bin/activate
    ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Prepare files:**
   - Copy all files you want to transfer to the `/files_to_copy` directory in this repository.

6. **Configure SSH credentials:**
   - Fill in the `config.yaml` file with your SSH credentials.

7. **Run the script:**
   - You can either click "play" in VSCode or execute the script with:

    ```bash
    python3 mass-copy.py
    ```
