import pytest
from flaskr.db import get_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login(client, username="test", password="test"):
    return client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )


def get_session_client(client, app):
    """Log in and return a client with an active session cookie."""
    with client.session_transaction() as sess:
        pass  # ensure session is initialised
    return client


# ---------------------------------------------------------------------------
# GET /api/posts/
# ---------------------------------------------------------------------------

class TestGetAllPosts:
    def test_get_all_posts_returns_200(self, client):
        response = client.get("/api/posts/")
        assert response.status_code == 200

    def test_get_all_posts_returns_list(self, client):
        response = client.get("/api/posts/")
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_all_posts_contains_seeded_post(self, client):
        response = client.get("/api/posts/")
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]["title"] == "test title"

    def test_get_all_posts_has_expected_fields(self, client):
        response = client.get("/api/posts/")
        post = response.get_json()[0]
        for field in ("id", "title", "body", "author_id", "author", "created"):
            assert field in post


# ---------------------------------------------------------------------------
# GET /api/posts/<id>
# ---------------------------------------------------------------------------

class TestGetSinglePost:
    def test_get_existing_post_returns_200(self, client):
        response = client.get("/api/posts/1")
        assert response.status_code == 200

    def test_get_existing_post_correct_data(self, client):
        response = client.get("/api/posts/1")
        data = response.get_json()
        assert data["title"] == "test title"
        assert data["body"] == "test\nbody"

    def test_get_nonexistent_post_returns_404(self, client):
        response = client.get("/api/posts/9999")
        assert response.status_code == 404

    def test_get_nonexistent_post_error_message(self, client):
        response = client.get("/api/posts/9999")
        data = response.get_json()
        assert "error" in data


# ---------------------------------------------------------------------------
# POST /api/posts/
# ---------------------------------------------------------------------------

class TestCreatePost:
    def test_create_post_unauthenticated_redirects(self, client):
        response = client.post("/api/posts/", json={"title": "New", "body": "Body"})
        # login_required redirects unauthenticated users
        assert response.status_code in (302, 401)

    def test_create_post_success(self, client, app):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post(
            "/api/posts/",
            json={"title": "New Post", "body": "New body content"},
        )
        assert response.status_code == 201

    def test_create_post_returns_created_data(self, client, app):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post(
            "/api/posts/",
            json={"title": "My Title", "body": "My body"},
        )
        data = response.get_json()
        assert data["title"] == "My Title"
        assert data["body"] == "My body"

    def test_create_post_missing_title_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", json={"body": "No title here"})
        assert response.status_code == 400

    def test_create_post_empty_title_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", json={"title": "   ", "body": "Body"})
        assert response.status_code == 400

    def test_create_post_no_json_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", data="not json", content_type="text/plain")
        assert response.status_code == 415

    def test_create_post_persisted_in_db(self, client, app):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        client.post("/api/posts/", json={"title": "DB Check", "body": "body"})
        with app.app_context():
            db = get_db()
            post = db.execute(
                "SELECT * FROM post WHERE title = ?", ("DB Check",)
            ).fetchone()
            assert post is not None

    def test_create_post_blank_body_is_allowed(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", json={"title": "Valid", "body": ""})
        assert response.status_code == 201
    def test_create_post_empty_json_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", json=None, content_type="application/json")
        assert response.status_code == 400

    def test_create_post_no_body_key(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.post("/api/posts/", json={"title": "No body key"})
        assert response.status_code == 201


# ---------------------------------------------------------------------------
# PUT /api/posts/<id>
# ---------------------------------------------------------------------------

class TestUpdatePost:
    def test_update_post_unauthenticated_redirects(self, client):
        response = client.put("/api/posts/1", json={"title": "Changed"})
        assert response.status_code in (302, 401)

    def test_update_post_success(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put(
            "/api/posts/1",
            json={"title": "Updated Title", "body": "Updated body"},
        )
        assert response.status_code == 200

    def test_update_post_returns_new_data(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/1", json={"title": "New Title"})
        data = response.get_json()
        assert data["title"] == "New Title"

    def test_update_nonexistent_post_returns_404(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/9999", json={"title": "Ghost"})
        assert response.status_code == 404

    def test_update_other_users_post_returns_403(self, client, app):
        # "other" user tries to edit post owned by "test"
        client.post("/auth/login", data={"username": "other", "password": "other"})
        response = client.put("/api/posts/1", json={"title": "Hijack"})
        assert response.status_code == 403

    def test_update_post_no_json_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/1", data="bad", content_type="text/plain")
        assert response.status_code == 415

    def test_update_post_empty_title_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/1", json={"title": "  "})
        assert response.status_code == 400

    def test_update_post_blank_title_in_json_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/1", json={"title": ""})
        assert response.status_code == 400
    def test_update_post_empty_json_returns_400(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.put("/api/posts/1", data="null", content_type="application/json")
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/posts/<id>
# ---------------------------------------------------------------------------

class TestDeletePost:
    def test_delete_post_unauthenticated_redirects(self, client):
        response = client.delete("/api/posts/1")
        assert response.status_code in (302, 401)

    def test_delete_post_success(self, client, app):
        # create a post to delete so seeded data stays intact for other tests
        client.post("/auth/login", data={"username": "test", "password": "test"})
        create_resp = client.post(
            "/api/posts/", json={"title": "To Delete", "body": "bye"}
        )
        new_id = create_resp.get_json()["id"]
        response = client.delete(f"/api/posts/{new_id}")
        assert response.status_code == 200

    def test_delete_post_returns_message(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        create_resp = client.post(
            "/api/posts/", json={"title": "Temp", "body": "temp"}
        )
        new_id = create_resp.get_json()["id"]
        response = client.delete(f"/api/posts/{new_id}")
        data = response.get_json()
        assert "message" in data

    def test_delete_nonexistent_post_returns_404(self, client):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        response = client.delete("/api/posts/9999")
        assert response.status_code == 404

    def test_delete_other_users_post_returns_403(self, client):
        client.post("/auth/login", data={"username": "other", "password": "other"})
        response = client.delete("/api/posts/1")
        assert response.status_code == 403

    def test_delete_actually_removes_from_db(self, client, app):
        client.post("/auth/login", data={"username": "test", "password": "test"})
        create_resp = client.post(
            "/api/posts/", json={"title": "Gone", "body": "soon gone"}
        )
        new_id = create_resp.get_json()["id"]
        client.delete(f"/api/posts/{new_id}")
        with app.app_context():
            db = get_db()
            post = db.execute(
                "SELECT * FROM post WHERE id = ?", (new_id,)
            ).fetchone()
            assert post is None
