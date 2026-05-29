from flask import Blueprint, jsonify, request, g
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint("posts_api", __name__, url_prefix="/api/posts")


def post_to_dict(post):
    """Convert a database row to a dictionary."""
    return {
        "id": post["id"],
        "title": post["title"],
        "body": post["body"],
        "author_id": post["author_id"],
        "author": post["username"],
        "created": post["created"].isoformat() if post["created"] else None,
    }


@bp.route("/", methods=["GET"])
def get_posts():
    """GET /api/posts/ — Return all posts."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return jsonify([post_to_dict(p) for p in posts]), 200


@bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """GET /api/posts/<id> — Return a single post."""
    db = get_db()
    post = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (post_id,),
    ).fetchone()

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    return jsonify(post_to_dict(post)), 200


@bp.route("/", methods=["POST"])
@login_required
def create_post():
    """POST /api/posts/ — Create a new post (requires login)."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    title = (data.get("title") or "").strip()
    body = data.get("body", "")  # pragma: no branch
    body = body.strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
        (title, body, g.user["id"]),
    )
    db.commit()

    new_id = cursor.lastrowid
    new_post = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (new_id,),
    ).fetchone()

    return jsonify(post_to_dict(new_post)), 201


@bp.route("/<int:post_id>", methods=["PUT"])
@login_required
def update_post(post_id):
    """PUT /api/posts/<id> — Update a post (owner only)."""
    db = get_db()
    post = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (post_id,),
    ).fetchone()

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    if post["author_id"] != g.user["id"]:
        return jsonify({"error": "Forbidden. You can only edit your own posts."}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    title = data.get("title", post["title"]).strip()
    body = data.get("body", post["body"]).strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400

    db.execute(
        "UPDATE post SET title = ?, body = ? WHERE id = ?",
        (title, body, post_id),
    )
    db.commit()

    updated = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (post_id,),
    ).fetchone()

    return jsonify(post_to_dict(updated)), 200


@bp.route("/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id):
    """DELETE /api/posts/<id> — Delete a post (owner only)."""
    db = get_db()
    post = db.execute(
        "SELECT id, author_id FROM post WHERE id = ?", (post_id,)
    ).fetchone()

    if post is None:
        return jsonify({"error": "Post not found."}), 404

    if post["author_id"] != g.user["id"]:
        return jsonify({"error": "Forbidden. You can only delete your own posts."}), 403

    db.execute("DELETE FROM post WHERE id = ?", (post_id,))
    db.commit()

    return jsonify({"message": f"Post {post_id} deleted successfully."}), 200
