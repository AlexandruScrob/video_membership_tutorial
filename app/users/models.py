import uuid

from . import validators, security
from config import get_settings

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


settings = get_settings()


class User(Model):
    __keyspace__ = settings.keyspace
    email = columns.Text(primary_key=True)
    user_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    password = columns.Text()

    def __str__(self) -> str:
        return self.__repr()

    def __repr__(self) -> str:
        return f"User(email={self.email}, user_id={self.user_id})"

    def set_password(self, pw: str, commit: bool = False) -> bool:
        pw_hash = security.generate_hash(pw)
        self.password = pw_hash
        if commit:
            self.save()

        return True

    def verify_password(self, pw_str: str):
        pw_hash = self.password
        verified, _ = security.verify_hash(pw_hash, pw_str)
        return verified

    @staticmethod
    def create_user(email: str, password: str = None):
        q = User.objects.filter(email=email)
        if q.count() != 0:
            raise Exception("User already has account.")

        valid, msg, email = validators._validate_email(email)

        if not valid:
            raise Exception(f"Invalid email: {msg}")

        obj = User(email=email)
        obj.set_password(password)
        obj.save()
        return obj
