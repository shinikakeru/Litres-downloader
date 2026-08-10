import os
import time
import requests
import base64

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import URL_BOOKS, URL_LOGIN, BOOK_ID, BOOK_NAME, PAGES, LOGIN, PASSWORD


def check_close(driver):
    """
    wait until user closed browser window
    :param driver:
    :return:
    """
    closed = False
    try:
        driver.title
    except Exception:
        return
        
    while not closed:
        try:
            driver.title
            time.sleep(1)
        except Exception:
            closed = True


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_service = Service(ChromeDriverManager().install())
    driver: WebDriver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver


def login_litres(driver):
    driver.get(URL_LOGIN)

    username_in = driver.find_element(by=By.NAME, value='email')
    username_in.click()
    username_in.send_keys(LOGIN)
    username_in.send_keys(Keys.RETURN)
    time.sleep(2)
    password_in = driver.find_element(by=By.NAME, value='pwd')
    password_in.send_keys(PASSWORD)
    time.sleep(1)
    password_in.send_keys(Keys.RETURN)
    time.sleep(2)


def scroll_down(driver):
    count = 0
    while True:
        page = driver.find_element(by=By.TAG_NAME, value="html")

        page.send_keys(Keys.END)
        driver.implicitly_wait(1)
        page.send_keys(Keys.END)
        driver.implicitly_wait(1)
        page.send_keys(Keys.END)
        count += 1
        print(f'scroll down {count}')
        driver.implicitly_wait(1)
        footer = driver.find_element(by=By.CLASS_NAME, value='footer-wrap')
        if footer and footer.is_displayed():
            loader_button = driver.find_element(by=By.ID, value='arts_loader_button')
            if loader_button and not loader_button.is_displayed():
                break

    print(f'scroll down exit after {count} scrolls')

import base64

def load_books(driver: WebDriver):
    print(f"create dir {BOOK_NAME}_{BOOK_ID}")
    if not os.path.exists("books"):
        os.mkdir("books")
    if not os.path.exists(f"books/{BOOK_NAME}_{BOOK_ID}"):
        os.makedirs(f"books/{BOOK_NAME}_{BOOK_ID}")
    driver.set_window_size(1280, 800)
    available_file_types = ['jpg', 'gif', 'jpeg', 'png', 'webp']
    
    for i in range(PAGES):
        percent = ((i + 1) / PAGES) * 100
        success = False
        
        for file_type in available_file_types:
            src = URL_BOOKS.format(i, file_type, BOOK_ID)
            
            if src.startswith("//"):
                src = "https:" + src
            elif not src.startswith("http"):
                src = "https://litres.ru" + src
            
            driver.get(src)
            time.sleep(1.5)  # Ждем загрузки картинки в кэш браузера
            
            page_title = driver.title.lower()
            if "403" in page_title or "forbidden" in page_title or "404" in page_title or "not found" in page_title:
                continue

            try:
                # Находим элемент изображения
                img_element = driver.find_element(By.TAG_NAME, "img")
                current_src = img_element.get_attribute("src")
                
                if BOOK_ID not in current_src:
                    continue

                js_script = """
                var img = arguments[0];
                var canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/jpeg').substring(22);
                """
                
                # Выполняем скрипт в Chrome и получаем байты оригинального файла
                image_base64 = driver.execute_script(js_script, img_element)
                image_bytes = base64.b64decode(image_base64)
                
                # Сохраняем чистый файл без сжатия экрана
                with open(f"books/{BOOK_NAME}_{BOOK_ID}/{i}.{file_type}", "wb") as f:
                    f.write(image_bytes)
                    
                print(f"Успешно сохранена страница {i} в оригинальном качестве ({file_type})")
                success = True
                
                if available_file_types != file_type:
                    available_file_types = [file_type] + [t for t in available_file_types if t != file_type]
                break
                
            except Exception as e:
                continue
        
        if not success:
            print(f"Не удалось получить страницу {i}.")
            if i > 0: 
                break

        if abs(percent - round(percent)) > 0.2:
            print(f"Done: {round(percent, 2)}%")


def litres_loads():
    driver = create_driver()
    driver.maximize_window()
    login_litres(driver)
    load_books(driver)
    time.sleep(1)

    check_close(driver)
    print('FINISH!')


def main():
    litres_loads()


if __name__ == '__main__':
    main()
