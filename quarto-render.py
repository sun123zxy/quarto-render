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
environment variables:
  QUARTO_RENDER_PROJECT_DIR     Path to the template Quarto project directory
  QUARTO_RENDER_OUTPUT_DIR      Relative path to the output directory of the template project
        """
    )
    
    parser.add_argument(
        'document',
        help='Path to the Quarto document to render'
    )
    
    parser.add_argument(
        '-r', '--resources',
        action='append',
        help='Path to resources (e.g., images, bibliography files) to be copied alongside the document. Can be used multiple times. Supports glob patterns.'
    )
    
    parser.add_argument(
        'quarto_args',
        nargs='*',
        help='Additional arguments to pass to quarto render'
    )
    
    args = parser.parse_args()
    
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
    
    try:
        # Collect all files to copy using glob
        matches = []
        if args.resources:
            for resource in args.resources:
                # Always use glob for matching (handles both wildcards and literal paths)
                for match in glob.glob(resource, recursive=True):
                    match_path = Path(match)
                    # Only collect files, ignore directories
                    if match_path.is_file():
                        matches.append(str(match_path))
                
                if not matches:
                    print(f"Warning: Resource '{resource}' does not match any files, skipping", file=sys.stderr)
        
        # Append document to matches if not already included
        source_file_str = str(source_file)
        if source_file_str not in matches:
            matches.append(source_file_str)
        
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
        
        # Change to project directory
        os.chdir(project_dir)
        
        # Remove existing output directory in project
        project_output_dir = project_dir / output_dir_str
        if project_output_dir.exists():
            print(f"Removing existing '{output_dir_str}' in project directory")
            shutil.rmtree(project_output_dir)
        
        # Build and execute quarto command
        quarto_cmd = ['quarto', 'render', filename] + args.quarto_args
        print(f"Executing: {' '.join(quarto_cmd)}")
        
        result = subprocess.run(quarto_cmd, capture_output=False)
        
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
        
        # Clean up: delete all copied files (document and resources) from project directory
        for match in matches:
            match_path = Path(match)
            target_resource = project_dir / match_path.name
            if target_resource.exists() and target_resource.is_file():
                print(f"Deleting '{match_path.name}' from project directory")
                target_resource.unlink()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Always return to original directory
        os.chdir(orig_dir)


if __name__ == '__main__':
    main()
