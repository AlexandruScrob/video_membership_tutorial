import db, utils

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from cassandra.cqlengine.management import sync_table

from users.models import User
from users.schemas import UserSignupSchema, UserLoginSchema

from shortcuts import render

app = FastAPI()
DB_SESSION = None


@app.on_event("startup")
def on_startup():
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)


@app.get("/login", response_class=HTMLResponse)
def login_get_view(request: Request):
    session_id = request.cookies.get("session_id")
    return render(request, "auth/login.html", {"logged_in": session_id is not None})


@app.post("/login", response_class=HTMLResponse)
def login_post_view(
    request: Request, email: str = Form(...), password: str = Form(...)
):

    raw_data = {"email": email, "password": password}
    data, errors = utils.valid_schema_data_or_error(raw_data, UserLoginSchema)

    context = {"data": data, "errors": errors}

    if len(errors) > 0:
        return render(request, "auth/login.html", context, status_code=400)

    return render(request, "auth/login.html", {"logged_in": True}, cookies=data)


@app.get("/signup", response_class=HTMLResponse)
def signup_get_view(request: Request):
    return render(request, "auth/signup.html")


@app.post("/signup", response_class=HTMLResponse)
def signup_post_view(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    raw_data = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm,
    }

    data, errors = utils.valid_schema_data_or_error(raw_data, UserSignupSchema)

    context = {"data": data, "errors": errors}

    if len(errors) > 0:
        return render(request, "auth/signup.html", context, status_code=400)

    return render(request, "auth/signup.html", context)


@app.get("/users")
def users_list_view():
    q = User.objects.all().limit(10)
    return list(q)
