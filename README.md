## quarto-render

A command line tool to let you render independent Quarto documents as if they were within a Quarto project.

`quarto-render` will first ask you to provide a Quarto project directory and its associated output directory in environment variables. After that, executing `quarto-render` with a Quarto document path will copy the document to the specified project directory, render it there, and then move the rendered output back to the original directory.

### Usage

```
usage: quarto-render [-h] [-r RESOURCES] document [quarto_args ...]

Render independent Quarto documents as if they were within a Quarto project.

positional arguments:
  document              Path to the Quarto document to render
  quarto_args           Additional arguments to pass to quarto render

options:
  -h, --help            show this help message and exit
  -r, --resources RESOURCES
                        Path to resources (e.g., images, bibliography files) to be copied alongside the document. Can  
                        be used multiple times. Supports glob patterns.

environment variables:
  QUARTO_RENDER_PROJECT_DIR     Path to the template Quarto project directory
  QUARTO_RENDER_OUTPUT_DIR      Relative path to the output directory of the template project
```