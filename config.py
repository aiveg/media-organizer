# Поддерживаемые форматы файлов
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.raw', '.cr2', '.nef'}
HEIC_EXTENSIONS = {'.heic'}  # Отдельно для HEIC файлов

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp', '.wmv', '.flv'}

# Формат папок с датами
DATE_FORMAT = "%Y-%m-%d"  # 2025-04-01

# Названия служебных папок
ARCHIVE_FOLDER = "Архив"
UNKNOWN_DATE_FOLDER = "НеизвестнаяДата"

# Лимит файлов для создания подпапок по времени
FILES_LIMIT_FOR_TIME_SPLIT = 100
