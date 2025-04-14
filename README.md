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

It is available as a pip as `clideps` so use as usual.
For uv users (recommended):

```
# Run the cli
uvx clideps
# Add to your project and you will be able to streamline setup for your users:
uv add clideps
```

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
