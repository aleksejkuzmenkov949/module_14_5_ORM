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

    # Добавление продуктов
    add_product(cursor, 'Product1', 'Описание для Product1', 100, 'photo1.png')
    add_product(cursor, 'Product2', 'Описание для Product2', 200, 'photo2.png')
    add_product(cursor, 'Product3', 'Описание для Product3', 300, 'photo3.png')
    add_product(cursor, 'Product4', 'Описание для Product4', 400, 'photo4.png')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()


def add_product(cursor, title, description, price, photo):
    cursor.execute('INSERT INTO Products (title, description, price, photo) VALUES (?, ?, ?, ?)',
                   (title, description, price, photo))

def get_all_products():
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        return [{"id": row[0], "title": row[1], "description": row[2], "price": row[3], "photo": row[4]} for row in
                products]
