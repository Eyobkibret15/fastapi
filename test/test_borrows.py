import httpx
import pytest
import requests
from fastapi import status


@pytest.fixture(scope='function', autouse=True)
async def client():
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture(scope="function")
async def setup_data(request,client):
    # Create authors
    author_names = ['a1']
    for name in author_names:
        data = {"name": name}
        res = await client.post('http://localhost:8000/v1/authors', json=data)
        assert res.status_code == 200

    # Create readers
    reader_names = ['r1', 'r2']
    for name in reader_names:
        data = {"name": name}
        res = await client.post('http://localhost:8000/v1/readers', json=data)
        assert res.status_code == 200

    # Create books
    book_titles = ['b1', 'b2', 'b3']
    for i, title in enumerate(book_titles):
        data = {"author_id": i + 1, "title": title}
        res = await client.post('http://localhost:8000/v1/books', json=data)
        assert res.status_code == 200
    yield
    to_be_deleted = [1,2,3]
    for id in to_be_deleted:
        res = await client.delete(f"http://localhost:8000/v1/borrows/{id}")
        assert res.status_code == 200


@pytest.mark.usefixtures("setup_data")
class TestBorrowsPost:
    url = "http://localhost:8000/v1/borrows"

    @pytest.mark.asyncio
    async def test_add_borrow_new_book(self, client):
        data = {"reader_id": 1, "book_id": 1}
        response = await client.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['message'] == "Borrow added successfully"
        assert response.json()['borrow'] == data

    @pytest.mark.asyncio
    async def test_add_borrow_same_book_by_another_reader(self,client):
        data_setup = {"reader_id": 1, "book_id": 1}
        _ = await client.post(url=self.url, json=data_setup)
        data = {"reader_id": 2, "book_id": 1}
        response = await client.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()['detail'] == "The book is already borrowed by someone else"

    @pytest.mark.asyncio
    async def test_add_borrow_same_book_by_same_reader(self,client):
        data_setup = {"reader_id": 1, "book_id": 1}
        _ = await client.post(url=self.url, json=data_setup)
        data = {"reader_id": 1, "book_id": 1}
        response = requests.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['detail'] == "The book is already borrowed by the same reader"

    @pytest.mark.asyncio
    async def test_add_borrow_another_book_by_same_reader(self,client):
        data_setup = {"reader_id": 1, "book_id": 1}
        _ = await client.post(url=self.url, json=data_setup)
        data = {"reader_id": 1, "book_id": 2}
        response = requests.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['message'] == "Borrow added successfully"
        assert response.json()['borrow'] == data

    @pytest.mark.asyncio
    async def test_add_borrow_another_book_by_another_reader(self,client):
        data_setup = {"reader_id": 1, "book_id": 1}
        _ = await client.post(url=self.url, json=data_setup)
        data = {"reader_id": 2, "book_id": 3}
        response = requests.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['message'] == "Borrow added successfully"
        assert response.json()['borrow'] == data

    @pytest.mark.asyncio
    async def test_add_borrow_with_invalid_reader(self,client):
        data = {"reader_id": 999, "book_id": 1}
        response = requests.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == "Invalid reader_id"

    @pytest.mark.asyncio
    async def test_add_borrow_with_invalid_book(self,client):
        data = {"reader_id": 1, "book_id": 999}
        response = requests.post(url=self.url, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == "Invalid book_id"
