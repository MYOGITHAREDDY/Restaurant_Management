# 🍽️ Restaurant Management System

A full-stack restaurant management system developed using **Flask (Python)** and **MySQL**, designed to streamline online food ordering with features like customer/admin login, menu management, order tracking, payment options, and QR code table access.

---

## 🔥 Features

- 👥 Customer/Admin login with role-based redirection
- 📋 Dynamic menu display with images
- 🛒 Add-to-cart and update quantity
- 💳 Payment integration (Card/Cash)
- 🔒 OTP verification at checkout
- 📊 Admin dashboard with sales analytics filters (daily/monthly/yearly/range)
- ✅ Mark orders as completed
- 🧾 Order summary and success confirmation
- 📷 QR code access for tables (same QR for all, with table input field)

---

## 🖥️ Technologies Used

| Frontend   | Backend | Database | Others      |
|------------|---------|----------|-------------|
| HTML, CSS  | Flask   | MySQL    | Jinja2, Ngrok, QRCode |

---

## 📂 Folder Structure
restaurant_management/
│
├── static/
│ └── styles.css # Unified stylesheet
│
├── templates/
│ ├── login.html
│ ├── register.html
│ ├── menu.html
│ ├── cart.html
│ ├── checkout.html
│ ├── otp.html
│ ├── success.html
│ └── admin_panel.html
│
├── app.py # Main Flask application
├── generate_qr.py # QR code generator
├── database.sql # MySQL schema
├── README.md
└── requirements.txt

**Ask for Ngrok demo URL during interview or test locally at:
http://localhost:5000/**
