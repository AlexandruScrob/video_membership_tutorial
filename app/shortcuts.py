import config

from cassandra.cqlengine.query import DoesNotExist, MultipleObjectsReturned

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException


settings = config.get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def get_object_or_404(class_name, **kwargs):
    try:
        return class_name.objects.get(**kwargs)

    except DoesNotExist as exc:
        raise StarletteHTTPException(status_code=404) from exc
    except MultipleObjectsReturned as exc:
        raise StarletteHTTPException(status_code=400) from exc
    except Exception as exc:
        raise StarletteHTTPException(status_code=500) from exc


def redirect(path, cookies: dict = None, remove_session: bool = False):
    if cookies is None:
        cookies = {}

    response = RedirectResponse(path, status_code=302)

    for k, v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)

    if remove_session:
        response.set_cookie(key="session_ended", value=True, httponly=True)
        response.delete_cookie("session_id")
    return response


def render(
    request: Request, template_name, context=None, status_code: int = 200, cookies=None
):
    if context is None:
        context = {}

    if cookies is None:
        cookies = {}

    ctx = context.copy()
    ctx.update({"request": request})
    t = templates.get_template(template_name)
    html_str = t.render(ctx)
    response = HTMLResponse(html_str, status_code=status_code)

    if len(cookies.keys()) > 0:
        for k, v in cookies.items():
            # httponly adds a small level o security
            response.set_cookie(key=k, value=v, httponly=True)

    # a somewhat form of security to refresh cookies
    # for key in request.cookies.keys():
    #     response.delete_cookie(key)

    return response
    # return templates.TemplateResponse(template_name, ctx)
