import subprocess
import argparse
import yaml
from pathlib import Path

def run_command(cmd, working_dir=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=working_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"COLMAP command failed with return code {result.returncode}")
    
    print("Command completed successfully")
    return result

def train_frame(frame_path, output_path, postshot_cli_path, config):
    print(f"\n=== Processing frame: {frame_path.name} ===")
    
    postshot_train_cmd = [
        f"\"{postshot_cli_path}\postshot_cli.exe\"",
        "train",
        "-i", f"\"{frame_path}\"",
        "-p", config['profile']
    ]

    if config['profile'] == "Splat3" or config['profile'] == "Splat MCMC":
        postshot_train_cmd.extend(["--max-num-splats", str(config['maxNumSplats'])])

    postshot_train_cmd.extend([
        "-s", str(config['iterations']),
        "--anti-aliasing", str(config['antiAliasing']),
        "--export-splat-ply", f"\"{output_path / frame_path.name}.ply\"",
    ])

    run_command(postshot_train_cmd)


def main():
    parser = argparse.ArgumentParser(description="Batch train postshot frames")
    parser.add_argument("project_path", help="Path to the project folder containing all frames")
    parser.add_argument("-o", help="Path to output frames")
    parser.add_argument("--postshot_cli", default="C:\\Program Files\\Jawset Postshot\\bin", help="Path to postshot_cli.exe")
    
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    output_path = Path(args.o)
    postshot_cli_path = Path(args.postshot_cli)
    config_path = project_path / "_config.yaml"
    
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
    
    print(f"Found {len(frame_folders)} frame folders:")
    for frame in frame_folders:
        print(f"  - {frame.name}")

    print(f"Profile: {config['profile']}, Iterations: {config['iterations']}, Max Splats: {config['maxNumSplats']}, Anti-Aliasing: {config['antiAliasing']}")

    for frame_folder in frame_folders:
        try:
            train_frame(frame_folder, output_path, postshot_cli_path, config)
        except Exception as e:
            print(f"Error processing frame {frame_folder.name}: {e}")
            continue

    print("\n=== All frames processed successfully! ===")

if __name__ == "__main__":
    main()
