import requests


def test_add_authors(app):
    result = requests.post("http://127.0.0.1:8000/v1/authors", json={"name": "Arthur C. Clarke"})
    assert result.ok

    result = requests.post("http://127.0.0.1:8000/v1/authors", json={"name": "Stephen Hawking"})
    assert result.ok

    result = requests.get("http://127.0.0.1:8000/v1/authors")
    assert result.json() == {"authors": [{"id": 1, "name": "Arthur C. Clarke"}, {"id": 2, "name": "Stephen Hawking"}]}
