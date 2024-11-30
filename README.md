# Process Eye 👁️

## Description

Alternative sollution to TOP or HTOP, with a different approach to the visualization of the processes.

## Features

- [x] List of processes
- [x] Process details
- [x] Kill process
- [x] Search process
- [x] Sort by column
- [x] Export to JSON

## Installation

```bash
git clone 
cd process-eye
#Compile Executable
pyinstaller --onefile --add-data "ascii_art.txt:." main.py
# Rename the executable
mv dist/main dist/eyemonit
# Move it to /usr/local/bin (may require sudo)
sudo mv dist/eyemonit /usr/local/bin/

# Run it
eyemonit
```

