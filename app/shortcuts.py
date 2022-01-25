import config
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

settings = config.get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


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

    # a somwhat form of security to refresh cookies
    # for key in request.cookies.keys():
    #     response.delete_cookie(key)

    return response
    # return templates.TemplateResponse(template_name, ctx)
