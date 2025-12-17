# quarto-render

A command line tool to let you render independent Quarto documents as if they were within a Quarto project.

- `quarto-render` will first ask you to provide a Quarto project directory and its associated output directory in environment variables.

- Once set up, executing `quarto-render` with a Quarto document path will copy the document to the specified project directory, along with any specified resources, with respect to their path relative to the current working directory.

- Then `quarto render` is executed within the project directory.

- Finally `quarto-render` moves the rendered output back to the current working directory, with respect to the output directory structure.

Python virtual environment in the specified Quarto project directory will be automatically detected and activated during rendering.

## Usage

```
usage: quarto-render [-h] [-r RESOURCES] document

Render independent Quarto documents as if they were within a Quarto project.

positional arguments:
  document              Path to the Quarto document to render

options:
  -h, --help            show this help message and exit
  -r, --resources RESOURCES
                        Path to resources (e.g., images, bibliography files) to be copied alongside the document. Can be used  
                        multiple times. Supports glob patterns.

unrecognized arguments are passed to quarto render.

environment variables:
  QUARTO_RENDER_PROJECT_DIR     Path to the template Quarto project directory
  QUARTO_RENDER_OUTPUT_DIR      Relative path to the output directory of the template project
```

You might wish to add this tool to your system PATH for easier access.

### Setting Up Environment Variables

To set up the environment variables, execute the following commands in your terminal:

```bash
export QUARTO_RENDER_PROJECT_DIR="/path/to/your/quarto/project"
export QUARTO_RENDER_OUTPUT_DIR="_output"
```

Or, on Windows Command Prompt:

```cmd
set QUARTO_RENDER_PROJECT_DIR="C:\path\to\your\quarto\project"
set QUARTO_RENDER_OUTPUT_DIR="_output"
```

You might wish to add them to your system environment variables.

## Building Executable

```bash
uv pip install pyinstaller
pyinstaller --onefile --name quarto-render quarto-render.py
```