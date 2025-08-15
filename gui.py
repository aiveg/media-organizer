# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from file_processor import FileProcessor

class MediaOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Организатор медиафайлов")
        self.root.geometry("700x600")
        
        self.selected_folder = tk.StringVar()
        self.delete_empty_var = tk.BooleanVar()
        self.archive_non_empty_var = tk.BooleanVar()
        self.is_processing = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # Выбор папки
        folder_frame = ttk.Frame(self.root, padding="10")
        folder_frame.pack(fill=tk.X)
        
        ttk.Label(folder_frame, text="Выберите папку с медиафайлами:").pack(anchor=tk.W)
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.folder_entry = ttk.Entry(folder_select_frame, textvariable=self.selected_folder, state="readonly")
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_select_frame, text="Обзор...", command=self.select_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Настройки
        options_frame = ttk.LabelFrame(self.root, text="Настройки", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(options_frame, text="Удалить пустые исходные папки", variable=self.delete_empty_var).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Архивировать непустые исходные папки", variable=self.archive_non_empty_var).pack(anchor=tk.W)
        
        # Кнопки
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Запустить организацию", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Очистить лог", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Прогресс
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="Готов к работе")
        self.status_label.pack(pady=5)
        
        # Лог с возможностью копирования
        log_frame = ttk.LabelFrame(self.root, text="Результаты", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаём контекстное меню для копирования
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать всё", command=self.copy_all_text)
        self.context_menu.add_command(label="Копировать выделенное", command=self.copy_selected_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить", command=self.clear_log)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем контекстное меню
        self.log_text.bind("<Button-2>", self.show_context_menu)  # Правая кнопка на Mac
        self.log_text.bind("<Button-3>", self.show_context_menu)  # Правая кнопка на Windows/Linux
    
    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_all_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        self.log_message("✓ Весь текст скопирован в буфер обмена")
    
    def copy_selected_text(self):
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.log_message("✓ Выделенный текст скопирован в буфер обмена")
        except tk.TclError:
            self.log_message("⚠ Сначала выделите текст для копирования")
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.update_status("Лог очищен")
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_processing(self):
        if self.is_processing:
            messagebox.showwarning("Внимание", "Обработка уже выполняется!")
            return
            
        if not self.selected_folder.get():
            messagebox.showerror("Ошибка", "Выберите папку для обработки!")
            return
        
        # Запускаем обработку в отдельном потоке
        self.is_processing = True
        self.start_button.config(text="Обработка...", state="disabled")
        threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        try:
            self.progress.start()
            self.update_status("Выполняется обработка файлов...")
            
            processor = FileProcessor(
                self.selected_folder.get(),
                self.delete_empty_var.get(),
                self.archive_non_empty_var.get()
            )
            
            self.log_message("=" * 50)
            self.log_message(f"🚀 НАЧИНАЕМ ОБРАБОТКУ: {self.selected_folder.get()}")
            self.log_message("=" * 50)
            
            processed_count, error_count = processor.process_files()
            
            # Выводим результаты
            self.log_message("\n" + "=" * 50)
            self.log_message("✅ ОБРАБОТКА ЗАВЕРШЕНА!")
            self.log_message(f"📊 Обработано операций: {processed_count}")
            self.log_message(f"❌ Ошибок: {error_count}")
            self.log_message("=" * 50)
            
            # Выводим детали
            if processor.processed_files:
                self.log_message("\n📁 ВЫПОЛНЕННЫЕ ОПЕРАЦИИ:")
                for operation in processor.processed_files:
                    self.log_message(f"  ✓ {operation}")
            
            if processor.errors:
                self.log_message("\n⚠️  ОШИБКИ:")
                for error in processor.errors:
                    self.log_message(f"  ✗ {error}")
            
            self.log_message(f"\n🎉 Готово! Можете проверить результат в папке: {self.selected_folder.get()}")
            self.update_status(f"Завершено! Операций: {processed_count}, Ошибок: {error_count}")
            
            # Показываем уведомление
            messagebox.showinfo("Готово!", f"Обработка завершена!\nОпераций: {processed_count}\nОшибок: {error_count}")
            
        except Exception as e:
            self.log_message(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
            self.update_status("Ошибка выполнения")
            messagebox.showerror("Ошибка", f"Критическая ошибка: {e}")
        finally:
            self.progress.stop()
            self.is_processing = False
            self.start_button.config(text="Запустить организацию", state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop()
