# Flaskr REST API Extension

## Original Repository
https://github.com/pallets/flask

## My Fork
https://github.com/PSUArthurBaldosanoJr/flask (branch: `feature/posts-api`)

## What I Added
A full REST API for blog posts using Flask Blueprints, registered at `/api/posts/`.

### Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/posts/ | Get all posts |
| GET | /api/posts/<id> | Get single post |
| POST | /api/posts/ | Create post (auth required) |
| PUT | /api/posts/<id> | Update post (owner only) |
| DELETE | /api/posts/<id> | Delete post (owner only) |

## How to Run
```bash
pip install -e ".[testing]"
flask --app flaskr init-db
flask --app flaskr run
```

## How to Test
```bash
py -m pytest --cov=flaskr.posts_api tests/test_posts_api.py --cov-report=term-missing
```