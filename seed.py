# fill_database.py
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

# Функція для хешування паролів
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Підключення до бази даних
conn = sqlite3.connect('robotics_shop.db')
cursor = conn.cursor()

# Очищення існуючих даних
cursor.execute("DELETE FROM chat_messages")
cursor.execute("DELETE FROM reviews")
cursor.execute("DELETE FROM order_items")
cursor.execute("DELETE FROM orders")
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM categories")
cursor.execute("DELETE FROM users")

print("База даних очищена. Починаємо заповнення...")

# Додавання менеджерів
managers = [
    ("admin", "admin@robotics.com", "admin123"),
    ("manager", "manager@robotics.com", "manager123")
]

for username, email, password in managers:
    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, hashed_password, "manager")
    )
    print(f"Доданий менеджер: {username}")

# Додавання клієнтів
clients = [
    ("oleksandr", "oleksandr@example.com", "password123"),
    ("mariya", "mariya@example.com", "password123"),
    ("ivan", "ivan@example.com", "password123"),
    ("anna", "anna@example.com", "password123"),
    ("petro", "petro@example.com", "password123"),
    ("natalia", "natalia@example.com", "password123"),
    ("volodymyr", "volodymyr@example.com", "password123"),
    ("olena", "olena@example.com", "password123"),
    ("sergiy", "sergiy@example.com", "password123"),
    ("tetyana", "tetyana@example.com", "password123")
]

for username, email, password in clients:
    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, hashed_password, "client")
    )
    print(f"Доданий клієнт: {username}")

# Додавання категорій
categories = [
    ("Мікроконтролери", "Різноманітні мікроконтролери та плати розробника"),
    ("Сенсори", "Датчики та сенсори для робототехнічних проектів"),
    ("Двигуни і приводи", "Мотори, сервоприводи та інші компоненти руху"),
    ("Живлення", "Акумулятори, блоки живлення та перетворювачі"),
    ("Інструменти", "Інструменти для створення та обслуговування проектів")
]

category_ids = {}
for name, description in categories:
    cursor.execute(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        (name, description)
    )
    category_id = cursor.lastrowid
    category_ids[name] = category_id
    print(f"Додана категорія: {name}")

# Додавання товарів
products = [
    # Мікроконтролери
    ("Arduino Uno R3", "Класична плата Arduino на базі ATmega328P мікроконтролера. Відмінна для початківців.", 250.00, 20, "Мікроконтролери", "https://content.arduino.cc/assets/UNO-TH_front.jpg"),
    ("Arduino Nano", "Компактна версія Arduino Uno з такими ж можливостями.", 180.00, 15, "Мікроконтролери", "https://store-cdn.arduino.cc/uni/catalog/product/cache/1/image/1000x750/f8876a31b63532bbba4e781c30024a0a/a/0/a000005_front_4_1.jpg"),
    ("Raspberry Pi 4 Model B 4GB", "Одноплатний комп'ютер з 4-ядерним процесором та 4 ГБ оперативної пам'яті.", 1800.00, 10, "Мікроконтролери", "https://www.rasppishop.de/media/image/product/2358/lg/raspberry-pi-4-computer-model-b-4gb-ram.jpg"),
    ("ESP32 DevKit", "Потужний 32-бітний мікроконтролер з підтримкою WiFi та Bluetooth.", 220.00, 25, "Мікроконтролери", "https://cdn-reichelt.de/bilder/web/xxl_ws/A300/DEBO_ESP_WROOM_01.png"),
    ("STM32 Blue Pill", "Доступний мікроконтролер з ARM Cortex-M3 процесором.", 120.00, 30, "Мікроконтролери", "https://upload.wikimedia.org/wikipedia/commons/5/54/STM32_Blue_Pill.jpg"),
    ("Arduino Mega 2560", "Розширена версія Arduino з більшою кількістю вводів/виводів.", 420.00, 8, "Мікроконтролери", "https://store-cdn.arduino.cc/uni/catalog/product/cache/1/image/520x330/604a3538c15e081937dbfbd20aa60aad/a/0/a000067_featured_5.jpg"),
    ("PICO Raspberry Pi", "Компактний мікроконтролер від Raspberry Pi з RP2040 чіпом.", 150.00, 22, "Мікроконтролери", "https://www.raspberrypi.com/app/uploads/2020/12/Pico-Angle-1-1760x1080.jpg"),

    # Сенсори
    ("DHT22 датчик температури і вологості", "Прецизійний датчик для вимірювання температури та відносної вологості.", 120.00, 40, "Сенсори", "https://5.imimg.com/data5/SELLER/Default/2020/8/UI/KS/PV/33779608/dht22-am2302-digital-temperature-and-humidity-sensor-500x500.jpg"),
    ("HC-SR04 ультразвуковий датчик", "Датчик для вимірювання відстані до об'єктів.", 45.00, 50, "Сенсори", "https://5.imimg.com/data5/SELLER/Default/2021/11/IO/CP/ZE/24534328/hc-sr04-ultrasonic-sensor-for-arduino-500x500.jpg"),
    ("MPU6050 гіроскоп та акселерометр", "6-осьовий сенсор руху для відстеження положення.", 85.00, 30, "Сенсори", "https://www.hotmcu.com/thumbnail.asp?file=images/gy-521.jpg&maxx=350&maxy=0"),
    ("MQ-2 датчик газу", "Датчик для виявлення горючих газів та диму.", 65.00, 25, "Сенсори", "https://5.imimg.com/data5/SELLER/Default/2020/10/VO/DH/CT/25485952/mq2-gas-sensor-500x500.jpg"),
    ("BMP280 датчик атмосферного тиску", "Прецизійний датчик для вимірювання атмосферного тиску та температури.", 95.00, 20, "Сенсори", "https://content.instructables.com/FDI/0JFT/IRAVHJLK/FDI0JFTIRAVHJLK.jpg?auto=webp"),
    ("PIR датчик руху", "Інфрачервоний датчик для виявлення руху.", 60.00, 35, "Сенсори", "https://images-na.ssl-images-amazon.com/images/I/61MpqwrOvuL._AC_SL1100_.jpg"),
    ("Датчик освітленості LDR", "Фоторезистивний датчик для визначення рівня освітленості.", 25.00, 45, "Сенсори", "https://components101.com/sites/default/files/component_pin/LDR-Pinout.jpg"),

    # Двигуни і приводи
    ("SG90 сервопривод", "Мініатюрний сервопривод для легких проектів.", 55.00, 40, "Двигуни і приводи", "https://www.hotmcu.com/thumbnail.asp?file=images/rp0061-1.jpg&maxx=350&maxy=0"),
    ("MG996R сервопривод", "Потужний металевий сервопривод для проектів з навантаженням.", 120.00, 20, "Двигуни і приводи", "https://srituhobby.com/wp-content/uploads/2019/12/MG996R-Servo-Motor.jpg"),
    ("28BYJ-48 кроковий двигун з ULN2003", "Популярний кроковий двигун з драйвером для точного позиціонування.", 75.00, 30, "Двигуни і приводи", "https://www.hotmcu.com/thumbnail.asp?file=images/5v-stepper-motor-uln2003.jpg&maxx=350&maxy=0"),
    ("Nema 17 кроковий двигун", "Високоякісний кроковий двигун для 3D принтерів та ЧПУ.", 280.00, 15, "Двигуни і приводи", "https://5.imimg.com/data5/SELLER/Default/2020/9/RS/CF/SG/67534603/stepper-motor-nema-17-500x500.jpg"),
    ("L298N модуль керування двигунами", "Драйвер для керування двома двигунами постійного струму.", 85.00, 25, "Двигуни і приводи", "https://5.imimg.com/data5/OU/QI/CG/SELLER-50023807/l298n-motor-drive-module-500x500.jpg"),
    ("DC мотор з редуктором", "Мотор постійного струму з редуктором для роботів.", 110.00, 20, "Двигуни і приводи", "https://m.media-amazon.com/images/I/61bFgsbCuiL._AC_SL1500_.jpg"),
    ("Драйвер крокового двигуна A4988", "Драйвер для керування кроковими двигунами з мікрокроком.", 95.00, 30, "Двигуни і приводи", "https://a.pololu-files.com/picture/0J3360.1200.jpg?8e2799e19050491f29beeb79ce2493e4"),

    # Живлення
    ("Li-ion акумулятор 18650", "Перезаряджуваний літій-іонний акумулятор ємністю 3000mAh.", 150.00, 50, "Живлення", "https://m.media-amazon.com/images/I/61vLCRjfP1L._AC_SL1500_.jpg"),
    ("Повербанк 10000mAh", "Портативний повербанк для живлення робототехнічних проектів.", 450.00, 10, "Живлення", "https://m.media-amazon.com/images/I/71IrnTALilL._AC_SL1500_.jpg"),
    ("Модуль зарядки Li-ion TP4056", "Плата для зарядки 3.7В літієвих акумуляторів.", 35.00, 30, "Живлення", "https://5.imimg.com/data5/TB/AS/MY-1833510/micro-usb-5v-1a-lithium-battery-charging-board-charger-module-tp4056-500x500.jpg"),
    ("Блок живлення 5V 2A", "Адаптер для живлення проектів від мережі.", 120.00, 20, "Живлення", "https://m.media-amazon.com/images/I/41cHVpRyyPL._AC_SL1000_.jpg"),
    ("DC-DC понижуючий перетворювач LM2596", "Перетворювач для регулювання напруги.", 55.00, 40, "Живлення", "https://5.imimg.com/data5/XA/IE/MY-31966560/dc-dc-buck-converter-step-down-module-lm2596-power-supply-output-1-25v-35v-500x500.jpg"),
    ("Тримач для батарейок 4xAA", "Тримач з роз'ємом для 4-х батарейок типу AA.", 40.00, 25, "Живлення", "https://m.media-amazon.com/images/I/41hzPIVfYNL._AC_SL1000_.jpg"),
    ("Сонячна панель 5V 1W", "Мініатюрна сонячна панель для автономних проектів.", 180.00, 15, "Живлення", "https://m.media-amazon.com/images/I/61dDGDwYMkL._AC_SL1001_.jpg"),

    # Інструменти
    ("Паяльна станція", "Професійна паяльна станція з регулюванням температури.", 800.00, 5, "Інструменти", "https://m.media-amazon.com/images/I/61cGDpwsv+L._AC_SL1001_.jpg"),
    ("Набір викруток", "Комплект прецизійних викруток для електроніки.", 250.00, 15, "Інструменти", "https://m.media-amazon.com/images/I/61Gkkzu2BNL._AC_SL1000_.jpg"),
    ("Цифровий мультиметр", "Інструмент для вимірювання електричних параметрів.", 350.00, 10, "Інструменти", "https://m.media-amazon.com/images/I/515V7jO1BsL._AC_SL1000_.jpg"),
    ("Бокорізи", "Інструмент для перекушування дротів та виводів компонентів.", 120.00, 20, "Інструменти", "https://m.media-amazon.com/images/I/61S1X2qPgvL._AC_SL1500_.jpg"),
    ("Термоусадочна трубка (набір)", "Набір термоусадочних трубок різного діаметру.", 95.00, 25, "Інструменти", "https://m.media-amazon.com/images/I/81q7eSrBXBL._AC_SL1500_.jpg"),
    ("Макетна плата", "Плата для прототипування без пайки.", 85.00, 30, "Інструменти", "https://m.media-amazon.com/images/I/61iEZ8JnwML._AC_SL1001_.jpg"),
    ("Набір дротів для макетування", "Комплект дротів різних кольорів для з'єднання компонентів.", 65.00, 40, "Інструменти", "https://m.media-amazon.com/images/I/61H9yqfKkJL._AC_SL1000_.jpg")
]

for name, description, price, quantity, category_name, image_url in products:
    cursor.execute(
        "INSERT INTO products (name, description, price, quantity, category_id, image_url) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, price, quantity, category_ids[category_name], image_url)
    )
    print(f"Доданий товар: {name}")

# Отримання ID користувачів (клієнтів)
cursor.execute("SELECT id FROM users WHERE role = 'client'")
client_ids = [row[0] for row in cursor.fetchall()]

# Отримання ID товарів
cursor.execute("SELECT id FROM products")
product_ids = [row[0] for row in cursor.fetchall()]

# Створення замовлень
orders_count = 25  # Створимо 25 замовлень
for _ in range(orders_count):
    # Випадковий клієнт
    client_id = random.choice(client_ids)
    
    # Випадкова дата (за останні 60 днів)
    days_ago = random.randint(0, 60)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Випадковий статус
    status = random.choice(["Обробляється", "Підтверджено", "Відправлено", "Доставлено", "Скасовано"])
    
    # Створення замовлення
    cursor.execute(
        "INSERT INTO orders (user_id, order_date, status, total_price) VALUES (?, ?, ?, ?)",
        (client_id, order_date, status, 0)  # Загальну ціну оновимо після додавання товарів
    )
    order_id = cursor.lastrowid
    
    # Додавання випадкової кількості товарів до замовлення (1-5 товарів)
    items_count = random.randint(1, 5)
    selected_products = random.sample(product_ids, items_count)
    total_price = 0
    
    for product_id in selected_products:
        # Отримання інформації про товар
        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        product_price = cursor.fetchone()[0]
        
        # Випадкова кількість (1-3 одиниці)
        quantity = random.randint(1, 3)
        
        # Додавання товару до замовлення
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price_per_item) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, product_price)
        )
        
        total_price += product_price * quantity
    
    # Оновлення загальної ціни замовлення
    cursor.execute("UPDATE orders SET total_price = ? WHERE id = ?", (total_price, order_id))
    
    print(f"Створено замовлення #{order_id} на суму {total_price} грн")

# Додавання відгуків
reviews_count = 80  # Створимо 80 відгуків
for _ in range(reviews_count):
    # Випадковий клієнт
    client_id = random.choice(client_ids)
    
    # Випадковий товар
    product_id = random.choice(product_ids)
    
    # Випадкова оцінка (1-5)
    rating = random.randint(1, 5)
    
    # Випадкові коментарі
    comments = [
        "Дуже задоволений покупкою, рекомендую!",
        "Хороша якість за свою ціну.",
        "Працює, як очікувалося. Швидка доставка.",
        "Не зовсім те, що я очікував, але загалом непогано.",
        "Чудовий продукт, вже замовив ще один.",
        "Трохи дорого, але якість відповідає ціні.",
        "Було кілька проблем на початку, але все вирішилося.",
        "Ідеально підійшло для мого проекту.",
        "Не працювало спочатку, але техпідтримка допомогла вирішити проблему.",
        "Повністю задоволений, буду звертатися ще.",
        "",  # Порожній коментар (тільки оцінка)
    ]
    comment = random.choice(comments)
    
    # Випадкова дата (за останні 90 днів)
    days_ago = random.randint(0, 90)
    review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Додавання відгуку
    try:
        cursor.execute(
            "INSERT INTO reviews (user_id, product_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?)",
            (client_id, product_id, rating, comment, review_date)
        )
        print(f"Доданий відгук для товару #{product_id}")
    except sqlite3.IntegrityError:
        # Пропускаємо, якщо користувач вже залишив відгук для цього товару
        pass

# Додавання чат-повідомлень
# Отримання ID менеджерів
cursor.execute("SELECT id FROM users WHERE role = 'manager'")
manager_ids = [row[0] for row in cursor.fetchall()]

chat_messages_count = 100  # Створимо 100 повідомлень у чаті
for _ in range(chat_messages_count):
    # Випадковий клієнт
    client_id = random.choice(client_ids)
    
    # Випадковий менеджер (або None для повідомлень від клієнта)
    manager_id = random.choice(manager_ids) if random.random() > 0.5 else None
    
    # Визначення відправника
    sender_role = "manager" if manager_id else "client"
    
    # Випадкові повідомлення
    client_messages = [
        "Добрий день, коли очікувати поставку мого замовлення?",
        "Підкажіть, будь ласка, чи є у вас в наявності Arduino Mega?",
        "Дякую за відповідь!",
        "Я хотів би дізнатись більше про ваші сервоприводи.",
        "Чи можна повернути товар, якщо він мені не підійде?",
        "Коли буде знижка на мікроконтролери?",
        "У мене виникла проблема з модулем WiFi, що мені робити?",
        "Скільки часу триватиме доставка до Львова?",
        "Чи є у вас запчастини для 3D-принтерів?",
        "Мені потрібна консультація щодо вибору датчиків для мого проекту."
    ]
    
    manager_messages = [
        "Доброго дня! Чим можу допомогти?",
        "Так, звичайно. Ваше замовлення буде доставлено протягом 2-3 днів.",
        "Так, Arduino Mega є в наявності, можете оформити замовлення на сайті.",
        "Будь ласка! Якщо виникнуть ще питання, звертайтеся.",
        "У нас є широкий вибір сервоприводів. Що саме вас цікавить?",
        "Так, повернення можливе протягом 14 днів з моменту отримання товару.",
        "Знижки на мікроконтролери плануються наступного місяця, слідкуйте за оновленнями.",
        "Будь ласка, опишіть проблему детальніше, і ми спробуємо допомогти.",
        "Доставка до Львова зазвичай займає 1-2 дні при наявності товару на складі.",
        "Так, у нас є різні запчастини для 3D-принтерів. Які саме вас цікавлять?"
    ]
    
    message = random.choice(manager_messages) if sender_role == "manager" else random.choice(client_messages)
    
    # Випадкова дата (за останні 30 днів)
    days_ago = random.randint(0, 30)
    message_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    
    # Випадковий статус прочитання
    is_read = random.choice([0, 1])
    
    # Додавання повідомлення
    cursor.execute(
        "INSERT INTO chat_messages (user_id, manager_id, sender_role, message, timestamp, is_read) VALUES (?, ?, ?, ?, ?, ?)",
        (client_id, manager_id, sender_role, message, message_date, is_read)
    )
    print(f"Додане повідомлення в чаті")

# Збереження змін
conn.commit()
conn.close()

print("База даних успішно заповнена тестовими даними!")