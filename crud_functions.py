import sqlite3


def initiate_db():
    # Подключение к базе данных (или создание её, если она не существует)
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Создание таблицы Products, если она ещё не создана
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            photo TEXT  
        )
    ''')
    add_product('Product1', 'Описание для Product1', 100, 'photo1.png')
    add_product('Product2', 'Описание для Product2', 200, 'photo2.png')
    add_product('Product3', 'Описание для Product3', 300, 'photo3.png')
    add_product('Product4', 'Описание для Product4', 400, 'photo4.png')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()


def get_all_products():
    # Подключение к базе данных
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Получение всех записей из таблицы Products
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    # Закрытие соединения
    conn.close()
    return products


def add_product(title, description, price, photo_path):
    # Подключение к базе данных
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Вставка нового продукта в таблицу с сохранением пути к изображению
    cursor.execute('''
        INSERT INTO Products (title, description, price, photo)
        VALUES (?, ?, ?, ?)
    ''', (title, description, price, photo_path))  # photo_path сохраняется как текст

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()