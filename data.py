import random
import mysql.connector

def get_db_connection():
    # Connect to MySQL database
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="shopping"
    )

def create_products_table():
    # Create products table with required columns if it doesn't exist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(100),
            category VARCHAR(100),
            gender ENUM('men', 'women', 'unisex'),
            description TEXT,
            color VARCHAR(50),
            size ENUM('S', 'M', 'L', 'XL'),
            price DECIMAL(10, 2),
            image_url TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def insert_sample_products():
    # Insert 100 random sample products with price in INR
    conn = get_db_connection()
    cursor = conn.cursor()

    categories = ['T-Shirt', 'Shirt', 'Jeans', 'Jacket', 'Kurta', 'Hoodie', 'Sweater', 'Shorts', 'Chinos', 'Blazer',
                  'Saree', 'Lehenga', 'Skirt', 'Top', 'Dress', 'Salwar Kameez', 'Dungaree', 'Tracksuit', 'Sweatpants', 'Activewear']
    genders = ['men', 'women', 'unisex']
    sizes = ['S', 'M', 'L', 'XL']
    colors = ['Red', 'Blue', 'Black', 'White', 'Green', 'Grey', 'Yellow', 'Pink', 'Brown', 'Purple']
    brands = ['Nike', 'Louis Vuitton', 'Chanel', 'Gucci', 'Adidas', 'Hermès', 'Zara', 'Dior', 'H&M']
    descriptors = ['Pure Cotton', 'Relaxed Fit', 'Slim Fit', 'Printed', 'Classic', 'Modern', 'Stylish', 'Comfortable', 'Trendy', 'Basic']

    for _ in range(100):
        brand = random.choice(brands)
        descriptor = random.choice(descriptors)
        category = random.choice(categories)
        gender = random.choice(genders)
        size = random.choice(sizes)
        color = random.choice(colors)

        name = f"{brand} {descriptor} {category}"
        description = f"A {gender}'s {category.lower()} in {color}, {descriptor.lower()} style."
        price = round(random.uniform(299, 2999), 2)  # price in INR

        cursor.execute('''
            INSERT INTO products (name, brand, category, gender, description, color, size, price, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
        ''', (name, brand, category, gender, description, color, size, price))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_products_table()
    insert_sample_products()
