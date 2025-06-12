# E-commerce-Sales-Chatbot

A rule-based conversational chatbot built with Flask that assists users in finding fashion products by interpreting natural language queries. This chatbot uses keyword extraction and rule-based logic to match user input with relevant products stored in a MySQL database.

---

## Project Summary

This project bridges the gap between user-friendly shopping experiences and backend-driven product discovery. Instead of manually navigating product categories, users can type queries like “Show me blue Nike hoodies under 3000” and get instant results.

While it doesn’t use AI or NLP models, the chatbot is capable of interpreting keywords using handcrafted logic, enabling attribute-based filtering such as color, size, brand, gender, and price. Chat history is stored per user session to allow for future personalization.

---

## Technologies Utilized

**Technologies Used to Build the System:**

- **Flask** – Micro web framework to handle routing, sessions, and backend logic
- **MySQL** – Relational database to store product data, user details, and chats
- **Bootstrap** – For building a responsive and visually appealing user interface
- **HTML/CSS/JavaScript** – Frontend technologies to enhance interactivity
- **Jinja2** – Template engine for rendering HTML pages dynamically
- **Werkzeug** – Secure password hashing and session management

---

## Key Features

- Secure login & signup with hashed password storage
- Chatbot interface to accept natural queries
- Extracts keywords like category, brand, size, price, etc.
- Queries the database and returns matching product results
- Stores real-time chat logs during session
- Works with multiple filtering criteria simultaneously
- Fully responsive layout using Bootstrap

## Project Structure

The project is organized as follows:
- templates/: This folder contains the HTML templates rendered using Flask's Jinja2 templating engine. It includes:
- login.html: Login page interface.
- register.html: User registration page.
- main.html: Main chatbot interface after login.
- app.py: This is the main Flask application that handles routing, session management, and rendering templates.
- data.py: A python script responsible for generating and inserting 100 synthetic, randomized product entries into the products table of the MySQL database.
- requirements.txt: Lists all the Python dependencies required to run the project.
- documents/: Contains PPT, Report of the work done

---

## Setup Instructions

### 1. Clone the Repository

    git clone https://github.com/your-username/ecommerce-chatbot.git
    cd ecommerce-chatbot

### 2. Install Required Dependencies
    pip install -r requirements.txt

### 3. Configure MySQL Database
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'database': 'shopping'

### 4. Create tables in SQL database
Table: users
- CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Table: products (You have to add your own entries....to make it automated run data.py after u create table)
- CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(100),
    size VARCHAR(20),
    color VARCHAR(50),
    gender VARCHAR(20),
    description TEXT,
    price DECIMAL(10, 2)
);

Table: chat_history
- CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
### 5. Running the application
    python app.py

All supporting documentation, including the detailed **project report** and **PowerPoint presentation**, is available in the `documents` folder.

