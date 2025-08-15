# file_processor.py
import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import config

class FileProcessor:
    def __init__(self, source_folder, delete_empty=False, archive_non_empty=False):
        self.source_folder = Path(source_folder)
        self.delete_empty = delete_empty
        self.archive_non_empty = archive_non_empty
        self.processed_files = []
        self.errors = []
    
    def get_photo_date(self, file_path):
        """Извлекает дату съёмки из EXIF фото"""
        try:
            image = Image.open(file_path)
            exif = image._getexif()
            
            if exif:
                for tag, value in exif.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'DateTimeOriginal':
                        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
            return None
        except Exception as e:
            self.errors.append(f"Ошибка чтения EXIF {file_path}: {e}")
            return None
    
    def get_video_date(self, file_path):
        """Извлекает дату создания видео"""
        try:
            parser = createParser(str(file_path))
            if parser:
                metadata = extractMetadata(parser)
                if metadata and hasattr(metadata, 'creation_date'):
                    cd = metadata.creation_date
                    # Исправляем: если дата в виде кортежа, берём первый элемент
                    if isinstance(cd, tuple) and len(cd) > 0:
                        return cd[0]  # Первый элемент - сама дата
                    return cd
            return None
        except Exception as e:
            self.errors.append(f"Ошибка чтения метаданных {file_path}: {e}")
            return None

    def get_file_date(self, file_path):
        """Получает дату файла (EXIF/метаданные или дата создания)"""
        file_ext = file_path.suffix.lower()
        
        # Пробуем получить дату из EXIF/метаданных
        if file_ext in config.PHOTO_EXTENSIONS:
            date = self.get_photo_date(file_path)
        elif file_ext in config.HEIC_EXTENSIONS:
            # Для HEIC используем дату файла, так как PIL их не читает
            date = None  # Будет использована дата создания файла

        elif file_ext in config.VIDEO_EXTENSIONS:
            date = self.get_video_date(file_path)
        else:
            return None  # Не медиафайл
        
        # Если не получилось - берём дату создания файла
        if date is None:
            try:
                stat = file_path.stat()
                # На macOS используем st_birthtime, на других системах - st_mtime
                if hasattr(stat, 'st_birthtime'):
                    date = datetime.fromtimestamp(stat.st_birthtime)
                else:
                    date = datetime.fromtimestamp(stat.st_mtime)
            except Exception:
                date = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        return date
    
    def create_date_folder(self, base_folder, date):
        """Создаёт папку по дате"""
        date_folder = base_folder / date.strftime(config.DATE_FORMAT)
        date_folder.mkdir(exist_ok=True)
        return date_folder
    
    def create_time_subfolder(self, date_folder, date, file_count):
        """Создаёт подпапку по времени, если файлов много"""
        if file_count <= config.FILES_LIMIT_FOR_TIME_SPLIT:
            return date_folder
        
        # Определяем время: до 12:00 или после
        time_suffix = "До_12" if date.hour < 12 else "После_12"
        time_folder = date_folder / time_suffix
        time_folder.mkdir(exist_ok=True)
        return time_folder
    
    def move_file(self, source_file, target_folder):
        """Перемещает файл в целевую папку"""
        try:
            target_file = target_folder / source_file.name
            
            # Если файл уже существует, добавляем суффикс
            counter = 1
            while target_file.exists():
                name_parts = source_file.stem, counter, source_file.suffix
                target_file = target_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.move(str(source_file), str(target_file))
            self.processed_files.append(f"Перемещён: {source_file} → {target_file}")
            return True
        except Exception as e:
            self.errors.append(f"Ошибка перемещения {source_file}: {e}")
            return False
    
    def scan_files(self):
        """Сканирует все файлы в папке и подпапках"""
        media_files = {}  # {дата: [файлы]}
        other_files = []
        
        for file_path in self.source_folder.rglob('*'):
            if file_path.is_file():
                date = self.get_file_date(file_path)
                
                if date:
                    date_key = date.strftime(config.DATE_FORMAT)
                    if date_key not in media_files:
                        media_files[date_key] = []
                    media_files[date_key].append((file_path, date))
                else:
                    other_files.append(file_path)
        
        return media_files, other_files
    
    def process_files(self):
        """Основной метод обработки файлов"""
        print("Сканирование файлов...")
        media_files, other_files = self.scan_files()
        
        print(f"Найдено медиафайлов: {sum(len(files) for files in media_files.values())}")
        print(f"Найдено других файлов: {len(other_files)}")
        
        # Обрабатываем медиафайлы
        for date_str, files in media_files.items():
            date_folder = self.create_date_folder(self.source_folder, files[0][1])  # ИСПРАВЛЕНО
            
            for file_path, file_date in files:
                target_folder = self.create_time_subfolder(date_folder, file_date, len(files))
                self.move_file(file_path, target_folder)
        
        # Обрабатываем остальные файлы (если нужно архивировать)
        if other_files and self.archive_non_empty:
            archive_folder = self.source_folder / config.ARCHIVE_FOLDER
            archive_folder.mkdir(exist_ok=True)
            
            for file_path in other_files:
                self.move_file(file_path, archive_folder)
        
        # Удаляем пустые папки (если нужно)
        if self.delete_empty:
            self.cleanup_empty_folders()
        
        return len(self.processed_files), len(self.errors)
    
    def cleanup_empty_folders(self):
        """Удаляет пустые папки"""
        for folder_path in sorted(self.source_folder.rglob('*'), reverse=True):
            if folder_path.is_dir() and not any(folder_path.iterdir()):
                try:
                    folder_path.rmdir()
                    self.processed_files.append(f"Удалена пустая папка: {folder_path}")
                except Exception as e:
                    self.errors.append(f"Ошибка удаления папки {folder_path}: {e}")
