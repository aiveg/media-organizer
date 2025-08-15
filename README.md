# Media Organizer

A small cross-platform Python utility that **sorts photos and videos into date-named folders** (`YYYY-MM-DD`).  
Optional features:  
- Split large days into `Before_12` / `After_12` subfolders (if files > 100)  
- Remove empty source folders  
- Move non-media leftovers to an **Archive** folder  

**Tech stack:**  
- GUI: `tkinter`  
- Metadata: `Pillow` + `Hachoir`  
- Tested on macOS, should work on Windows/Linux.

---

## Features
- Recursive scan of any folder
- EXIF / video metadata date detection (fallback: file creation time)
- Drag-and-drop (macOS) or Browse button
- Real-time log with context menu (copy / clear)
- Safe mode: nothing is deleted without the corresponding checkbox

## Installation

```bash
git clone git@github.com:aiveg/media-organizer.git
cd media-organizer

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

## Packaging

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The compiled binary will appear in the `dist/` folder.

## License
MIT
