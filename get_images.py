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
from config import URL_BOOKS, URL_LOGIN, BOOK_ID, BOOK_NAME, PAGES, LOGIN, PASSWORD, READER_URL


def check_close(driver):
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

    print("\n" + "=" * 60)
    print("✉️  Авторизация в аккаунте Литрес:")
    print("1. Введите почту, пароль и код подтверждения в открывшемся браузере.")
    print("2. Дождитесь, пока полностью прогрузится ваш профиль.")
    print("3. Вернитесь в эту консоль и НАЖМИТЕ ENTER для продолжения.")
    print("=" * 60 + "\n")
    
    input("👉 Нажмите ENTER, когда успешно войдете в аккаунт...")

    print("Открываем читалку...")
    driver.get(READER_URL)
    time.sleep(6)


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


def load_books(driver: WebDriver):
    print(f"Создаем директорию books/{BOOK_NAME}_{BOOK_ID}")
    os.makedirs(f"books/{BOOK_NAME}_{BOOK_ID}", exist_ok=True)
    driver.set_window_size(1280, 800)
    
    # Принудительно сбрасываем прокрутку в самый верх (на 0-ю страницу)
    driver.execute_script("""
        var container = document.getElementById('canvas');
        if (container) {
            container.scrollTop = 0;
        } else {
            window.scrollTo(0, 0);
        }
    """)
    time.sleep(2)
    
    print("Начинаем скачивание страниц с самого начала...")
    
    for i in range(PAGES):
        file_path = f"books/{BOOK_NAME}_{BOOK_ID}/{i}.jpg"
        
        # Если страница уже скачана ранее, пропускаем её
        if os.path.exists(file_path):
            print(f"Страница {i} уже есть, пропускаем.")
            continue
            
        success = False
        for attempt in range(25):  # Прокручиваем вниз в поисках нужной страницы
            js_script = f"""
            var div = document.getElementById('p_{i}');
            if (!div) return null;
            
            // Прокручиваем к этой странице в центр экрана
            div.scrollIntoView({{behavior: 'instant', block: 'center'}});
            
            var img = div.querySelector('img');
            if (!img || !img.src || !img.complete || img.naturalWidth === 0) return null;
            
            var canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/jpeg', 0.95).substring(22);
            """
            
            image_base64 = driver.execute_script(js_script)
            
            if image_base64:
                image_bytes = base64.b64decode(image_base64)
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Страница {i} успешно сохранена.")
                success = True
                break
            else:
                # Если страница еще не подгрузилась в DOM, скроллим контейнер дальше вниз
                driver.execute_script("""
                    var container = document.getElementById('canvas');
                    if (container) {
                        container.scrollBy(0, 500);
                    } else {
                        window.scrollBy(0, 500);
                    }
                """)
                time.sleep(0.3)
                
        if not success:
            print(f"Не удалось найти или вытащить страницу {i}.")
            break

    print("Все страницы успешно обработаны!")


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