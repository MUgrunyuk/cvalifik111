# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import datetime
import secrets
import jwt
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect('robotics_shop.db')
    cursor = conn.cursor()
    
    # Таблиця користувачів
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблиця категорій
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    ''')
    
    # Таблиця товарів
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        category_id INTEGER,
        image_url TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')
    
    # Таблиця замовлень
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Обробляється',
        total_price REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Таблиця деталей замовлення
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        price_per_item REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Таблиця відгуків
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        rating INTEGER NOT NULL,
        comment TEXT,
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Таблиця повідомлень чату
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        manager_id INTEGER,
        sender_role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (manager_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Виклик ініціалізації при запуску сервера
init_db()

# Функція для хешування паролів
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Ендпоінт для реєстрації
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'client')
    
    if not all([username, password, email]):
        return jsonify({"success": False, "message": "Всі поля повинні бути заповнені"}), 400
    
    # Перевірка ролі
    if role not in ['client', 'manager']:
        return jsonify({"success": False, "message": "Недійсна роль"}), 400
    
    hashed_password = hash_password(password)
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                      (username, hashed_password, email, role))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Користувач успішно зареєстрований"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Ім'я користувача або email вже використовуються"}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для авторизації
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({"success": False, "message": "Всі поля повинні бути заповнені"}), 400
    
    hashed_password = hash_password(password)
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, role FROM users WHERE username = ? AND password = ?",
                      (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_data = {"id": user[0], "username": user[1], "email": user[2], "role": user[3]}
            token = jwt.encode(
                {"user_id": user[0], "username": user[1], "role": user[3], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )
            
            return jsonify({"success": True, "token": token, "user": user_data}), 200
        else:
            return jsonify({"success": False, "message": "Неправильне ім'я користувача або пароль"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Функція для перевірки авторизації
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"success": False, "message": "Необхідний токен авторизації"}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            conn = sqlite3.connect('robotics_shop.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (data['user_id'],))
            current_user = cursor.fetchone()
            conn.close()
            
            if not current_user:
                return jsonify({"success": False, "message": "Недійсний токен"}), 401
        except:
            return jsonify({"success": False, "message": "Недійсний токен"}), 401
        
        return f(current_user, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# Ендпоінт для отримання списку категорій
@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        conn = sqlite3.connect('robotics_shop.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM categories")
        categories = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({"success": True, "categories": categories}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для отримання товарів
@app.route('/products', methods=['GET'])
def get_products():
    try:
        category_id = request.args.get('category_id')
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        
        conn = sqlite3.connect('robotics_shop.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE 1=1"
        params = []
        
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        
        if search_query:
            query += " AND (p.name LIKE ? OR p.description LIKE ?)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if min_price:
            query += " AND p.price >= ?"
            params.append(min_price)
        
        if max_price:
            query += " AND p.price <= ?"
            params.append(max_price)
        
        # Валідація сортування
        valid_sort_fields = ['name', 'price']
        valid_sort_orders = ['asc', 'desc']
        
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
        
        if sort_order not in valid_sort_orders:
            sort_order = 'asc'
        
        query += f" ORDER BY p.{sort_by} {sort_order}"
        
        cursor.execute(query, params)
        products = [dict(row) for row in cursor.fetchall()]
        
        # Додавання рейтингу для кожного товару
        for product in products:
            cursor.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(id) as reviews_count 
                FROM reviews 
                WHERE product_id = ?
            """, (product['id'],))
            
            rating_data = cursor.fetchone()
            product['avg_rating'] = rating_data['avg_rating'] if rating_data['avg_rating'] else 0
            product['reviews_count'] = rating_data['reviews_count']
        
        conn.close()
        
        return jsonify({"success": True, "products": products}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для отримання деталей товару
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = sqlite3.connect('robotics_shop.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.id = ?
        """, (product_id,))
        
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"success": False, "message": "Товар не знайдено"}), 404
        
        product_dict = dict(product)
        
        # Отримання відгуків
        cursor.execute("""
            SELECT r.*, u.username 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.product_id = ? 
            ORDER BY r.review_date DESC
        """, (product_id,))
        
        reviews = [dict(row) for row in cursor.fetchall()]
        
        # Отримання середнього рейтингу
        cursor.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(id) as reviews_count 
            FROM reviews 
            WHERE product_id = ?
        """, (product_id,))
        
        rating_data = cursor.fetchone()
        product_dict['avg_rating'] = rating_data['avg_rating'] if rating_data['avg_rating'] else 0
        product_dict['reviews_count'] = rating_data['reviews_count']
        product_dict['reviews'] = reviews
        
        conn.close()
        
        return jsonify({"success": True, "product": product_dict}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для створення замовлення
@app.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    user_id, username, role = current_user
    
    if role != 'client':
        return jsonify({"success": False, "message": "Тільки клієнти можуть створювати замовлення"}), 403
    
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({"success": False, "message": "Замовлення не може бути порожнім"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка наявності товарів та розрахунок загальної суми
        total_price = 0
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            cursor.execute("SELECT price, quantity FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                conn.close()
                return jsonify({"success": False, "message": f"Товар з ID {product_id} не знайдено"}), 404
            
            price, available_quantity = product
            
            if quantity > available_quantity:
                conn.close()
                return jsonify({"success": False, "message": f"Недостатня кількість товару (ID: {product_id})"}), 400
            
            total_price += price * quantity
        
        # Створення замовлення
        cursor.execute("""
            INSERT INTO orders (user_id, total_price) 
            VALUES (?, ?)
        """, (user_id, total_price))
        
        order_id = cursor.lastrowid
        
        # Додавання товарів до замовлення та оновлення кількості товарів
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            price = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_per_item) 
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            
            cursor.execute("""
                UPDATE products 
                SET quantity = quantity - ? 
                WHERE id = ?
            """, (quantity, product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Замовлення успішно створено", 
            "order_id": order_id,
            "total_price": total_price
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для отримання історії замовлень користувача
@app.route('/orders/history', methods=['GET'])
@token_required
def get_order_history(current_user):
    user_id, username, role = current_user
    
    if role not in ['client', 'manager']:
        return jsonify({"success": False, "message": "Доступ заборонено"}), 403
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Якщо користувач - клієнт, показуємо тільки його замовлення
        # Якщо менеджер - можемо показати всі замовлення або фільтрувати
        if role == 'client':
            cursor.execute("""
                SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC
            """, (user_id,))
        else:
            user_filter = request.args.get('user_id')
            status_filter = request.args.get('status')
            
            query = "SELECT o.*, u.username FROM orders o JOIN users u ON o.user_id = u.id WHERE 1=1"
            params = []
            
            if user_filter:
                query += " AND o.user_id = ?"
                params.append(user_filter)
            
            if status_filter:
                query += " AND o.status = ?"
                params.append(status_filter)
            
            query += " ORDER BY o.order_date DESC"
            cursor.execute(query, params)
        
        orders = [dict(row) for row in cursor.fetchall()]
        
        # Отримання товарів для кожного замовлення
        for order in orders:
            cursor.execute("""
                SELECT oi.*, p.name as product_name 
                FROM order_items oi 
                JOIN products p ON oi.product_id = p.id 
                WHERE oi.order_id = ?
            """, (order['id'],))
            
            order['items'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({"success": True, "orders": orders}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для додавання відгуку
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
@token_required
def add_review(current_user, product_id):
    user_id, username, role = current_user
    
    if role != 'client':
        return jsonify({"success": False, "message": "Тільки клієнти можуть додавати відгуки"}), 403
    
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"success": False, "message": "Рейтинг повинен бути числом від 1 до 5"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує товар
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Товар не знайдено"}), 404
        
        # Перевірка, чи користувач вже додавав відгук для цього товару
        cursor.execute("SELECT id FROM reviews WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing_review = cursor.fetchone()
        
        if existing_review:
            # Оновлення існуючого відгуку
            cursor.execute("""
                UPDATE reviews 
                SET rating = ?, comment = ?, review_date = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (rating, comment, existing_review[0]))
            message = "Відгук успішно оновлено"
        else:
            # Додавання нового відгуку
            cursor.execute("""
                INSERT INTO reviews (user_id, product_id, rating, comment) 
                VALUES (?, ?, ?, ?)
            """, (user_id, product_id, rating, comment))
            message = "Відгук успішно додано"
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": message}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінти для менеджерів (CRUD для товарів)
@app.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть додавати товари"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    quantity = data.get('quantity')
    category_id = data.get('category_id')
    image_url = data.get('image_url', '')
    
    if not all([name, price, quantity, category_id]):
        return jsonify({"success": False, "message": "Необхідні поля: name, price, quantity, category_id"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує категорія
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Категорія не знайдена"}), 404
        
        cursor.execute("""
            INSERT INTO products (name, description, price, quantity, category_id, image_url) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, description, price, quantity, category_id, image_url))
        
        product_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Товар успішно додано", 
            "product_id": product_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть оновлювати товари"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    quantity = data.get('quantity')
    category_id = data.get('category_id')
    image_url = data.get('image_url')
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує товар
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Товар не знайдено"}), 404
        
        # Оновлення тільки наданих полів
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
        
        if price is not None:
            update_fields.append("price = ?")
            params.append(price)
        
        if quantity is not None:
            update_fields.append("quantity = ?")
            params.append(quantity)
        
        if category_id is not None:
            # Перевірка, чи існує категорія
            cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({"success": False, "message": "Категорія не знайдена"}), 404
            
            update_fields.append("category_id = ?")
            params.append(category_id)
        
        if image_url is not None:
            update_fields.append("image_url = ?")
            params.append(image_url)
        
        if not update_fields:
            conn.close()
            return jsonify({"success": False, "message": "Немає даних для оновлення"}), 400
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
        params.append(product_id)
        
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Товар успішно оновлено"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть видаляти товари"}), 403
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує товар
        cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Товар не знайдено"}), 404
        
        # Видалення товару
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Товар успішно видалено"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінти для категорій (CRUD)
@app.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть додавати категорії"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"success": False, "message": "Ім'я категорії є обов'язковим"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        
        category_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Категорія успішно додана", 
            "category_id": category_id
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Категорія з таким ім'ям вже існує"}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

@app.route('/categories/<int:category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть оновлювати категорії"}), 403
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    
    if not name and description is None:
        return jsonify({"success": False, "message": "Немає даних для оновлення"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує категорія
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Категорія не знайдена"}), 404
        
        # Оновлення полів
        update_fields = []
        params = []
        
        if name:
            update_fields.append("name = ?")
            params.append(name)
        
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
        
        query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = ?"
        params.append(category_id)
        
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Категорія успішно оновлена"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Категорія з таким ім'ям вже існує"}), 409
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

@app.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть видаляти категорії"}), 403
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує категорія
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Категорія не знайдена"}), 404
        
        # Перевірка, чи є товари в цій категорії
        cursor.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,))
        products_count = cursor.fetchone()[0]
        
        if products_count > 0:
            conn.close()
            return jsonify({"success": False, "message": "Неможливо видалити категорію, яка містить товари"}), 400
        
        # Видалення категорії
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Категорія успішно видалена"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для оновлення статусу замовлення (для менеджерів)
@app.route('/orders/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(current_user, order_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть оновлювати статус замовлення"}), 403
    
    data = request.get_json()
    status = data.get('status')
    
    valid_statuses = ['Обробляється', 'Підтверджено', 'Відправлено', 'Доставлено', 'Скасовано']
    
    if not status or status not in valid_statuses:
        return jsonify({"success": False, "message": f"Недійсний статус. Допустимі значення: {', '.join(valid_statuses)}"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує замовлення
        cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "message": "Замовлення не знайдено"}), 404
        
        # Оновлення статусу
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Статус замовлення успішно оновлено"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінти для чату
@app.route('/chat/messages', methods=['GET'])
@token_required
def get_chat_messages(current_user):
    user_id, username, role = current_user
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role == 'client':
            # Клієнт бачить тільки свої повідомлення
            cursor.execute("""
                SELECT cm.*, u.username as user_username, m.username as manager_username 
                FROM chat_messages cm 
                LEFT JOIN users u ON cm.user_id = u.id 
                LEFT JOIN users m ON cm.manager_id = m.id 
                WHERE cm.user_id = ? 
                ORDER BY cm.timestamp ASC
            """, (user_id,))
        else:
            # Менеджер може бачити повідомлення від певного користувача або всі
            client_id = request.args.get('client_id')
            
            if client_id:
                cursor.execute("""
                    SELECT cm.*, u.username as user_username, m.username as manager_username 
                    FROM chat_messages cm 
                    LEFT JOIN users u ON cm.user_id = u.id 
                    LEFT JOIN users m ON cm.manager_id = m.id 
                    WHERE cm.user_id = ? 
                    ORDER BY cm.timestamp ASC
                """, (client_id,))
            else:
                # Отримуємо список унікальних клієнтів з повідомленнями
                cursor.execute("""
                    SELECT DISTINCT cm.user_id, u.username 
                    FROM chat_messages cm 
                    JOIN users u ON cm.user_id = u.id 
                    ORDER BY u.username
                """)
                clients = [dict(row) for row in cursor.fetchall()]
                
                return jsonify({"success": True, "clients": clients}), 200
        
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Позначаємо повідомлення як прочитані
        if messages and role == 'manager':
            client_id = request.args.get('client_id')
            if client_id:
                cursor.execute("""
                    UPDATE chat_messages 
                    SET is_read = 1 
                    WHERE user_id = ? AND sender_role = 'client' AND is_read = 0
                """, (client_id,))
                conn.commit()
        elif messages and role == 'client':
            cursor.execute("""
                UPDATE chat_messages 
                SET is_read = 1 
                WHERE user_id = ? AND sender_role = 'manager' AND is_read = 0
            """, (user_id,))
            conn.commit()
        
        conn.close()
        
        return jsonify({"success": True, "messages": messages}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

@app.route('/chat/messages', methods=['POST'])
@token_required
def send_chat_message(current_user):
    user_id, username, role = current_user
    
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({"success": False, "message": "Повідомлення не може бути порожнім"}), 400
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        if role == 'client':
            # Клієнт відправляє повідомлення
            cursor.execute("""
                INSERT INTO chat_messages (user_id, sender_role, message) 
                VALUES (?, ?, ?)
            """, (user_id, 'client', message))
        else:
            # Менеджер відправляє повідомлення клієнту
            client_id = data.get('client_id')
            
            if not client_id:
                conn.close()
                return jsonify({"success": False, "message": "ID клієнта не вказано"}), 400
            
            # Перевірка, чи існує користувач
            cursor.execute("SELECT id FROM users WHERE id = ? AND role = 'client'", (client_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({"success": False, "message": "Клієнт не знайдений"}), 404
            
            cursor.execute("""
                INSERT INTO chat_messages (user_id, manager_id, sender_role, message) 
                VALUES (?, ?, ?, ?)
            """, (client_id, user_id, 'manager', message))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Повідомлення успішно відправлено"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для оновлення профілю користувача
@app.route('/users/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    user_id, username, role = current_user
    
    data = request.get_json()
    new_username = data.get('username')
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        # Оновлення імені користувача
        if new_username and new_username != username:
            # Перевірка чи ім'я не зайняте
            cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({"success": False, "message": "Це ім'я користувача вже використовується"}), 409
            
            update_fields.append("username = ?")
            params.append(new_username)
        
        # Оновлення email
        if email:
            # Перевірка чи email не зайнятий
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
            if cursor.fetchone():
                conn.close()
                return jsonify({"success": False, "message": "Цей email вже використовується"}), 409
            
            update_fields.append("email = ?")
            params.append(email)
        
        # Зміна пароля
        if current_password and new_password:
            hashed_current = hash_password(current_password)
            
            # Перевірка поточного пароля
            cursor.execute("SELECT id FROM users WHERE id = ? AND password = ?", (user_id, hashed_current))
            if not cursor.fetchone():
                conn.close()
                return jsonify({"success": False, "message": "Неправильний поточний пароль"}), 401
            
            hashed_new = hash_password(new_password)
            update_fields.append("password = ?")
            params.append(hashed_new)
        
        if not update_fields:
            conn.close()
            return jsonify({"success": False, "message": "Немає даних для оновлення"}), 400
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        params.append(user_id)
        
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Профіль успішно оновлено"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

# Ендпоінт для видалення користувача (для менеджерів)
@app.route('/users/<int:target_user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, target_user_id):
    user_id, username, role = current_user
    
    if role != 'manager':
        return jsonify({"success": False, "message": "Тільки менеджери можуть видаляти користувачів"}), 403
    
    try:
        conn = sqlite3.connect('robotics_shop.db')
        cursor = conn.cursor()
        
        # Перевірка, чи існує користувач
        cursor.execute("SELECT role FROM users WHERE id = ?", (target_user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({"success": False, "message": "Користувач не знайдений"}), 404
        
        # Перевірка, чи користувач не є менеджером
        if user_data[0] == 'manager':
            conn.close()
            return jsonify({"success": False, "message": "Неможливо видалити менеджера"}), 403
        
        # Видалення користувача
        cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Користувач успішно видалений"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Помилка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
