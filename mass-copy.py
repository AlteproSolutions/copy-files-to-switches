import asyncio
import asyncssh
import os, shutil
import yaml
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm



def load_file(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, filename), mode="r") as file:

        loaded_file = file.readlines()

        return [line.strip() for line in loaded_file]

def load_config(config_path="config.yaml"):
    # Load configuration from a YAML file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    config_file = os.path.join(script_dir, config_path)
    template_file = os.path.join(script_dir, f"{script_dir}" + "config_template.yaml")

    # Check if config.yaml exists
    if not os.path.exists(config_file):
        # If not, copy config_template.yaml to create config.yaml
        shutil.copy(template_file, config_file)
    
    with open(os.path.join(script_dir, config_path), "r") as f:
        return yaml.safe_load(f)


async def copy_file_to_switch(switch_ip, username, password, local_file_path, remote_file_path, errors):
    try:
        async with asyncssh.connect(switch_ip, username=username, password=password, known_hosts=None) as conn:
            async with conn.start_sftp_client() as sftp:
                file_size = os.path.getsize(local_file_path)
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=f'{switch_ip}:{os.path.basename(local_file_path)}') as progress:
                    async with sftp.open(remote_file_path, 'wb') as remote_file:
                        with open(local_file_path, 'rb') as local_file:
                            while True:
                                data = local_file.read(32768)
                                if not data:
                                    break
                                await remote_file.write(data)
                                progress.update(len(data))
        print(f"Successfully copied {local_file_path} to {switch_ip}:{remote_file_path}")
    except (OSError, asyncssh.Error) as e:
        print(f"Failed to copy file to {switch_ip}: {e}")
        errors.append((switch_ip, local_file_path, str(e)))

async def copy_files_to_switches(switch_ips, username, password, files_directory, remote_directory):
    # Get a list of files in the specified directory
    files_to_copy = [os.path.join(files_directory, file) for file in os.listdir(files_directory) if os.path.isfile(os.path.join(files_directory, file))]
    
    if not files_to_copy:
        print(f"No files found in the directory {files_directory}.")
        return

    # List to store errors
    errors = []

    # Create a list of tasks
    tasks = []
    for switch_ip in switch_ips:
        for local_file_path in files_to_copy:
            remote_file_path = os.path.join(remote_directory, os.path.basename(local_file_path))
            tasks.append(copy_file_to_switch(switch_ip, username, password, local_file_path, remote_file_path, errors))
    
    # Run the tasks concurrently
    await asyncio.gather(*tasks)

    # Check for errors
    if errors:
        print("------------------------------------------------------------------------------------------------")
        print("Some errors occurred during the file copying process:")
        for error in errors:
            print(f" - Failed to copy {error[1]} to {error[0]}: {error[2]}")
    else:
        print("------------------------------------------------------------------------------------------------")
        print("All files copied to all hosts successfully.")

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    config = load_config()
    # List of switch IP addresses
    switch_ips = load_file(f"{script_dir}/hosts.txt")
    print(switch_ips)
    
    # Authentication details
    username = config['SSH_USERNAME']
    password = config['SSH_PASSWORD']
    
    # Directories
    files_directory = f"{script_dir}/files_to_copy/"
    remote_directory = '/'

    await copy_files_to_switches(switch_ips, username, password, files_directory, remote_directory)

if __name__ == "__main__":
    asyncio.run(main())