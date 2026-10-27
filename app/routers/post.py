from typing import List, Optional

from .. import models,schema,utils,oauth2
from fastapi import FastAPI, Response,status,APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["post"]
)

@router.get("/",response_model=List[ schema.Post])
def get_posts(db:Session = Depends(get_db),user_id = Depends(oauth2.get_current_user),limit:int = 10,skip:int = 0,search:Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts =cursor.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schema.Post)
def create_posts(post:schema.PostCreate,db:Session = Depends(get_db),user_id = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, contnet, published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id = user_id.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
# title str, content str,

@router.get("/{id}")
def get_post(id:int,db:Session = Depends(get_db),user_id = Depends(oauth2.get_current_user)):
    # cursor.execute('''SELECT * FROM posts WHERE id = %s''',(str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    result = db.query(models.Post).join()
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"post {id} was not found")
    return post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id:int,db:Session = Depends(get_db),user_id = Depends(oauth2.get_current_user)):
    # cursor.execute('''DELETE FROM posts WHERE id = %s RETURNING *''',(str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    posts = db.query(models.Post).filter(models.Post.id == id).first()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post eith {id} was not found")
    if posts.owner_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Authorized")
    db.delete(posts)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id:int,post:schema.PostCreate,db:Session = Depends(get_db),user_id = Depends(oauth2.get_current_user)):
    # cursor.execute('''UPDATE posts SET title = %s, contnet = %s, published = %s WHERE id = %s RETURNING *''',(post.title,post.content,post.published,str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    ex_post = post_query.first()
    if not ex_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post eith {id} was not found")
    if ex_post.owner_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    post_query.update(post.model_dump(),synchronize_session=False)
    db.commit()
    return post_query.first()


