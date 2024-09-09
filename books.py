from typing import Optional

from fastapi import FastAPI
from enum import Enum
app=FastAPI()

BOOKS={
    'book_1': {'title':'Title1', 'author':'Author 1'},
    'book_2': {'title': 'Title2', 'author': 'Author 2'},
    'book_3': {'title': 'Title3', 'author': 'Author 3'},
    'book_4': {'title': 'Title4', 'author': 'Author 4'},
    'book_5': {'title': 'Title5', 'author': 'Author 5'},
    'book_6': {'title': 'Title6', 'author': 'Author 6'}
}

class DirectionName(str,Enum):
        north="North"
        south ="South"
        east="East"
        west="West"

@app.get("/")
async def read_all_books(skip_book: Optional[str]= None):
    if skip_book:
        newBooks= BOOKS.copy()
        del newBooks[skip_book]
        return newBooks
    else:
        return BOOKS

@app.get("/{book_name}")
async def read_book(book_name: str):
    return BOOKS[book_name]

@app.post("/")
async def create_book(book_title:str, book_author:str):
    current_book_id = 0
    if len(BOOKS)> 0 :
        for book in BOOKS:
            x= int (book.split('_')[-1])
            if x > current_book_id:
                    current_book_id=x
    BOOKS[f'book_{current_book_id+1}']= {'title':book_title, 'author':book_author}
    return BOOKS[f'book_{current_book_id+1}']

@app.put("/{book_name}")
async def update_book(book_name:str,book_title:str, book_author:str):
    book_information = {'title':book_title, 'author':book_author}
    BOOKS[book_name]=book_information
    return book_information

@app.get("/direction/{direction_name}")
async def get_direction(direction_name:DirectionName):
    if direction_name == DirectionName.north:
        return {"Direction": direction_name, "sub":"UP"}
    if direction_name == DirectionName.south:
        return {"Direction": direction_name, "sub": "DOWN"}
    if direction_name == DirectionName.west:
        return {"Direction": direction_name, "sub": "LEFT"}
    return {"Direction": direction_name, "sub": "RIGHT"}

@app.delete("/{book_name}")
async def book_delete(book_name:str):
    del BOOKS[book_name]
    return f'Book_{book_name} deleted.'

@app.get("/assignment/")
async def read_book_assignment(book_name:str):
    return BOOKS[book_name]

@app.delete ("/assignment/{book_name}")
async def delete_book_assignment(book_name:str):
    del BOOKS[book_name]
    return BOOKS

