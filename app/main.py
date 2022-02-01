import db, utils

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from cassandra.cqlengine.management import sync_table

from users.models import User
from users.schemas import UserSignupSchema, UserLoginSchema
from users.decorators import login_required
from users.exceptions import LoginRequiredException

from shortcuts import render, redirect

app = FastAPI()
DB_SESSION = None


@app.on_event("startup")
def on_startup():
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = "errors/404.html" if status_code == 404 else "errors/main.html"

    context = {"status_code": status_code}

    return render(request, template_name, context, status_code=status_code)


@app.exception_handler(LoginRequiredException)
async def login_exception_handler(request, exc):
    return redirect(f"/login?next={request.url}", remove_session=True)


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

    return redirect("/", cookies=data)


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

    return redirect("/login")


@app.get("/users")
def users_list_view():
    q = User.objects.all().limit(10)
    return list(q)


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return render(request, "home.html")


@app.get("/account", response_class=HTMLResponse)
@login_required
def homepage(request: Request):

    return render(request, "account.html")
