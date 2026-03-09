from typing import  List,Optional
from fastapi import  Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import Oauth2
from .. import model, schema 
from ..database import engine, get_db


router = APIRouter(
    prefix="/post",
    tags=["Posts"]
)

@router.get("/connection")
def test_connection(db: Session = Depends(get_db),user: int = Depends(Oauth2.get_current_user)):
    try:
        return {"message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection failed: {e}")



@router.get("/",response_model=List[schema.PostOut])
def get_posts(db: Session = Depends(get_db),limit: int = 10,skip: int = 0,search: Optional[str]= ""):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()

    result = db.query(model.Post,func.count(model.Vote.post_id).label("votes_count")).join(model.Vote, model.Vote.post_id == model.Post.id, isouter=True).group_by(model.Post.id)
    post= result.filter(model.Post.title.contains(search)).limit(limit).offset(skip).all()
    print(result)
    
    return post

@router.post("/",response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db),get_current_user: int =  Depends(Oauth2.get_current_user)):
    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", 
    #                (post.title, post.content, post.published))
    print(get_current_user.user_id)
    new_post = model.Post(owner_id=get_current_user.user_id, **post.model_dump())
    # new_post = cursor.fetchone()
    # conn.commit()
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post

@router.get("/{id}",response_model=schema.PostOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # req_post  = cursor.fetchone()
    req_post = db.query(model.Post , func.count(model.Vote.post_id).label("votes_count")).join(model.Vote, model.Vote.post_id == model.Post.id, isouter=True).group_by(model.Post.id).filter(model.Post.id == id).all()
    if not req_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    return  req_post


# @app.get("/posts/latest")
# def get_latest_post(response: Response):
#     cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
#     latest_post = cursor.fetchone()
#     if not latest_post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts available")
#     return latest_post

@router.put("/{id}",response_model=schema.Post)
def update_post(id: int, updated_post: schema.PostCreate,db: Session = Depends(get_db),get_current_user: schema.TokenData = Depends(Oauth2.get_current_user)):
    
    # cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *", 
    #                (updated_post.title, updated_post.content, updated_post.published, str(id)))
    # post = cursor.fetchone()
    
    # conn.commit()
    post_query = db.query(model.Post).filter(model.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    
    if post.owner_id != get_current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested update")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.delete("/{id}")
def delete_post(id: int, response: Response, db: Session = Depends(get_db),get_current_user: schema.TokenData = Depends(Oauth2.get_current_user)):
    # post = find_post(id)
    post = db.query(model.Post).filter(model.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    
    if post.owner_id != get_current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested deletion")
    db.delete(post)
    db.commit()
    return {"message": f"Post with id {id} deleted successfully"}


