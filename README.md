# BackupScripter

## Description

A backup script editor with a GUI. Still a work-in-progress. Create a single-file executable .pyz file that compiles files and folders into a single file (e.g. .zip). Has a basic file explorer for browsing included directories and choosing directories to exclude, showing the size and nested item counts for directory items. Use matching groups to dynamically exclude (include not supported yet) files and folders based off of patterns and conditions checked at script runtime.



## State of BackupScripter

Work-in-Progress, but functional. Not quite ready.

There is no guarantee that generated scripts will be editable from future updates to the editor. This is a current priority.



## Download & Installation

Coming Soon



## Building

Clone repo:
```
git clone https://github.com/seth-kitchens/BackupScripter
```

Install requirements:
```
cd backupscripter
python -m pip install -r requirements.txt
```

Run BackupScripter
```
python .
```

Run BackupScript in Debug:

1. Double-click scripts/test_editor.py

OR

2. Enter into cmd:
```
python . --debug --noterm
```

Without, --noterm it will open an extra cmd on its own.



## Testing

Run unit tests with the `run_tests.py` script in `scripts/`
