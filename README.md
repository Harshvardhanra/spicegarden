# 🍛 Spice Garden — QR Restaurant System
### Django + Premium UI · Full Stack

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database & seed data
python manage.py migrate
python manage.py seed_data

# 4. Run server
python manage.py runserver
```

### 🌐 Open in browser:
| Page | URL |
|------|-----|
| 📱 Customer Menu | http://127.0.0.1:8000/menu/?table=5 |
| 🍳 Kitchen Display | http://127.0.0.1:8000/kitchen/ |
| 📊 Admin Dashboard | http://127.0.0.1:8000/dashboard/ |
| 📦 QR Code Generator | http://127.0.0.1:8000/qr-codes/ |
| ⚙️ Django Admin | http://127.0.0.1:8000/admin/ |

**Django Admin Login:** `admin` / `admin123`

---

## 📁 Project Structure

```
spicegarden/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                    ← Auto-created
│
├── spicegarden_project/
│   ├── settings.py
│   └── urls.py
│
└── restaurant/
    ├── models.py                 ← Category, MenuItem, Table, Order, OrderItem
    ├── views.py                  ← Page views + REST APIs
    ├── urls.py                   ← URL routing
    ├── admin.py                  ← Django admin config
    └── templates/restaurant/
        ├── menu.html             ← 📱 Customer QR menu (premium dark UI)
        ├── kitchen.html          ← 🍳 Kitchen order display
        ├── admin_dashboard.html  ← 📊 Restaurant analytics
        └── qr_codes.html         ← 📦 QR code generator
```

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/menu/` | Fetch full menu with categories |
| POST | `/api/orders/place/` | Place a new order |
| GET | `/api/orders/` | List active kitchen orders |
| POST | `/api/orders/<id>/status/` | Update order status |
| GET | `/api/tables/` | Get all table statuses |
| POST | `/api/generate-qr/<n>/` | Generate QR for table n |

### Place Order — POST `/api/orders/place/`
```json
{
  "table_number": 5,
  "items": [
    {"id": 1, "quantity": 2},
    {"id": 3, "quantity": 1}
  ],
  "special_instructions": "Less spicy please"
}
```

### Update Order Status — POST `/api/orders/<id>/status/`
```json
{ "status": "preparing" }
```
Status flow: `pending` → `preparing` → `ready` → `served` → `paid`

---

## 💳 Razorpay Payment Integration

Add your keys in `settings.py`:
```python
RAZORPAY_KEY_ID = 'rzp_test_xxxxxxxxxxxx'
RAZORPAY_KEY_SECRET = 'your_secret_here'
```

Install: `pip install razorpay`

---

## 🗄️ Database Models

```
Category       → name, slug, icon, sort_order
MenuItem       → category, name, description, price, emoji,
                 food_type, is_bestseller, is_new, spice_level
Table          → number, capacity, status, qr_code
Order          → order_id, table, status, payment_status,
                 subtotal, gst_amount, total_amount, special_instructions
OrderItem      → order, menu_item, item_name, item_price, quantity
```

---

## 🎨 Design System

- **Primary Font:** Playfair Display (headings — elegant serif)
- **Body Font:** DM Sans (UI — modern utility)
- **Gold Accent:** `#C9A84C`
- **Dark Background:** `#0D0D0D` (menu header)
- **Cream Surface:** `#F8F5F0` (dashboard, cards)

---

## ⚡ Production Deployment

```bash
# 1. Set in settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secret-production-key'

# 2. Collect static files
python manage.py collectstatic

# 3. Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spicegarden_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
    }
}

# 4. Run with Gunicorn
pip install gunicorn
gunicorn spicegarden_project.wsgi:application --bind 0.0.0.0:8000
```

---

*Built with Django 4.x · SQLite (dev) / PostgreSQL (prod) · No frontend framework required*
