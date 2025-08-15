# Media Organizer

Небольшая кроссплатформенная утилита на Python, которая **раскладывает фото и видео по папкам с датой** (`YYYY-MM-DD`).  
Дополнительно может:  
- Делить большой день на подпапки `До_12` / `После_12` (если файлов > 100)  
- Удалять пустые исходные каталоги  
- Складывать «несортированные» файлы в папку **Архив**

**Технологии:**  
- GUI: `tkinter`  
- Даты: `Pillow` + `Hachoir`  
- Проверено на macOS, работает на Windows/Linux.

---

## Возможности
- Рекурсивный обход всех подпапок
- Определение даты из EXIF / видеометаданных (если нет — берётся дата создания файла)
- Drag-and-drop (macOS) или кнопка «Обзор»
- Живой лог с копированием и очисткой
- Безопасный режим: ничего не удаляется без соответствующей галочки

## Установка

```bash
git clone git@github.com:aiveg/media-organizer.git
cd media-organizer

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

## Сборка EXE / APP

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Готовый исполняемый файл появится в папке `dist/`.

## Лицензия
MIT
