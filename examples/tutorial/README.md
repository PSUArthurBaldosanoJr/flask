# Flaskr - REST API Extension

## Original Repository
https://github.com/pallets/flask  
The Flaskr tutorial app lives in `examples/tutorial` of the official Flask repository by the Pallets organization. It is a simple blog application that has been publicly available since 2010.

## My Fork
https://github.com/PSUArthurBaldosanoJr/flask  
Branch: `feature/posts-api`

---

## Original Application Overview
Flaskr is a minimal blog web application. It allows users to:
- Register and log in
- Create, edit, and delete blog posts via a web interface

It uses **Flask** as the web framework, **SQLite** as the database, and is structured using **Flask Blueprints** - one for authentication (`auth`) and one for blog functionality (`blog`).

---

## My Enhancement - Posts REST API
The original app had no REST API. All interactions were through HTML form submissions. I added a full **CRUD REST API** for blog posts, allowing external clients to interact with posts programmatically via JSON.

### New File Added
- `flaskr/posts_api.py` - New Blueprint registered at `/api/posts/`

### Modified File
- `flaskr/__init__.py` - Registered the new `posts_api` blueprint

### New Test File
- `tests/test_posts_api.py` - 33 unit tests with 98% coverage

---

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/posts/` | No | Get all posts |
| GET | `/api/posts/<id>` | No | Get a single post |
| POST | `/api/posts/` | Yes | Create a new post |
| PUT | `/api/posts/<id>` | Yes (owner only) | Update a post |
| DELETE | `/api/posts/<id>` | Yes (owner only) | Delete a post |

### HTTP Status Codes Used
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/empty title)
- `403` - Forbidden (not the post owner)
- `404` - Post not found
- `415` - Unsupported Media Type (non-JSON body)

---

## Dependencies
- Python 3.10+
- Flask 3.x
- pytest
- pytest-cov

---

## Installation

```bash
# 1. Clone the fork
git clone https://github.com/PSUArthurBaldosanoJr/flask.git
cd flask/examples/tutorial

# 2. Checkout the feature branch
git checkout feature/posts-api

# 3. Install the app
pip install -e ".[testing]"

# 4. Install pytest if not already installed
pip install pytest pytest-cov

# 5. Initialize the database
flask --app flaskr init-db

# 6. Run the app
flask --app flaskr run
```

---

## Running Tests

```bash
py -m pytest --cov=flaskr.posts_api tests/test_posts_api.py --cov-report=term-missing
```

Expected output: **33 passed, 98% coverage**

---

## Author
Arthur Baldosano - IT6 Final Drill  
PSU - 2026