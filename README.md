# Neighborly Wiki Generator

This repository generates HTML wiki pages from [Neighborly](https://github.com/ShiJbey/neighborly) simulations.

Currently, the pages are very simple and include the same data as one would see if they ran Neighborly's sample simulation using `python -i samples/sample.py` and called `inspect(...)` using GameObject IDs.

## Installation instructions

```bash
# Step 0: Clone or download + extract the repository.

# Step 1: Then change to the repository or open it in a terminal
cd neighborly-wiki-generator

# Step 2: (Linux/MacOS) Create a virtual environment to hold dependencies.
python3 -m venv venv

# Step 2: (Windows) Create a virtual environment to hold dependencies.
python -m venv venv

# Step 3: (Linux/MacOS) Activate the virtual environment
source venv/bin/activate

# Step 3: (Windows using PowerShell) Activate the virtual environment
# You may need to enable script execution. Follow the instructions at this link
# https://superuser.com/questions/106360/how-to-enable-execution-of-powershell-scripts#106363
./venv/Scripts/activate.ps1

# Step 4: Install dependencies
python -m pip install -r requirements.txt
```

## Usage Instructions

### Running the generator

Currently, the generator accepts JSON data from a Neighborly simulation and extracts various parts data to create HTML pages. It accepts the path to the file containing the JSON data as the main parameter. The generated HTML pages are placed in the `output/` directory.

```bash
python main.py path/to/data.json
```

The following will print help information for how to use the generator:

```bash
python main.py --help
```

Example data is provided in the `data/` directory for users to experiment with.

### Open the wiki in the generator

We use the http server that comes with python to serve files from the `output/` directory.

```bash
python -m http.server -d output
```

### Updating the page templates

All pages are generated using the Jinja2 templates located in the `templates/` directory.
