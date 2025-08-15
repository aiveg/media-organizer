#!/usr/bin/env python3
"""
Организатор медиафайлов
Автор: Дима
Описание: Организует фото и видео по папкам с датами
"""

import tkinter as tk
from gui import MediaOrganizerGUI

def main():
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

