import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog='quarto-render',
        description="Render independent Quarto documents as if they were within a Quarto project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
unrecognized arguments are passed to quarto render.
        
environment variables:
  QUARTO_RENDER_PROJECT_DIR     Path to the template Quarto project directory
  QUARTO_RENDER_OUTPUT_DIR      Relative path to the output directory of the template project
        """
    )
    
    parser.add_argument(
        '-r', '--resources',
        action='append',
        help='Path to resources (e.g., images, bibliography files) to be copied alongside the document. Can be used multiple times. Supports glob patterns.'
    )
    
    parser.add_argument(
        'document',
        help='Path to the Quarto document to render'
    )
    
    # Use parse_known_args to capture all unknown args as quarto options
    args, quarto_args = parser.parse_known_args()
    args.quarto_args = quarto_args
    
    # Get environment variables
    project_dir_str = os.environ.get('QUARTO_RENDER_PROJECT_DIR')
    output_dir_str = os.environ.get('QUARTO_RENDER_OUTPUT_DIR')
    
    if not project_dir_str:
        print("Error: environment variable QUARTO_RENDER_PROJECT_DIR is not set", file=sys.stderr)
        print("Please set it to the path to your template Quarto project directory", file=sys.stderr)
        sys.exit(1)
    if not output_dir_str:
        print("Error: environment variable QUARTO_RENDER_OUTPUT_DIR is not set", file=sys.stderr)
        print("Please set it to the relative path to the output directory of the template project", file=sys.stderr)
        sys.exit(1)
    
    # Strip quotes from environment variables if present
    project_dir_str = project_dir_str.strip('"').strip("'")
    output_dir_str = output_dir_str.strip('"').strip("'")
    
    # Validate source document
    source_file = Path(args.document).resolve()
    if not source_file.exists():
        print(f"Error: File '{source_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    if not source_file.is_file():
        print(f"Error: '{source_file}' is not a file", file=sys.stderr)
        sys.exit(1)
    
    # Setup paths
    project_dir = Path(project_dir_str).resolve()
    orig_dir = Path.cwd()
    source_dir = source_file.parent
    filename = source_file.name
    
    # Check if project directory exists
    if not project_dir.exists():
        print(f"Error: Project directory '{project_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Collect all files to copy using glob
    matches = set()
    if args.resources:
        for resource in args.resources:
            resource_found = False
            # Always use glob for matching (handles both wildcards and literal paths)
            for match in glob.glob(resource, recursive=True):
                match_path = Path(match)
                # Only collect files, ignore directories
                if match_path.is_file():
                    matches.add(str(match_path.resolve()))
                    resource_found = True
            
            if not resource_found:
                print(f"Warning: Resource '{resource}' does not match any files, skipping", file=sys.stderr)
    
    # Add document to matches
    matches.add(str(source_file.resolve()))
    
    # Check for collisions before copying any files
    for match in matches:
        match_path = Path(match)
        match_filename = match_path.name
        
        # Check for collision with existing files in project directory
        target_resource_path = project_dir / match_filename
        if target_resource_path.exists():
            print(f"Error: File '{match_filename}' already exists in project directory '{project_dir}'", file=sys.stderr)
            sys.exit(1)
    
    # Copy all files (document and resources)
    for match in matches:
        match_path = Path(match)
        target_resource_path = project_dir / match_path.name
        print(f"Copying '{match_path}' to '{project_dir}/'")
        shutil.copy2(match_path, target_resource_path)
    
    try:
        # Change to project directory
        os.chdir(project_dir)
        
        # Remove existing output directory in project
        project_output_dir = project_dir / output_dir_str
        if project_output_dir.exists():
            print(f"Removing existing '{output_dir_str}' in project directory")
            shutil.rmtree(project_output_dir)
        
        # Detect and activate virtual environment if present
        venv_activated = False
        venv_dirs = ['.venv', 'venv', '.env']
        
        for venv_dir in venv_dirs:
            venv_path = project_dir / venv_dir
            if venv_path.exists() and venv_path.is_dir():
                # Check for activation script
                if sys.platform == 'win32':
                    activate_script = venv_path / 'Scripts' / 'activate.bat'
                else:
                    activate_script = venv_path / 'bin' / 'activate'
                
                if activate_script.exists():
                    print(f"Detected Python virtual environment in project directory: {venv_dir}")
                    venv_activated = True
                    break
        
        # Build and execute quarto command
        env = os.environ.copy()
        if venv_activated:
            # Modify environment to use the virtual environment
            if sys.platform == 'win32':
                venv_scripts = venv_path / 'Scripts'
                # Prepend venv Scripts to PATH
                env['PATH'] = f"{venv_scripts}{os.pathsep}{env.get('PATH', '')}"
                env['VIRTUAL_ENV'] = str(venv_path)
                # Unset PYTHONHOME if set
                env.pop('PYTHONHOME', None)
            else:
                venv_bin = venv_path / 'bin'
                # Prepend venv bin to PATH
                env['PATH'] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
                env['VIRTUAL_ENV'] = str(venv_path)
                env.pop('PYTHONHOME', None)
            
            print(f"Using Python virtual environment: {venv_path}")
        
        quarto_cmd = ['quarto', 'render', filename] + args.quarto_args
        print(f"Executing: {' '.join(quarto_cmd)}")
        result = subprocess.run(quarto_cmd, env=env, capture_output=False)
        
        if result.returncode != 0:
            print(f"Error: quarto render failed with exit code {result.returncode}", file=sys.stderr)
            sys.exit(result.returncode)
        
        # Copy output back to original directory
        if project_output_dir.exists():
            dest_output_dir = source_dir / output_dir_str
            print(f"Copying '{output_dir_str}' contents to '{dest_output_dir}' (overwriting existing files)")
            
            # Copy contents, overwriting existing files
            if dest_output_dir.exists():
                # Merge: copy tree with overwrite
                shutil.copytree(project_output_dir, dest_output_dir, dirs_exist_ok=True)
            else:
                # Fresh copy
                shutil.copytree(project_output_dir, dest_output_dir)
            
            print(f"Copy succeeded; removing source '{output_dir_str}'")
            shutil.rmtree(project_output_dir)
        else:
            print(f"No '{output_dir_str}' produced by quarto")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up: delete all copied files (document and resources) from project directory
        print("Cleaning up copied files from project directory")
        for match in matches:
            match_path = Path(match)
            target_resource = project_dir / match_path.name
            if target_resource.exists() and target_resource.is_file():
                print(f"Deleting '{match_path.name}' from project directory")
                target_resource.unlink()
        
        # Always return to original directory
        os.chdir(orig_dir)


if __name__ == '__main__':
    main()
