from typing import Optional
from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy.orm import Session
import models
from database import engine,SessionLocal
from pydantic import BaseModel, Field
from routers.auth import get_current_user, get_user_exception,get_user_excetpion_unauthorized


router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()


class Todo (BaseModel):
    title: str
    description : Optional[str]
    priority: int = Field (gt=0, lt=6, description="The priority as between 1-5")
    complete: bool
    class Config:
        json_schema_extra = {
            "example": {
                "title": "We are in Summer",
                "description": "Now we are in summer edition",
                "priority": 4,
                "complete": False
            }
        }


@router.get("/")
async def read_all(db:SessionLocal = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).all()


@router.get("/user")
async  def read_all_by_user(user: dict = Depends(get_current_user), db:Session = Depends (get_db)):
    if user is None:
        raise get_user_exception()
    return (db.query(models.Todos)
            .filter(models.Todos.owner_id == user.get("id"))\
            .all())


@router.get("/{todo_id}")
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends (get_db)):
    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()
    if todo_model is not None:
        return todo_model
    raise http_exception()

@router.post("/")
async def create_todo(todo: Todo, db : Session = Depends (get_db), user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description=todo.description
    todo_model.priority=todo.priority
    todo_model.complete=todo.complete
    todo_model.owner_id=user.get("id")
    db.add(todo_model)
    db.commit()
    return {
        'status':201,
        'transaction': "Successful"
    }



@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, todo:Todo, db : Session = Depends (get_db), user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()
    todo_db = (db.query(models.Todos)
               .filter(models.Todos.owner_id == user.get("id"))
               .filter(models.Todos.id == todo_id))
    if todo_db is None:
        raise get_user_excetpion_unauthorized()
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return "Delete todo"


@router.put("/{todo_id}")
async def update_todo(todo_id: int, todo:Todo, db : Session = Depends (get_db), user: dict = Depends(get_current_user)):
    if user is None:
        raise get_user_exception()
    todo_model = (db.query(models.Todos)
                  .filter(models.Todos.owner_id == user.get('id'))
                  .filter(models.Todos.id == todo_id))
    if todo_model is None:
        raise http_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).one()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    todo_model.sqlmodel_update(todo_model)
    db.add(todo_model)
    db.commit()
   # db.refresh(todo_model)
    return "Update complete"


def http_exception(message:str = None):
    if message is None:
        message= "Todo not found"
    return HTTPException ( status_code=404, detail=message)
