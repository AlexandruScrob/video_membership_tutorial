import datetime

import config
from jose import jwt, ExpiredSignatureError
from users.models import User


settings = config.Settings()


def authenticate(email: str, password: str):
    try:
        # objects.allow_filtering -> for keys that are not primary keys
        user_obj = User.objects.get(email=email)

    except Exception as e:
        return

    if not user_obj.verify_password(password):
        return

    return user_obj


def login(user_obj, expires: int = settings.session_duration):
    raw_data = {
        "user_id": str(user_obj.user_id),
        "role": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires),
    }

    return jwt.encode(raw_data, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_user_id(token: str):
    data = []
    verified = False
    try:
        data = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        verified = True
    except ExpiredSignatureError as e:
        print(e, "Log out user")
    except:
        pass

    if "user_id" not in data:
        return
    return data, verified
