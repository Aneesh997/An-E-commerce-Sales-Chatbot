from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
import re
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'database': 'shopping'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def extract_attributes(query):
    """Extract product attributes from natural language query"""
    attributes = defaultdict(list)
    
    # Predefined lists of possible values (case-insensitive matching)
    categories = ['t-shirt', 'shirt', 'jeans', 'jacket', 'kurta', 'hoodie', 'sweater', 
                 'shorts', 'chinos', 'blazer', 'saree', 'lehenga', 'skirt', 'top', 
                 'dress', 'salwar kameez', 'dungaree', 'tracksuit', 'sweatpants', 'activewear']
    genders = ['men', 'women', 'unisex', 'boys', 'girls']
    sizes = ['s', 'm', 'l', 'xl', 'xxl', 'xs']
    colors = ['red', 'blue', 'black', 'white', 'green', 'grey', 'yellow', 
             'pink', 'brown', 'purple', 'orange', 'maroon', 'navy', 'teal']
    brands = ['nike', 'louis vuitton', 'chanel', 'gucci', 'adidas', 
             'hermès', 'zara', 'dior', 'h&m', 'puma', 'levis', 'ralph lauren',
             'tommy hilfiger', 'calvin klein', 'versace']
    descriptors = ['pure cotton', 'relaxed fit', 'slim fit', 'printed', 
                  'classic', 'modern', 'stylish', 'comfortable', 'trendy', 'basic',
                  'regular fit', 'skinny', 'straight', 'bootcut', 'formal', 'casual']
    
    query_lower = query.lower()
    
    # Extract categories (handle multi-word categories first)
    for category in sorted(categories, key=len, reverse=True):
        if category in query_lower:
            attributes['category'].append(category.title())
            query_lower = query_lower.replace(category, '')  # Remove matched to avoid duplicates
    
    # Extract gender
    for gender in genders:
        if gender in query_lower:
            attributes['gender'].append(gender)
            query_lower = query_lower.replace(gender, '')
    
    # Extract size (handle both "size m" and standalone "m")
    size_pattern = re.compile(r'(?:size\s+)?([smlx]+)', re.IGNORECASE)
    size_matches = size_pattern.finditer(query_lower)
    for match in size_matches:
        size = match.group(1).lower()
        if size in sizes:
            attributes['size'].append(size.upper())
    
    # Extract colors
    for color in colors:
        if color in query_lower:
            attributes['color'].append(color.title())
            query_lower = query_lower.replace(color, '')
    
    # Extract brands (handle special characters and multi-word brands)
    for brand in sorted(brands, key=len, reverse=True):
        brand_pattern = re.compile(r'\b' + re.escape(brand) + r'\b', re.IGNORECASE)
        if brand_pattern.search(query_lower):
            attributes['brand'].append(brand.title())
            query_lower = brand_pattern.sub('', query_lower)
    
    # Extract descriptors (multi-word phrases first)
    for descriptor in sorted(descriptors, key=len, reverse=True):
        if descriptor in query_lower:
            attributes['descriptor'].append(descriptor.title())
            query_lower = query_lower.replace(descriptor, '')
    
    # Extract price range
    price_ranges = [
        (r'under\s*(?:rs\.?|₹)?\s*(\d+)', 'max_price'),
        (r'below\s*(?:rs\.?|₹)?\s*(\d+)', 'max_price'),
        (r'above\s*(?:rs\.?|₹)?\s*(\d+)', 'min_price'),
        (r'over\s*(?:rs\.?|₹)?\s*(\d+)', 'min_price'),
        (r'(?:rs\.?|₹)?\s*(\d+)\s*to\s*(?:rs\.?|₹)?\s*(\d+)', 'range'),
        (r'(?:rs\.?|₹)?\s*(\d+)\s*-\s*(?:rs\.?|₹)?\s*(\d+)', 'range')
    ]
    
    for pattern, price_type in price_ranges:
        matches = re.finditer(pattern, query_lower, re.IGNORECASE)
        for match in matches:
            if price_type == 'range':
                attributes['min_price'] = float(match.group(1))
                attributes['max_price'] = float(match.group(2))
            else:
                attributes[price_type] = float(match.group(1))
    
    # Extract remaining words as potential product names
    remaining_words = re.findall(r'\b[a-z]{3,}\b', query_lower)
    if remaining_words and not any(attributes.values()):
        attributes['name'] = remaining_words
    
    return dict(attributes)

def search_products(attributes):
    """Search products based on extracted attributes"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Base query
    sql = '''
        SELECT id, name, brand, color, size, price, category, gender, description 
        FROM products 
        WHERE 1=1
    '''
    params = []
    
    # Add conditions for each attribute
    if 'name' in attributes:
        name_conditions = []
        for name in attributes['name']:
            name_conditions.append('name LIKE %s')
            params.append(f'%{name}%')
        sql += f" AND ({' OR '.join(name_conditions)})"
    
    if 'brand' in attributes:
        brand_conditions = []
        for brand in attributes['brand']:
            brand_conditions.append('brand LIKE %s')
            params.append(f'%{brand}%')
        sql += f" AND ({' OR '.join(brand_conditions)})"
    
    if 'color' in attributes:
        color_conditions = []
        for color in attributes['color']:
            color_conditions.append('color LIKE %s')
            params.append(f'%{color}%')
        sql += f" AND ({' OR '.join(color_conditions)})"
    
    if 'size' in attributes:
        size_conditions = []
        for size in attributes['size']:
            size_conditions.append('size = %s')
            params.append(size)
        sql += f" AND ({' OR '.join(size_conditions)})"
    
    if 'category' in attributes:
        category_conditions = []
        for category in attributes['category']:
            category_conditions.append('category LIKE %s')
            params.append(f'%{category}%')
        sql += f" AND ({' OR '.join(category_conditions)})"
    
    if 'gender' in attributes:
        gender_conditions = []
        for gender in attributes['gender']:
            gender_conditions.append('gender = %s')
            params.append(gender)
        sql += f" AND ({' OR '.join(gender_conditions)})"
    
    if 'descriptor' in attributes:
        desc_conditions = []
        for desc in attributes['descriptor']:
            desc_conditions.append('description LIKE %s')
            params.append(f'%{desc}%')
        sql += f" AND ({' OR '.join(desc_conditions)})"
    
    if 'max_price' in attributes:
        sql += " AND price <= %s"
        params.append(attributes['max_price'])
    
    if 'min_price' in attributes:
        sql += " AND price >= %s"
        params.append(attributes['min_price'])
    
    # Limit results
    sql += " LIMIT 5"
    
    cursor.execute(sql, params)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Format price as INR and handle sizes
    for product in products:
        product['price'] = f"₹{product['price']:.2f}"
        if product['size']:
            product['size'] = product['size'].upper()
    
    return products

def generate_bot_response(attributes, products):
    """Generate a natural language response based on attributes and products"""
    if not attributes:
        return "I couldn't understand what you're looking for. Could you please provide more details?"
    
    # Start building response parts
    response_parts = []
    
    # Acknowledge the attributes found
    if any(attributes.values()):
        response_parts.append("I understand you're looking for:")
        
        if 'category' in attributes:
            response_parts.append(f"- Category: {', '.join(attributes['category'])}")
        if 'gender' in attributes:
            response_parts.append(f"- For: {', '.join(attributes['gender'])}")
        if 'color' in attributes:
            response_parts.append(f"- Color: {', '.join(attributes['color'])}")
        if 'size' in attributes:
            response_parts.append(f"- Size: {', '.join(attributes['size'])}")
        if 'brand' in attributes:
            response_parts.append(f"- Brand: {', '.join(attributes['brand'])}")
        if 'descriptor' in attributes:
            response_parts.append(f"- Features: {', '.join(attributes['descriptor'])}")
        if 'min_price' in attributes or 'max_price' in attributes:
            price_range = []
            if 'min_price' in attributes:
                price_range.append(f"above ₹{attributes['min_price']}")
            if 'max_price' in attributes:
                price_range.append(f"under ₹{attributes['max_price']}")
            response_parts.append(f"- Price: {' '.join(price_range)}")
    
    # Add product information
    if products:
        response_parts.append("\nHere are some options that match your criteria:")
    else:
        response_parts.append("\nI couldn't find exact matches for your criteria. Would you like to try a broader search?")
    
    # Join all parts with newlines
    return '\n'.join(response_parts)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                (name, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/main')
@login_required
def main():
    return render_template('main.html', name=session.get('user_name'))

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_id = session.get('user_id')
    user_msg = request.json.get('message')

    if not user_msg:
        return jsonify({'error': 'No message received'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Save user message
        cursor.execute('INSERT INTO chats (user_id, sender, message) VALUES (%s, %s, %s)',
                      (user_id, 'user', user_msg))
        
        # Extract attributes and search products
        attributes = extract_attributes(user_msg)
        products = search_products(attributes)
        
        # Generate bot reply
        bot_reply = generate_bot_response(attributes, products)
        
        # Save bot reply
        cursor.execute('INSERT INTO chats (user_id, sender, message) VALUES (%s, %s, %s)',
                      (user_id, 'bot', bot_reply))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        'bot_reply': bot_reply,
        'products': products,
        'attributes': attributes  # For debugging
    })

@app.route('/get_chat_history')
@login_required
def get_chat_history():
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT 
            DATE(created_at) as chat_date,
            sender,
            message,
            created_at
        FROM chats 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    raw_history = cursor.fetchall()
    cursor.close()
    conn.close()
    
    processed_history = {}
    for entry in raw_history:
        date_str = entry['chat_date'].strftime('%Y-%m-%d')
        if date_str not in processed_history:
            processed_history[date_str] = {
                'date': date_str,
                'conversations': []
            }
        processed_history[date_str]['conversations'].append({
            'sender': entry['sender'],
            'message': entry['message'],
            'time': entry['created_at'].strftime('%H:%M:%S')
        })
    
    result = sorted(
        processed_history.values(),
        key=lambda x: x['date'],
        reverse=True
    )
    
    return jsonify(result)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)