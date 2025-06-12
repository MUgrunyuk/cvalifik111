# client.py
import streamlit as st
import requests
import json
from datetime import datetime

# Конфігурація API
API_URL = "http://localhost:5000"

# Кольорова гама (з прикладу на зображенні)
COLORS = {
    "mushroom": "#FEF2E4",  #  (світло-бежевий)
    "onion": "#FD974F",     #  (оранжевий)
    "red_pepper": "#000000", # Червоний перець
    "wood": "#805A3B",      # Деревина (коричневий)
    "text_dark": "#333333",  # Темний текст
    "text_light": "#FFFFFF", # Світлий текст
    "success": "#4CAF50",   # Зелений для успіху
    "error": "#F44336",     # Червоний для помилок
    "info": "#2196F3",      # Синій для інформації
    "warning": "#FF9800",   # Оранжевий для попереджень
    "light_bg": "#F9F9F9",  # Світлий фон для карток
    "dark_bg": "#333333"    # Темний фон для акцентів
}

# Функції для взаємодії з API
def register_user(username, password, email, role="client"):
    response = requests.post(
        f"{API_URL}/register",
        json={"username": username, "password": password, "email": email, "role": role}
    )
    return response.json()

def login_user(username, password):
    response = requests.post(
        f"{API_URL}/login",
        json={"username": username, "password": password}
    )
    return response.json()

def get_categories():
    try:
        response = requests.get(f"{API_URL}/categories")
        return response.json().get("categories", [])
    except:
        return []

def get_products(category_id=None, search="", sort_by="name", sort_order="asc", min_price=None, max_price=None):
    params = {}
    if category_id:
        params["category_id"] = category_id
    if search:
        params["search"] = search
    if sort_by:
        params["sort_by"] = sort_by
    if sort_order:
        params["sort_order"] = sort_order
    if min_price:
        params["min_price"] = min_price
    if max_price:
        params["max_price"] = max_price
    
    try:
        response = requests.get(f"{API_URL}/products", params=params)
        return response.json().get("products", [])
    except:
        return []

def get_product_details(product_id):
    try:
        response = requests.get(f"{API_URL}/products/{product_id}")
        return response.json().get("product", {})
    except:
        return {}

def create_order(items, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/orders",
        json={"items": items},
        headers=headers
    )
    return response.json()

def get_order_history(token, user_id=None, status=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if user_id:
        params["user_id"] = user_id
    if status:
        params["status"] = status
    
    response = requests.get(f"{API_URL}/orders/history", headers=headers, params=params)
    return response.json().get("orders", [])

def add_review(product_id, rating, comment, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/products/{product_id}/reviews",
        json={"rating": rating, "comment": comment},
        headers=headers
    )
    return response.json()

def add_product(name, description, price, quantity, category_id, image_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/products",
        json={
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
            "category_id": category_id,
            "image_url": image_url
        },
        headers=headers
    )
    return response.json()

def update_product(product_id, data, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{API_URL}/products/{product_id}",
        json=data,
        headers=headers
    )
    return response.json()

def delete_product(product_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/products/{product_id}", headers=headers)
    return response.json()

def add_category(name, description, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/categories",
        json={"name": name, "description": description},
        headers=headers
    )
    return response.json()

def update_category(category_id, name, description, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{API_URL}/categories/{category_id}",
        json={"name": name, "description": description},
        headers=headers
    )
    return response.json()

def delete_category(category_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/categories/{category_id}", headers=headers)
    return response.json()

def update_order_status(order_id, status, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{API_URL}/orders/{order_id}/status",
        json={"status": status},
        headers=headers
    )
    return response.json()

def get_chat_messages(token, client_id=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if client_id:
        params["client_id"] = client_id
    
    response = requests.get(f"{API_URL}/chat/messages", headers=headers, params=params)
    return response.json()

def send_chat_message(message, token, client_id=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    if client_id:
        data["client_id"] = client_id
    
    response = requests.post(f"{API_URL}/chat/messages", json=data, headers=headers)
    return response.json()

def update_profile(token, username=None, email=None, current_password=None, new_password=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if username:
        data["username"] = username
    if email:
        data["email"] = email
    if current_password and new_password:
        data["current_password"] = current_password
        data["new_password"] = new_password
    
    response = requests.put(f"{API_URL}/users/profile", json=data, headers=headers)
    return response.json()

def delete_user(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/users/{user_id}", headers=headers)
    return response.json()

# Налаштування Streamlit
st.set_page_config(
    page_title="Магазин робототехніки",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Функції стилізації
def apply_custom_style():
    st.markdown(f"""
    <style>
    .main {{
        background-color: {COLORS["mushroom"]};
        color: {COLORS["text_dark"]};
    }}
    .sidebar .sidebar-content {{
        background-color: {COLORS["wood"]};
        color: {COLORS["text_light"]};
    }}
    h1, h2, h3 {{
        color: {COLORS["text_dark"]};
    }}
    .stButton > button {{
        background-color: {COLORS["onion"]};
        color: {COLORS["text_dark"]};
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        width: 100%;
        height: 40px;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background-color: {COLORS["wood"]};
        color: {COLORS["text_light"]};
    }}
    .product-card {{
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    .product-price {{
        font-weight: bold;
        color: {COLORS["red_pepper"]};
    }}
    .category-badge {{
        background-color: {COLORS["onion"]};
        color: {COLORS["text_dark"]};
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8em;
    }}
    .success-box {{
        background-color: {COLORS["success"]};
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .error-box {{
        background-color: {COLORS["error"]};
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .info-box {{
        background-color: {COLORS["info"]};
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .warning-box {{
        background-color: {COLORS["warning"]};
        color: {COLORS["text_dark"]};
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .chat-client {{
        background-color: {COLORS["wood"]};
        color: {COLORS["text_light"]};
        padding: 10px;
        border-radius: 10px 10px 0 10px;
        margin: 5px 20px 5px 5px;
        display: inline-block;
    }}
    .chat-manager {{
        background-color: {COLORS["onion"]};
        color: {COLORS["text_dark"]};
        padding: 10px;
        border-radius: 10px 10px 10px 0;
        margin: 5px 5px 5px 20px;
        display: inline-block;
    }}
    .product-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        grid-gap: 20px;
    }}
    .card {{
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: transform 0.3s;
    }}
    .card:hover {{
        transform: translateY(-5px);
    }}
    .card-image {{
        width: 100%;
        height: 200px;
        object-fit: cover;
    }}
    .card-content {{
        padding: 15px;
    }}
    .btn-red {{
        background-color: {COLORS["red_pepper"]};
        color: white;
    }}
    .btn-red:hover {{
        background-color: #a50000;
        color: white;
    }}
    .btn-blue {{
        background-color: {COLORS["info"]};
        color: white;
    }}
    .btn-blue:hover {{
        background-color: #0b7dda;
        color: white;
    }}
    .btn-orange {{
        background-color: {COLORS["onion"]};
        color: {COLORS["text_dark"]};
    }}
    .btn-orange:hover {{
        background-color: #e58739;
        color: {COLORS["text_dark"]};
    }}
    .btn-green {{
        background-color: {COLORS["success"]};
        color: white;
    }}
    .btn-green:hover {{
        background-color: #3e8e41;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# Функція для рендерингу повідомлення про успіх
def success_message(message):
    st.markdown(f"""
    <div class="success-box">
        {message}
    </div>
    """, unsafe_allow_html=True)

# Функція для рендерингу повідомлення про помилку
def error_message(message):
    st.markdown(f"""
    <div class="error-box">
        {message}
    </div>
    """, unsafe_allow_html=True)

# Функція для рендерингу інформаційного повідомлення
def info_message(message):
    st.markdown(f"""
    <div class="info-box">
        {message}
    </div>
    """, unsafe_allow_html=True)

# Функція для рендерингу попередження
def warning_message(message):
    st.markdown(f"""
    <div class="warning-box">
        {message}
    </div>
    """, unsafe_allow_html=True)

# Функція для рендерингу картки товару
def render_product_card(product):
    st.markdown(f"""
    <div class="card">
        <img src="{product.get('image_url', 'https://via.placeholder.com/300x200?text=Немає+зображення')}" class="card-image" alt="{product['name']}">
        <div class="card-content">
            <h3>{product['name']}</h3>
            <span class="category-badge">{product.get('category_name', 'Без категорії')}</span>
            <p class="product-price">{product['price']} грн</p>
            <p>Доступно: {product['quantity']} шт.</p>
            <p>Рейтинг: {'⭐' * int(product.get('avg_rating', 0))}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Ініціалізація сесії
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.cart = []
    st.session_state.current_page = "home"
    st.session_state.selected_category = None
    st.session_state.search_query = ""
    st.session_state.selected_product = None
    st.session_state.sort_by = "name"
    st.session_state.sort_order = "asc"
    st.session_state.min_price = None
    st.session_state.max_price = None
    st.session_state.chat_with_client = None
    st.session_state.edit_product = None
    st.session_state.confirm_delete = {}
    st.session_state.message_sent = False
    st.session_state.product_added = False
    st.session_state.order_completed = False

# Функції навігації
def navigate_to(page):
    st.session_state.current_page = page

# Застосування стилів
apply_custom_style()

# Навігаційне меню в боковій панелі
with st.sidebar:
    st.title("🤖 Магазин робототехніки")
    
    # Меню для неавторизованих користувачів
    if not st.session_state.authenticated:
        if st.button("Головна", key="nav_home", on_click=navigate_to, args=("home",)):
            pass
        
        if st.button("Каталог", key="nav_catalog", on_click=navigate_to, args=("catalog",)):
            pass
        
        if st.button("Увійти", key="nav_login", on_click=navigate_to, args=("login",)):
            pass
        
        if st.button("Зареєструватися", key="nav_register", on_click=navigate_to, args=("register",)):
            pass
    
    # Меню для авторизованих користувачів
    else:
        st.markdown(f"### Вітаємо, {st.session_state.user['username']}!")
        st.markdown(f"Роль: **{st.session_state.user['role'].title()}**")
        
        if st.button("Головна", key="nav_home_auth", on_click=navigate_to, args=("home",)):
            pass
        
        if st.button("Каталог", key="nav_catalog_auth", on_click=navigate_to, args=("catalog",)):
            pass
        
        # Кошик та історія замовлень для клієнтів
        if st.session_state.user['role'] == 'client':
            cart_count = len(st.session_state.cart)
            if st.button(f"Кошик ({cart_count})", key="nav_cart", on_click=navigate_to, args=("cart",)):
                pass
            
            if st.button("Мої замовлення", key="nav_orders", on_click=navigate_to, args=("orders",)):
                pass
            
            if st.button("Чат з менеджером", key="nav_chat", on_click=navigate_to, args=("chat",)):
                pass
        
        # Меню для менеджерів
        elif st.session_state.user['role'] == 'manager':
            if st.button("Управління товарами", key="nav_manage_products", on_click=navigate_to, args=("manage_products",)):
                pass
            
            if st.button("Управління категоріями", key="nav_manage_categories", on_click=navigate_to, args=("manage_categories",)):
                pass
            
            if st.button("Управління замовленнями", key="nav_manage_orders", on_click=navigate_to, args=("manage_orders",)):
                pass
            
            if st.button("Чати з клієнтами", key="nav_chats", on_click=navigate_to, args=("manager_chats",)):
                pass
        
        # Профіль та вихід для всіх користувачів
        if st.button("Мій профіль", key="nav_profile", on_click=navigate_to, args=("profile",)):
            pass
        
        if st.button("Вийти", key="nav_logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.cart = []
            st.session_state.current_page = "home"
            st.cache_data.clear()

# Головні сторінки
if st.session_state.current_page == "home":
    st.title("Ласкаво просимо до магазину робототехніки!")
    
    st.markdown("""
    ### Наш магазин пропонує широкий вибір комплектуючих для робототехніки:
    * Мікроконтролери та плати розробника
    * Сенсори та датчики
    * Двигуни та приводи
    * Акумулятори та блоки живлення
    * Інструменти для монтажу
    """)
    
    # Відображення останніх доданих товарів
    st.subheader("Останні надходження")
    products = get_products(sort_by="id", sort_order="desc")[:4]
    
    # Відображення товарів у сітці
    col1, col2 = st.columns(2)
    for i, product in enumerate(products):
        with col1 if i % 2 == 0 else col2:
            render_product_card(product)
            if st.button("Деталі", key=f"home_details_{product['id']}", 
                          use_container_width=True):
                st.session_state.selected_product = product['id']
                navigate_to("product_details")
    
    st.markdown("""
    ### Чому саме ми?
    * Великий вибір компонентів
    * Швидка доставка
    * Консультації спеціалістів
    * Гарантія якості
    * Доступні ціни
    """)

elif st.session_state.current_page == "catalog":
    st.title("Каталог товарів")
    
    # Фільтрація та пошук
    with st.expander("Фільтри та сортування", expanded=True):
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Вибір категорії
            categories = [{"id": None, "name": "Всі категорії"}] + get_categories()
            category_names = [cat["name"] for cat in categories]
            selected_category_name = st.selectbox("Категорія", category_names)
            
            # Знаходимо id обраної категорії
            selected_category = None
            for cat in categories:
                if cat["name"] == selected_category_name:
                    selected_category = cat["id"]
            
            st.session_state.selected_category = selected_category
        
        with col2:
            # Сортування
            sort_options = {
                "name_asc": "Назва (А-Я)",
                "name_desc": "Назва (Я-А)",
                "price_asc": "Ціна (зростання)",
                "price_desc": "Ціна (спадання)"
            }
            
            selected_sort = st.selectbox("Сортування", list(sort_options.values()))
            
            # Знаходимо ключ обраного сортування
            for key, value in sort_options.items():
                if value == selected_sort:
                    sort_key = key
                    break
            
            sort_field, sort_direction = sort_key.split("_")
            st.session_state.sort_by = sort_field
            st.session_state.sort_order = sort_direction
        
        with col3:
            # Пошук
            search_query = st.text_input("Пошук товарів", value=st.session_state.search_query)
            st.session_state.search_query = search_query
        
        # Фільтр за ціною
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Мінімальна ціна", min_value=0, value=int(st.session_state.min_price) if st.session_state.min_price else 0)
            st.session_state.min_price = min_price if min_price > 0 else None
        
        with col2:
            max_price = st.number_input("Максимальна ціна", min_value=0, value=int(st.session_state.max_price) if st.session_state.max_price else 0)
            st.session_state.max_price = max_price if max_price > 0 else None
    
    # Отримання відфільтрованих товарів
    products = get_products(
        category_id=st.session_state.selected_category,
        search=st.session_state.search_query,
        sort_by=st.session_state.sort_by,
        sort_order=st.session_state.sort_order,
        min_price=st.session_state.min_price,
        max_price=st.session_state.max_price
    )
    
    if not products:
        info_message("Товарів не знайдено. Спробуйте змінити параметри пошуку.")
    else:
        st.subheader(f"Знайдено товарів: {len(products)}")
        
        # Відображення товарів у сітці
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                render_product_card(product)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Деталі", key=f"details_{product['id']}", 
                                  use_container_width=True):
                        st.session_state.selected_product = product['id']
                        navigate_to("product_details")
                
                with col2:
                    if (st.session_state.authenticated and 
                        st.session_state.user['role'] == 'client' and 
                        product['quantity'] > 0):
                        if st.button("У кошик", key=f"add_{product['id']}", 
                                      use_container_width=True):
                            # Перевірка, чи товар вже є в кошику
                            existing_item = None
                            for item in st.session_state.cart:
                                if item["product_id"] == product["id"]:
                                    existing_item = item
                                    break
                            
                            if existing_item:
                                # Оновлення кількості, якщо товар вже є в кошику
                                existing_item["quantity"] += 1
                                st.session_state.product_added = f"Оновлено кількість '{product['name']}' у кошику."
                            else:
                                # Додавання нового товару в кошик
                                st.session_state.cart.append({
                                    "product_id": product["id"],
                                    "name": product["name"],
                                    "price": product["price"],
                                    "quantity": 1,
                                    "image_url": product.get("image_url", "")
                                })
                                st.session_state.product_added = f"Товар '{product['name']}' додано до кошика."
                                
        # Відображення повідомлення про додання товару
        if st.session_state.product_added:
            success_message(st.session_state.product_added)
            st.session_state.product_added = False

elif st.session_state.current_page == "product_details":
    if st.session_state.selected_product:
        product = get_product_details(st.session_state.selected_product)
        
        if not product:
            error_message("Товар не знайдено")
            st.button("Повернутися до каталогу", on_click=navigate_to, args=("catalog",))
        else:
            # Кнопка повернення
            if st.button("← Назад до каталогу", on_click=navigate_to, args=("catalog",)):
                pass
            
            # Заголовок з назвою товару
            st.title(product["name"])
            
            # Зображення та основна інформація
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if product.get("image_url"):
                    st.image(product["image_url"], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=Немає+зображення", use_container_width=True)
            
            with col2:
                st.markdown(f"### Інформація про товар")
                st.markdown(f"**Категорія:** {product.get('category_name', 'Без категорії')}")
                st.markdown(f"**Ціна:** {product['price']} грн")
                st.markdown(f"**Доступна кількість:** {product['quantity']} шт.")
                
                # Рейтинг
                avg_rating = product.get('avg_rating', 0)
                reviews_count = product.get('reviews_count', 0)
                
                st.markdown(f"**Рейтинг:** {'⭐' * int(avg_rating)}{f' ({avg_rating:.1f}/5, {reviews_count} відгуків)' if reviews_count else 'Немає відгуків'}")
                
                # Кнопка додавання в кошик для клієнтів
                if st.session_state.authenticated and st.session_state.user['role'] == 'client' and product['quantity'] > 0:
                    quantity = st.number_input("Кількість", min_value=1, max_value=product['quantity'], value=1)
                    
                    if st.button("Додати до кошика", use_container_width=True):
                        # Перевірка, чи товар вже є в кошику
                        existing_item = None
                        for item in st.session_state.cart:
                            if item["product_id"] == product["id"]:
                                existing_item = item
                                break
                        
                        if existing_item:
                            # Оновлення кількості, якщо товар вже є в кошику
                            existing_item["quantity"] += quantity
                            success_message(f"Оновлено кількість '{product['name']}' у кошику.")
                        else:
                            # Додавання нового товару в кошик
                            st.session_state.cart.append({
                                "product_id": product["id"],
                                "name": product["name"],
                                "price": product["price"],
                                "quantity": quantity,
                                "image_url": product.get("image_url", "")
                            })
                            success_message(f"Товар '{product['name']}' додано до кошика.")
            
            # Опис товару
            st.markdown("### Опис")
            st.markdown(product.get("description", "Опис відсутній"))
            
            # Відгуки
            st.markdown("### Відгуки")
            
            reviews = product.get("reviews", [])
            
            # Форма для додавання відгуку (для авторизованих клієнтів)
            if st.session_state.authenticated and st.session_state.user['role'] == 'client':
                with st.expander("Додати відгук", expanded=False):
                    rating = st.slider("Оцінка", 1, 5, 5)
                    comment = st.text_area("Коментар")
                    
                    if st.button("Надіслати відгук", use_container_width=True):
                        result = add_review(product["id"], rating, comment, st.session_state.token)
                        
                        if result.get("success"):
                            success_message(result.get("message", "Відгук успішно додано"))
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            error_message(result.get("message", "Помилка при додаванні відгуку"))
            
            # Відображення відгуків
            if reviews:
                for review in reviews:
                    with st.container():
                        st.markdown(f"""
                        ##### {'⭐' * review['rating']} ({review['rating']}/5) - {review['username']}
                        *{datetime.fromisoformat(review['review_date'].replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')}*
                        
                        {review['comment'] if review['comment'] else 'Без коментаря'}
                        """)
                        st.markdown("---")
            else:
                st.info("Ще немає відгуків для цього товару.")

elif st.session_state.current_page == "login":
    st.title("Вхід у систему")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Ім'я користувача")
            password = st.text_input("Пароль", type="password")
            
            if st.button("Увійти", use_container_width=True):
                if username and password:
                    result = login_user(username, password)
                    
                    if result.get("success"):
                        st.session_state.authenticated = True
                        st.session_state.user = result.get("user")
                        st.session_state.token = result.get("token")
                        st.session_state.current_page = "home"
                        success_message("Успішний вхід у систему!")
                        st.rerun()
                    else:
                        error_message(result.get("message", "Помилка при вході в систему"))
                else:
                    error_message("Будь ласка, введіть ім'я користувача та пароль")
            
            st.markdown("Ще не маєте облікового запису?")
            if st.button("Зареєструватися", use_container_width=True):
                navigate_to("register")

elif st.session_state.current_page == "register":
    st.title("Реєстрація нового користувача")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Ім'я користувача")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            confirm_password = st.text_input("Підтвердіть пароль", type="password")
            
            role = st.selectbox("Роль", ["client", "manager"])
            
            if st.button("Зареєструватися", use_container_width=True):
                if not all([username, email, password, confirm_password]):
                    error_message("Всі поля повинні бути заповнені")
                elif password != confirm_password:
                    error_message("Паролі не співпадають")
                elif "@" not in email:
                    error_message("Введіть коректний email")
                else:
                    result = register_user(username, password, email, role)
                    
                    if result.get("success"):
                        success_message("Реєстрація успішна! Тепер ви можете увійти в систему.")
                        # Перенаправлення на сторінку входу
                        navigate_to("login")
                    else:
                        error_message(result.get("message", "Помилка при реєстрації"))
            
            st.markdown("Вже маєте обліковий запис?")
            if st.button("Увійти", use_container_width=True):
                navigate_to("login")

elif st.session_state.current_page == "cart":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'client':
        error_message("Доступ заборонено. Будь ласка, увійдіть як клієнт.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Кошик")
        
        if not st.session_state.cart:
            info_message("Ваш кошик порожній")
            if st.button("Перейти до каталогу", use_container_width=True):
                navigate_to("catalog")
        else:
            # Відображення товарів у кошику
            total_price = 0
            
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    st.markdown(f"### {item['name']}")
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    
                    with col1:
                        if item.get("image_url"):
                            st.image(item["image_url"], width=100)
                        else:
                            st.image("https://via.placeholder.com/100x100?text=Немає+зображення", width=100)
                    
                    with col2:
                        st.markdown(f"Ціна: {item['price']} грн за шт.")
                    
                    with col3:
                        new_quantity = st.number_input(f"Кількість", min_value=1, value=item['quantity'], key=f"cart_qty_{i}")
                        
                        if new_quantity != item['quantity']:
                            st.session_state.cart[i]['quantity'] = new_quantity
                        
                        item_total = item['price'] * st.session_state.cart[i]['quantity']
                        st.markdown(f"**Сума: {item_total} грн**")
                        
                        total_price += item_total
                    
                    with col4:
                        if st.button("Видалити", key=f"remove_{i}", use_container_width=True):
                            del st.session_state.cart[i]
                            st.rerun()
                    
                    st.markdown("---")
            
            # Підсумок замовлення
            st.markdown(f"### Загальна сума: {total_price} грн")
            
            # Оформлення замовлення
            if st.button("Оформити замовлення", use_container_width=True):
                # Підготовка даних для замовлення
                items = []
                for item in st.session_state.cart:
                    items.append({
                        "product_id": item["product_id"],
                        "quantity": item["quantity"]
                    })
                
                # Відправка замовлення
                result = create_order(items, st.session_state.token)
                
                if result.get("success"):
                    # Очищення кошика після успішного замовлення
                    st.session_state.cart = []
                    st.session_state.order_completed = True
                    success_message(f"Замовлення успішно оформлено! Номер замовлення: {result.get('order_id')}")
                    navigate_to("orders")
                else:
                    error_message(result.get("message", "Помилка при оформленні замовлення"))

elif st.session_state.current_page == "orders":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'client':
        error_message("Доступ заборонено. Будь ласка, увійдіть як клієнт.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Мої замовлення")
        
        # Повідомлення про успішне замовлення
        if st.session_state.order_completed:
            success_message("Ваше замовлення успішно оформлено!")
            st.session_state.order_completed = False
        
        # Отримання історії замовлень
        orders = get_order_history(st.session_state.token)
        
        if not orders:
            info_message("У вас ще немає замовлень")
        else:
            for order in orders:
                with st.expander(f"Замовлення #{order['id']} від {order['order_date'][:10]} - {order['status']}"):
                    st.markdown(f"**Статус:** {order['status']}")
                    st.markdown(f"**Загальна сума:** {order['total_price']} грн")
                    
                    # Відображення товарів у замовленні
                    st.markdown("#### Товари в замовленні:")
                    for item in order.get('items', []):
                        st.markdown(f"- {item['product_name']} x {item['quantity']} шт. ({item['price_per_item']} грн за шт.)")

elif st.session_state.current_page == "profile":
    # Перевірка автентифікації
    if not st.session_state.authenticated:
        error_message("Доступ заборонено. Будь ласка, увійдіть в систему.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Мій профіль")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Аватар користувача (заглушка)
            st.image("https://via.placeholder.com/150?text=User", width=150)
        
        with col2:
            # Відображення поточної інформації
            st.markdown(f"### {st.session_state.user['username']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Роль:** {st.session_state.user['role'].title()}")
        
        st.markdown("---")
        
        # Форма для оновлення профілю
        with st.expander("Оновити особисту інформацію", expanded=False):
            new_username = st.text_input("Нове ім'я користувача", value=st.session_state.user['username'])
            new_email = st.text_input("Новий Email", value=st.session_state.user['email'])
            
            if st.button("Оновити інформацію", use_container_width=True):
                update_data = {}
                
                # Перевірка змін в імені користувача та email
                if new_username != st.session_state.user['username']:
                    update_data["username"] = new_username
                
                if new_email != st.session_state.user['email']:
                    update_data["email"] = new_email
                
                # Оновлення профілю
                if update_data:
                    result = update_profile(
                        st.session_state.token,
                        username=update_data.get("username"),
                        email=update_data.get("email")
                    )
                    
                    if result.get("success"):
                        success_message("Профіль успішно оновлено")
                        
                        # Оновлення інформації в сесії
                        if "username" in update_data:
                            st.session_state.user['username'] = new_username
                        
                        if "email" in update_data:
                            st.session_state.user['email'] = new_email
                        
                        st.rerun()
                    else:
                        error_message(result.get("message", "Помилка при оновленні профілю"))
                else:
                    info_message("Немає змін для збереження")
        
        # Форма для зміни пароля
        with st.expander("Змінити пароль", expanded=False):
            current_password = st.text_input("Поточний пароль", type="password")
            new_password = st.text_input("Новий пароль", type="password")
            confirm_password = st.text_input("Підтвердіть новий пароль", type="password")
            
            if st.button("Змінити пароль", use_container_width=True):
                if not current_password:
                    error_message("Введіть поточний пароль")
                elif not new_password:
                    error_message("Введіть новий пароль")
                elif new_password != confirm_password:
                    error_message("Новий пароль та підтвердження не співпадають")
                else:
                    result = update_profile(
                        st.session_state.token,
                        current_password=current_password,
                        new_password=new_password
                    )
                    
                    if result.get("success"):
                        success_message("Пароль успішно змінено")
                    else:
                        error_message(result.get("message", "Помилка при зміні пароля"))

elif st.session_state.current_page == "chat":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'client':
        error_message("Доступ заборонено. Будь ласка, увійдіть як клієнт.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Чат з менеджером")
        
        # Отримання повідомлень
        chat_result = get_chat_messages(st.session_state.token)
        
        # Ініціалізуємо форму для повідомлень
        with st.form(key="chat_form"):
            message = st.text_area("Текст повідомлення", key="message_text")
            submit_button = st.form_submit_button(label="Відправити", use_container_width=True)
            
            if submit_button and message:
                result = send_chat_message(message, st.session_state.token)
                if result.get("success"):
                    st.rerun()
                else:
                    st.error(result.get("message", "Помилка при відправці повідомлення"))
        
        # Відображення повідомлень
        if chat_result.get("success"):
            messages = chat_result.get("messages", [])
            
            if not messages:
                info_message("У вас ще немає повідомлень. Напишіть першим!")
            
            else:
                st.markdown("### Історія повідомлень")
                for message in messages:
                    is_client = message['sender_role'] == 'client'
                    
                    # Стилізація повідомлень
                    if is_client:
                        st.markdown(f"""
                        <div style="text-align: right;">
                            <div class="chat-client">
                                <div><strong>Ви:</strong></div>
                                <div>{message['message']}</div>
                                <div><small>{message['timestamp'][:16].replace('T', ' ')}</small></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: left;">
                            <div class="chat-manager">
                                <div><strong>Менеджер:</strong></div>
                                <div>{message['message']}</div>
                                <div><small>{message['timestamp'][:16].replace('T', ' ')}</small></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Оновлення після відправки повідомлення
            if st.session_state.message_sent:
                st.session_state.message_sent = False

elif st.session_state.current_page == "manager_chats":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'manager':
        error_message("Доступ заборонено. Будь ласка, увійдіть як менеджер.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Чати з клієнтами")
        
        # Отримання списку клієнтів з повідомленнями
        chat_result = get_chat_messages(st.session_state.token)
        
        if chat_result.get("success") and "clients" in chat_result:
            clients = chat_result.get("clients", [])
            
            if not clients:
                info_message("Немає активних чатів з клієнтами")
            else:
                # Вибір клієнта
                client_options = ["Виберіть клієнта..."] + [client["username"] for client in clients]
                selected_client = st.selectbox("Клієнт", client_options)
                
                if selected_client != "Виберіть клієнта...":
                    # Знаходимо id обраного клієнта
                    client_id = None
                    for client in clients:
                        if client["username"] == selected_client:
                            client_id = client["user_id"]
                            break
                    
                    st.session_state.chat_with_client = client_id
                    
                    # Показуємо чат з обраним клієнтом
                    if client_id:
                        # Отримання повідомлень для обраного клієнта
                        chat_messages = get_chat_messages(st.session_state.token, client_id=client_id)
                        
                        # Форма для відправки повідомлення
                        with st.form(key=f"manager_chat_form_{client_id}"):
                            message = st.text_area("Текст повідомлення", key=f"manager_message_text_{client_id}")
                            submit_button = st.form_submit_button(label="Відправити", use_container_width=True)
                            
                            if submit_button and message:
                                result = send_chat_message(message, st.session_state.token, client_id=client_id)
                                if result.get("success"):
                                    st.rerun()
                                else:
                                    st.error(result.get("message", "Помилка при відправці повідомлення"))
                        
                        # Відображення повідомлень
                        if chat_messages.get("success"):
                            messages = chat_messages.get("messages", [])
                            
                            if messages:
                                st.markdown("### Історія повідомлень")
                                for message in messages:
                                    is_manager = message['sender_role'] == 'manager'
                                    
                                    # Стилізація повідомлень
                                    if is_manager:
                                        st.markdown(f"""
                                        <div style="text-align: right;">
                                            <div class="chat-manager">
                                                <div><strong>Ви:</strong></div>
                                                <div>{message['message']}</div>
                                                <div><small>{message['timestamp'][:16].replace('T', ' ')}</small></div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                        <div style="text-align: left;">
                                            <div class="chat-client">
                                                <div><strong>{selected_client}:</strong></div>
                                                <div>{message['message']}</div>
                                                <div><small>{message['timestamp'][:16].replace('T', ' ')}</small></div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)

elif st.session_state.current_page == "manage_products":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'manager':
        error_message("Доступ заборонено. Будь ласка, увійдіть як менеджер.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Управління товарами")
        
        # Створення нового товару або редагування існуючого
        tab1, tab2 = st.tabs(["Список товарів", "Додати новий товар"])
        
        with tab1:
            # Отримання всіх товарів
            products = get_products()
            
            if not products:
                info_message("Товари відсутні")
            else:
                # Фільтрація за категоріями
                categories = [{"id": None, "name": "Всі категорії"}] + get_categories()
                category_names = [cat["name"] for cat in categories]
                selected_filter = st.selectbox("Фільтр за категорією", category_names)
                
                # Фільтруємо товари за категорією
                filtered_products = products
                if selected_filter != "Всі категорії":
                    filtered_products = [p for p in products if p.get('category_name') == selected_filter]
                
                # Відображення товарів з можливістю редагування та видалення
                for product in filtered_products:
                    with st.expander(f"{product['name']} - {product['price']} грн"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**ID:** {product['id']}")
                            st.markdown(f"**Категорія:** {product.get('category_name', 'Без категорії')}")
                            st.markdown(f"**Ціна:** {product['price']} грн")
                            st.markdown(f"**Кількість на складі:** {product['quantity']} шт.")
                            st.markdown(f"**Опис:** {product.get('description', 'Опис відсутній')}")
                            
                            if product.get("image_url"):
                                st.image(product["image_url"], width=200)
                        
                        with col2:
                            # Кнопки редагування та видалення
                            st.button("Редагувати", key=f"edit_{product['id']}", use_container_width=True, 
                                      on_click=lambda p=product: setattr(st.session_state, 'edit_product', p) or 
                                                               navigate_to("edit_product"))
                            
                            # Кнопка видалення з підтвердженням
                            product_id = product['id']
                            if f"confirm_delete_{product_id}" not in st.session_state.confirm_delete:
                                st.session_state.confirm_delete[f"confirm_delete_{product_id}"] = False
                            
                            if st.session_state.confirm_delete[f"confirm_delete_{product_id}"]:
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Так", key=f"yes_delete_{product_id}", use_container_width=True):
                                        result = delete_product(product_id, st.session_state.token)
                                        
                                        if result.get("success"):
                                            success_message(result.get("message", "Товар успішно видалено"))
                                            st.session_state.confirm_delete[f"confirm_delete_{product_id}"] = False
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            error_message(result.get("message", "Помилка при видаленні товару"))
                                
                                with col2:
                                    if st.button("Ні", key=f"no_delete_{product_id}", use_container_width=True):
                                        st.session_state.confirm_delete[f"confirm_delete_{product_id}"] = False
                                        st.rerun()
                            else:
                                if st.button("Видалити", key=f"delete_{product_id}", use_container_width=True, 
                                             type="primary", help="Видалити товар"):
                                    st.session_state.confirm_delete[f"confirm_delete_{product_id}"] = True
                                    st.rerun()
        
        with tab2:
            st.subheader("Додати новий товар")
            
            # Форма для додавання нового товару
            name = st.text_input("Назва товару")
            
            # Вибір категорії
            categories = get_categories()
            category_options = [{"id": cat["id"], "name": cat["name"]} for cat in categories]
            
            if not category_options:
                warning_message("Немає доступних категорій. Спочатку створіть категорію.")
                category_id = None
            else:
                selected_category = st.selectbox(
                    "Категорія",
                    [cat["name"] for cat in category_options],
                    index=0
                )
                
                # Знаходимо id обраної категорії
                category_id = None
                for cat in category_options:
                    if cat["name"] == selected_category:
                        category_id = cat["id"]
                        break
            
            description = st.text_area("Опис товару")
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Ціна (грн)", min_value=0.01, step=0.01, value=1.00)
            
            with col2:
                quantity = st.number_input("Кількість на складі", min_value=0, step=1, value=1)
            
            image_url = st.text_input("URL зображення (опціонально)")
            
            if st.button("Додати товар", use_container_width=True):
                if not all([name, category_id, price, quantity]):
                    error_message("Заповніть всі обов'язкові поля")
                else:
                    result = add_product(name, description, price, quantity, category_id, image_url, st.session_state.token)
                    
                    if result.get("success"):
                        success_message(result.get("message", "Товар успішно додано"))
                        # Очищення форми
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        error_message(result.get("message", "Помилка при додаванні товару"))

elif st.session_state.current_page == "edit_product":
    # Перевірка автентифікації та наявності товару для редагування
    if not st.session_state.authenticated or st.session_state.user['role'] != 'manager':
        error_message("Доступ заборонено. Будь ласка, увійдіть як менеджер.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    elif not hasattr(st.session_state, "edit_product") or st.session_state.edit_product is None:
        error_message("Товар для редагування не вибрано")
        st.button("Повернутися до управління товарами", on_click=navigate_to, args=("manage_products",))
    else:
        product = st.session_state.edit_product
        
        st.title(f"Редагування товару: {product['name']}")
        
        # Кнопка повернення
        if st.button("← Назад до списку товарів", on_click=navigate_to, args=("manage_products",)):
            pass
        
        # Форма для редагування товару
        name = st.text_input("Назва товару", value=product['name'])
        
        # Вибір категорії
        categories = get_categories()
        category_options = [{"id": cat["id"], "name": cat["name"]} for cat in categories]
        
        if not category_options:
            warning_message("Немає доступних категорій. Спочатку створіть категорію.")
            category_id = None
        else:
            # Знаходимо індекс поточної категорії
            current_category_index = 0
            for i, cat in enumerate(category_options):
                if cat["id"] == product.get('category_id'):
                    current_category_index = i
                    break
            
            selected_category = st.selectbox(
                "Категорія",
                [cat["name"] for cat in category_options],
                index=current_category_index
            )
            
            # Знаходимо id обраної категорії
            category_id = None
            for cat in category_options:
                if cat["name"] == selected_category:
                    category_id = cat["id"]
                    break
        
        description = st.text_area("Опис товару", value=product.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Ціна (грн)", min_value=0.01, step=0.01, value=float(product['price']))
        
        with col2:
            quantity = st.number_input("Кількість на складі", min_value=0, step=1, value=int(product['quantity']))
        
        image_url = st.text_input("URL зображення (опціонально)", value=product.get('image_url', ''))
        
        if st.button("Зберегти зміни", use_container_width=True):
            if not all([name, category_id, price, quantity]):
                error_message("Заповніть всі обов'язкові поля")
            else:
                # Збираємо дані для оновлення
                update_data = {
                    "name": name,
                    "description": description,
                    "price": price,
                    "quantity": quantity,
                    "category_id": category_id,
                    "image_url": image_url
                }
                
                result = update_product(product['id'], update_data, st.session_state.token)
                
                if result.get("success"):
                    success_message(result.get("message", "Товар успішно оновлено"))
                    # Повернення до списку товарів
                    st.session_state.edit_product = None
                    navigate_to("manage_products")
                else:
                    error_message(result.get("message", "Помилка при оновленні товару"))

elif st.session_state.current_page == "manage_categories":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'manager':
        error_message("Доступ заборонено. Будь ласка, увійдіть як менеджер.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Управління категоріями")
        
        # Створення нової категорії або редагування існуючої
        tab1, tab2 = st.tabs(["Список категорій", "Додати нову категорію"])
        
        with tab1:
            # Отримання всіх категорій
            categories = get_categories()
            
            if not categories:
                info_message("Категорії відсутні")
            else:
                # Відображення категорій з можливістю редагування та видалення
                for category in categories:
                    with st.expander(f"{category['name']}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**ID:** {category['id']}")
                            st.markdown(f"**Опис:** {category.get('description', 'Опис відсутній')}")
                            
                            # Форма для редагування
                            new_name = st.text_input("Нова назва", value=category['name'], key=f"name_{category['id']}")
                            new_description = st.text_area("Новий опис", value=category.get('description', ''), key=f"desc_{category['id']}")
                        
                        with col2:
                            if st.button("Оновити", key=f"update_{category['id']}", use_container_width=True):
                                result = update_category(category['id'], new_name, new_description, st.session_state.token)
                                
                                if result.get("success"):
                                    success_message(result.get("message", "Категорія успішно оновлена"))
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    error_message(result.get("message", "Помилка при оновленні категорії"))
                            
                            # Кнопка видалення з підтвердженням
                            category_id = category['id']
                            if f"confirm_delete_cat_{category_id}" not in st.session_state.confirm_delete:
                                st.session_state.confirm_delete[f"confirm_delete_cat_{category_id}"] = False
                            
                            if st.session_state.confirm_delete[f"confirm_delete_cat_{category_id}"]:
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Так", key=f"yes_delete_cat_{category_id}", use_container_width=True):
                                        result = delete_category(category_id, st.session_state.token)
                                        
                                        if result.get("success"):
                                            success_message(result.get("message", "Категорія успішно видалена"))
                                            st.session_state.confirm_delete[f"confirm_delete_cat_{category_id}"] = False
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            error_message(result.get("message", "Помилка при видаленні категорії"))
                                
                                with col2:
                                    if st.button("Ні", key=f"no_delete_cat_{category_id}", use_container_width=True):
                                        st.session_state.confirm_delete[f"confirm_delete_cat_{category_id}"] = False
                                        st.rerun()
                            else:
                                if st.button("Видалити", key=f"delete_cat_{category_id}", use_container_width=True):
                                    st.session_state.confirm_delete[f"confirm_delete_cat_{category_id}"] = True
                                    st.rerun()
        
        with tab2:
            st.subheader("Додати нову категорію")
            
            # Форма для додавання нової категорії
            name = st.text_input("Назва категорії")
            description = st.text_area("Опис категорії")
            
            if st.button("Додати категорію", use_container_width=True):
                if not name:
                    error_message("Назва категорії обов'язкова")
                else:
                    result = add_category(name, description, st.session_state.token)
                    
                    if result.get("success"):
                        success_message(result.get("message", "Категорія успішно додана"))
                        # Очищення форми
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        error_message(result.get("message", "Помилка при додаванні категорії"))

elif st.session_state.current_page == "manage_orders":
    # Перевірка автентифікації
    if not st.session_state.authenticated or st.session_state.user['role'] != 'manager':
        error_message("Доступ заборонено. Будь ласка, увійдіть як менеджер.")
        st.button("Перейти на сторінку входу", on_click=navigate_to, args=("login",))
    else:
        st.title("Управління замовленнями")
        
        # Отримання всіх замовлень
        orders = get_order_history(st.session_state.token)
        
        if not orders:
            info_message("Замовлення відсутні")
        else:
            # Фільтрація за статусом
            status_options = ["Всі статуси", "Обробляється", "Підтверджено", "Відправлено", "Доставлено", "Скасовано"]
            selected_status = st.selectbox("Фільтр за статусом", status_options)
            
            filtered_orders = orders
            if selected_status != "Всі статуси":
                filtered_orders = [order for order in orders if order['status'] == selected_status]
            
            if not filtered_orders:
                info_message(f"Немає замовлень зі статусом '{selected_status}'")
            else:
                # Відображення замовлень у вигляді таблиці
                st.subheader(f"Знайдено замовлень: {len(filtered_orders)}")
                
                # Відображення замовлень
                for order in filtered_orders:
                    with st.expander(f"Замовлення #{order['id']} - {order.get('username', 'Користувач')} - {order['status']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Клієнт:** {order.get('username', 'Невідомий')}")
                            st.markdown(f"**Дата замовлення:** {order['order_date'][:10]}")
                            st.markdown(f"**Загальна сума:** {order['total_price']} грн")
                            
                            # Відображення товарів у замовленні
                            st.markdown("#### Товари в замовленні:")
                            for item in order.get('items', []):
                                st.markdown(f"- {item['product_name']} x {item['quantity']} шт. ({item['price_per_item']} грн за шт.)")
                        
                        with col2:
                            # Форма для оновлення статусу
                            new_status = st.selectbox(
                                "Статус замовлення",
                                ["Обробляється", "Підтверджено", "Відправлено", "Доставлено", "Скасовано"],
                                index=status_options.index(order['status']) - 1 if order['status'] in status_options[1:] else 0,
                                key=f"status_{order['id']}"
                            )
                            
                            if st.button("Оновити статус", key=f"update_status_{order['id']}", use_container_width=True):
                                result = update_order_status(order['id'], new_status, st.session_state.token)
                                
                                if result.get("success"):
                                    success_message(result.get("message", "Статус замовлення успішно оновлено"))
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    error_message(result.get("message", "Помилка при оновленні статусу замовлення"))

# Запуск додатку
if __name__ == "__main__":
    pass  # Streamlit автоматично запускає скрипт