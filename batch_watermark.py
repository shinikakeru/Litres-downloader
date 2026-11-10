import os
from PIL import Image, ImageDraw, ImageFont

def add_watermark_to_image(file_path, text="t.me/xmyaff"):
    try:
        img = Image.open(file_path).convert("RGBA")
        width, height = img.size
        
        watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        try:
            font = ImageFont.truetype("arial.ttf", int(width * 0.04))
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", int(width * 0.04))
            except:
                font = ImageFont.load_default()
                
        # Плотность/прозрачность (100 — оптимально: хорошо видно, но не мешает читать)
        fill_color = (100, 100, 100, 100)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        # Создаем заготовку текста для поворота
        txt_img = Image.new("RGBA", (tw + 40, th + 40), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((20, 20), text, fill=fill_color, font=font)
        
        # Поворачиваем по диагонали на -30 градусов
        rotated_txt = txt_img.rotate(-30, expand=True, resample=Image.BICUBIC)
        rw, rh = rotated_txt.size
        
        # Делаем идеальную симметричную сетку (2 колонки, 3 ряда)
        cols = 2
        rows = 3
        step_x = width / cols
        step_y = height / rows
        
        for r in range(rows):
            for c in range(cols):
                # Вычисляем центр каждой ячейки и центрируем в ней текст
                cell_center_x = c * step_x + step_x / 2
                cell_center_y = r * step_y + step_y / 2
                
                paste_x = int(cell_center_x - rw / 2)
                paste_y = int(cell_center_y - rh / 2)
                
                watermark_layer.paste(rotated_txt, (paste_x, paste_y), rotated_txt)
                
        watermarked = Image.alpha_composite(img, watermark_layer)
        rgb_img = watermarked.convert("RGB")
        rgb_img.save(file_path, "JPEG", quality=95)
        print(f"Отцентрировано и защищено: {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"Ошибка с файлом {file_path}: {e}")

def process_book_by_query(search_query, text="t.me/xmyaff"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_dir = os.path.join(script_dir, "books")
    
    if not os.path.exists(books_dir):
        print(f"Папка 'books' не найдена по пути: {books_dir}")
        return
        
    matching_folders = []
    for item in os.listdir(books_dir):
        item_path = os.path.join(books_dir, item)
        if os.path.isdir(item_path) and search_query.lower() in item.lower():
            matching_folders.append(item_path)
            
    if not matching_folders:
        print(f"❌ Не найдено папок в 'books', содержащих запрос: '{search_query}'")
        return
        
    target_folder = matching_folders[0]
    print(f"📁 Обрабатываем папку: {os.path.basename(target_folder)}\n")
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    files = os.listdir(target_folder)
    count = 0
    
    for filename in files:
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(target_folder, filename)
            add_watermark_to_image(file_path, text)
            count += 1
            
    print(f"\n✨ Готово! Ровно отцентрировано файлов: {count}")

if __name__ == "__main__":
    BOOK_QUERY = "128856228" 
    WATERMARK_TEXT = "t.me/xmyaff"
    
    process_book_by_query(BOOK_QUERY, WATERMARK_TEXT)