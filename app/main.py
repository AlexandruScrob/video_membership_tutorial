import config
from fastapi import FastAPI


app = FastAPI()
settings = config.get_settings()


@app.get("/")
def homepage():
    return {"hello": "world"}
