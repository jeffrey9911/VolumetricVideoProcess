import subprocess
import argparse
import yaml
import sys
import time
from pathlib import Path

def run_command_adv(cmd, working_dir=None):
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    
    # Use Popen for real-time output with both stdout and stderr
    process = subprocess.Popen(
        cmd, 
        cwd=working_dir, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    stdout_lines = []
    stderr_lines = []
    
    # Read output in real-time
    while True:
        # Check if process is still running
        if process.poll() is not None:
            break
            
        # Read from stdout
        if process.stdout:
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(f"OUT: {stdout_line.strip()}")
                stdout_lines.append(stdout_line.strip())
                sys.stdout.flush()  # Force output to appear immediately
        
        # Read from stderr  
        if process.stderr:
            stderr_line = process.stderr.readline()
            if stderr_line:
                print(f"ERR: {stderr_line.strip()}")
                stderr_lines.append(stderr_line.strip())
                sys.stdout.flush()
                
        time.sleep(0.01)  # Small delay to prevent excessive CPU usage
    
    # Get any remaining output
    remaining_stdout, remaining_stderr = process.communicate()
    if remaining_stdout:
        for line in remaining_stdout.strip().split('\n'):
            if line:
                print(f"OUT: {line}")
                stdout_lines.append(line)
    if remaining_stderr:
        for line in remaining_stderr.strip().split('\n'):
            if line:
                print(f"ERR: {line}")
                stderr_lines.append(line)
    
    return_code = process.returncode
    print("=" * 60)
    
    if return_code != 0:
        print(f"Error: Command failed with return code {return_code}")
        raise RuntimeError(f"Command failed with return code {return_code}")
    
    print("Command completed successfully")
    
    # Create result object
    class Result:
        def __init__(self, returncode, stdout_lines, stderr_lines):
            self.returncode = returncode
            self.stdout = '\n'.join(stdout_lines)
            self.stderr = '\n'.join(stderr_lines)
    
    return Result(return_code, stdout_lines, stderr_lines)

def run_command(cmd, working_dir=None):
    print(f"Running: {' '.join(cmd)}")
#    result = subprocess.run(cmd, cwd=working_dir, capture_output=True, text=True)
    process = subprocess.Popen(
        cmd, 
        cwd=working_dir, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        text=True, 
        shell=False,
        bufsize=1,
        universal_newlines=True
    )

    stdout_lines = []
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            stdout_lines.append(output.strip())
    
    return_code = process.poll()

    if return_code != 0:
        print(f"Error: Command failed with return code {return_code}")
        raise RuntimeError(f"Command failed with return code {return_code}")
    
    
    print("Command completed successfully")
    return return_code

def train_frame(frame_path, output_path, postshot_cli_path, config):
    print(f"\n=== Processing frame: {frame_path.name} ===")
    
    postshot_train_cmd = [
        str(postshot_cli_path / "postshot-cli.exe"),
        "train",
        "-i", f"{frame_path}",
        "-p", config['profile']
    ]

    if config['profile'] == "Splat3" or config['profile'] == "Splat MCMC":
        postshot_train_cmd.extend(["--max-num-splats", str(config['maxNumSplats'])])

    postshot_train_cmd.extend([
        "-s", str(config['iterations']),
        "--anti-aliasing", str(config['antiAliasing']),
        "--export-splat-ply", str(output_path / f"{frame_path.name}.ply")
    ])

    #run_command(postshot_train_cmd, str(Path.home))
    run_command(postshot_train_cmd, str(frame_path.parent))


def main():
    parser = argparse.ArgumentParser(description="Batch train postshot frames")
    parser.add_argument("project_path", help="Path to the project folder containing all frames")
    parser.add_argument("-o", help="Path to output frames")
    parser.add_argument("--postshot_cli", default="C:\\Program Files\\Jawset Postshot\\bin", help="Path to postshot_cli.exe")
    parser.add_argument("--start_from", default=0, help="Index of the frame to start from (defult:0)")
    parser.add_argument("--count", default=0, help="Number of frames to process (default: 0, meaning all frames)")
    parser.add_argument("--reverse", action='store_true', help="Process frames in reverse order")
    parser.add_argument("--test", action='store_true', help="Test mode, only processes the first frame")
    
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    output_path = Path(args.o)
    postshot_cli_path = Path(args.postshot_cli)
    config_path = project_path / "_config.yaml"

    start_index = int(args.start_from)
    count = int(args.count)
    reverse = args.reverse
    test_mode = args.test
    
    if not project_path.exists():
        raise RuntimeError(f"Project path does not exist: {project_path}")
    
    if not output_path.exists():
        raise RuntimeError(f"Output path does not exist: {output_path}")

    if not postshot_cli_path.exists():
        raise RuntimeError(f"Postshot CLI path does not exist: {postshot_cli_path}")

    if not config_path.exists():
        raise RuntimeError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    config = {
            'profile': data['profile'],
            'iterations': int(data['iterations']),
            'maxNumSplats': int(data['maxNumSplats']),
            'antiAliasing': bool(data['antiAliasing'])
    }
    
    frame_folders = sorted([d for d in project_path.iterdir() 
                          if d.is_dir() and d.name.startswith("frame_")])
    
    if not frame_folders:
        raise RuntimeError(f"No frame folders found in {project_path}")
    
#    print(f"Found {len(frame_folders)} frame folders:")
#    for frame in frame_folders:
#        print(f"  - {frame.name}")

#    train_frame(frame_folders[0], output_path, postshot_cli_path, config)
#    for frame_folder in frame_folders:
#        try:
#            train_frame(frame_folder, output_path, postshot_cli_path, config)
#        except Exception as e:
#            print(f"Error processing frame {frame_folder.name}: {e}")
#            continue

    print("\n\n=== Starting batch processing of frames ===")
    print(f"Total frames: {len(frame_folders)}")
    print(f"Processing frames from index {start_index} with count {count} in {'reverse' if reverse else 'normal'} order")
    print(f"Splat profile: {config['profile']}")
    print(f"Iterations: {config['iterations']}")
    print(f"Max Splats: {config['maxNumSplats']}")
    print(f"Anti-Aliasing: {config['antiAliasing']}\n\n")

    # wait for any key press before starting
    input("Press Enter to start processing frames...")

    if test_mode:
        print("Test mode enabled, only processing the first frame.")
        if frame_folders:
            train_frame(frame_folders[0], output_path, postshot_cli_path, config)
        else:
            print("No frames to process in test mode.")
        
        return

    if count <= 0:
        count = len(frame_folders)
        print(f"Defult count to {count} based on available frames.")

    if reverse:
        for i in range(start_index, start_index - count - 1, -1):
            if i < 0 or i >= len(frame_folders):
                print(f"Skipping invalid index {i}")
                break
            train_frame(frame_folders[i], output_path, postshot_cli_path, config)
    
    if not reverse:
        for i in range(start_index, start_index + count):
            if i < 0 or i >= len(frame_folders):
                print(f"Skipping invalid index {i}")
                break
            train_frame(frame_folders[i], output_path, postshot_cli_path, config)

    print("\n=== All frames processed successfully! ===")

if __name__ == "__main__":
    main()
