# clideps

(New and currently in progress!)

clideps is a cross-platform tool and library that helps with the headache of checking
your system setup and if you have various dependencies set up right:

- Environment variables, .env files, and API keys

- System tools and packages: Check for external tools (like ffmpeg or ripgrep) and
  environment variables (such as API keys) available.

- Python external library dependencies

And then it interactively helps you fix it!

- It can help you find and safely edit .env files with API keys

- It can check if you have packages installed

- If you don't, it can tell you how to install them using whatever package manager you
  use

- If you don't have a package manager installed, it will help you install it too!

Supports several major package managers on macOS, Windows, and Linux.

## Usage

It is available on PyPy `clideps` so do the usual `uv add clideps` or `pip install clideps`, etc.
For uv users (recommended):

```
# Run the cli
uvx clideps --help

# Check current setup
uvx clideps check
```

<img width="994" alt="output of uvx clideps check" src="https://github.com/user-attachments/assets/a2ff1d83-3494-4820-800a-0c359c34fc92" />


* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
