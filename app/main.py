from typing import Annotated
from fastapi import FastAPI, Depends
# from sqlmodel import SQLModel

# from .core.dependecies import engine,oauth2_scheme
from .core.dependecies import oauth2_scheme
from app.api.router import router as api_router

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(api_router, prefix='/api')
# # STARTUP
# @app.on_event("startup") # type: ignore
# def on_startup():
#     create_db_and_tables()

# keeping this protected for now
@app.get("/")
async def root(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Hello World"}

