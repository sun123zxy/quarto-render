# quarto-render

A command line tool to let you render independent Quarto documents as if they were within a Quarto project.

- `quarto-render` will first ask you to provide a Quarto project directory and its associated output directory in environment variables.

- Once set up, executing `quarto-render` with a Quarto document path will copy the document to the specified project directory, along with any specified resources, with respect to their path relative to the current working directory.

- Then `quarto render` is executed within the project directory.

- Finally `quarto-render` moves the rendered output back to the current working directory, with respect to the output directory structure.

Python virtual environment in the specified Quarto project directory will be automatically detected and activated during rendering.

## Usage

```
usage: quarto-render [-h] document [-r RESOURCE [RESOURCE ...]] [quarto options]

Render independent Quarto documents as if they were within a Quarto project.

positional arguments:
  document              Path to the Quarto document to render

options:
  -h, --help            show this help message and exit
  -r, --resources RESOURCE [RESOURCE ...]
                        Paths to resources (e.g., images or bibliography files) to copy alongside the document. Shell-expanded
                        paths are accepted, and the option can be used multiple times.

unrecognized arguments are passed to quarto render.

environment variables:
  QUARTO_RENDER_PROJECT_DIR     Path to the template Quarto project directory
  QUARTO_RENDER_OUTPUT_DIR      Relative path to the output directory of the template project
```

You might wish to add this tool to your system PATH for easier access.

### Resources and shell expansion

`quarto-render` accepts one or more file paths after `-r`. It does not expand glob patterns itself. On shells that perform glob expansion, such as Bash and Zsh, leave the pattern unquoted so the shell passes the matching files to `quarto-render`:

```bash
quarto-render slide.qmd -r img/*
```

The document must appear before a multi-value `-r` option. Otherwise, `-r` will consume the document path as another resource. The option may also be repeated:

```bash
quarto-render slide.qmd -r img/a.jpg img/b.jpg -r references.bib
```

Options not recognized by `quarto-render` are passed to Quarto:

```bash
quarto-render slide.qmd -r img/* --toc --format revealjs
```

PowerShell and Command Prompt do not normally expand wildcards for native programs. In PowerShell, expand the files explicitly:

```powershell
quarto-render slide.qmd -r (Get-ChildItem -File img/*).FullName
```

In Command Prompt, list the resource paths explicitly.

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
