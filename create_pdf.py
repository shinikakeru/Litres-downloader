import os
import re
import img2pdf
from config import BOOK_NAME, BOOK_ID

def get_page_number(filename):

    base_name = os.path.basename(filename)
    name_without_ext = os.path.splitext(base_name)[0]
    
    # Находим все цифры в названии
    match = re.search(r'\d+', name_without_ext)
    return int(match.group()) if match else 0

def convert_images_to_pdf():
    # Путь к папке со скачанными картинками
    folder_path = f"books/{BOOK_NAME}_{BOOK_ID}"
    
    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не найдена! Проверьте config.py или запустите сначала основной парсер.")
        return

    print(f"Поиск изображений в папке: {folder_path}...")
    
    # Список поддерживаемых форматов картинок
    valid_extensions = ('.jpg', '.jpeg', '.gif', '.png', '.webp')
    
    # Собираем полные пути ко всем картинкам в папке
    image_paths = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(valid_extensions):
            image_paths.append(os.path.join(folder_path, file))

    if not image_paths:
        print("Ошибка: В папке нет подходящих изображений для сборки.")
        return

    print(f"Найдено изображений: {len(image_paths)}. Сортировка по страницам...")
    image_paths.sort(key=get_page_number)

    # Путь, куда сохранится готовый PDF
    pdf_output_path = f"books/{BOOK_NAME}_{BOOK_ID}.pdf"
    print("Начинается прямая сборка PDF (без потери качества)...")

    try:
        with open(pdf_output_path, "wb") as f:
            # Упаковываем байты картинок напрямую в контейнер PDF
            f.write(img2pdf.convert(image_paths))
        print(f"Сборка завершена успешно!")
        print(f"👉 Готовый файл сохранен по пути: {os.path.abspath(pdf_output_path)}")
    except Exception as e:
        print(f"Ошибка при генерации PDF: {e}")

if __name__ == "__main__":
    convert_images_to_pdf()
