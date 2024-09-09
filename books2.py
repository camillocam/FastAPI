from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status, Form, Header
from pydantic import BaseModel, Field
from uuid import UUID
from starlette.responses import JSONResponse


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


app = FastAPI()


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(description="Description of book", max_length=100, min_length=1)
    rating: int = Field(gt=-1, lt=101)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "eef28e06-2eae-4603-9193-46e73b580eee",
                "title": " Title Baby",
                "author": "Example Author !!",
                "description": "Description nice to you",
                "rating": 80
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(description="Description of book", max_length=100, min_length=1)


    class Config:
        json_schema_extra = {
            "example": {
                "id": "eef28e06-2eae-4603-9193-46e73b580eee",
                "title": " Title Baby",
                "author": "Example Author !!",
                "description": "Description nice to you"
            }
        }


BOOKS = []


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request, exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={"message": f" Hey why do you want {exception.books_to_return}"
                            f"books? You need to read more!"}
    )


@app.get("/book/{book_id}", )
async def read_book(book_id: UUID):
    for x in BOOKS:

        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.get("/book/rating/{book_id}", response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for x in BOOKS:
        if x.id == book_id:
            return x
    raise raise_item_cannot_be_found_exception()


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            BOOKS[counter - 1] = book
            return BOOKS[counter - 1]


@app.delete("/{book_id}")
async def delete_book(book_id: UUID):
    counter = 0
    for x in BOOKS:
        counter += 1
        if x.id == book_id:
            del BOOKS[counter - 1]
            return f'ID:{book_id} deleted'
    raise raise_item_cannot_be_found_exception()


@app.get("/")
async def read_all_books(books_to_return: Optional[int] = None):
    if books_to_return and books_to_return < 0:
        raise NegativeNumberException(books_to_return=books_to_return)
    if len(BOOKS) < 1:
        create_book_no_api()
    if books_to_return and len(BOOKS) >= books_to_return:
        new_books = []
        for x in BOOKS[0:books_to_return]:
            new_books.append(x)
        return new_books
    return BOOKS


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    return book


@app.get("/header")
async def read_header(random_header:Optional[str] = Header(None)):
    return {"Random-Header":random_header}


@app.post("/books/login")
async def book_login(book_id: int, username: Optional[str] = Header(None), password: Optional[str] = Header(None)):
    if username == "ABC" and password == "123":
        if book_id >-1  and book_id <= len(BOOKS):
            return BOOKS[book_id]
        else:
            raise raise_item_cannot_be_found_exception()
    else:
        return "Invalid User"


def raise_item_cannot_be_found_exception():
    raise HTTPException(status_code=404, detail="Book not found",
                        headers={"X-Header-Error": "Nothing to be seen at the UUID"})


def create_book_no_api():
    book_1 = Book(id="8a8b60ad-b69b-4ac5-96e6-b271fec3af3e",
                  title="Test 1",
                  author="Autore 1",
                  description="Descriptin 1",
                  rating=60)

    book_2 = Book(id="b44fb1d7-dbf8-432f-9587-3f7847af39c3",
                  title="Test Titolo 2",
                  author="Autore 2",
                  description="Descriptin 2",
                  rating=30)

    book_3 = Book(id="9aa2f610-6f2d-412d-b385-1285de688d95",
                  title="Test 3",
                  author="Autore 3",
                  description="Descriptin 3",
                  rating=80)

    book_4 = Book(id="e1053246-7369-4729-a216-a6382948c3b8",
                  title="Test 4",
                  author="Autore 4",
                  description="Descriptin 4",
                  rating=90)
    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)
