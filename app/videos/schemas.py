import uuid

from typing import Dict
from pydantic import BaseModel, validator, root_validator
from .extractors import extract_video_id
from users.exceptions import InvalidUserIDException
from .exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException
from .models import Video


class VideoCreateSchema(BaseModel):
    url: str  # user generated
    title: str  # user generated
    user_id: uuid.UUID  # request.session user_id

    @validator("url")
    def validate_youtube_url(cls, v, values, **kwargs) -> str:
        video_id = extract_video_id(v)  # v = url

        if video_id is None:
            raise ValueError(f"{v} is not a valid YouTube URL")

        return v

    @root_validator
    def validate_data(cls, values) -> Dict[str, str]:
        url = values.get("url")
        title = values.get("title")

        if url is None:
            raise ValueError("A valid url is required.")

        user_id = values.get("user_id")
        video_obj = None

        extra_data = {}
        if title is not None:
            extra_data["title"] = title

        try:
            video_obj = Video.add_video(url, user_id, **extra_data)
        except InvalidYouTubeVideoURLException as e:
            raise ValueError(f"{url} is not a valid YouTube URL") from e
        except VideoAlreadyAddedException as e:
            raise ValueError(f"{url} has already been added to your account") from e
        except InvalidUserIDException as e:
            raise ValueError(
                "There's a problem with your account, please try again."
            ) from e

        except Exception as e:
            raise ValueError(
                "There's a problem with your account, please try again."
            ) from e

        if video_obj is None or not isinstance(video_obj, Video):
            raise ValueError("There's a problem with your account, please try again.")

        return video_obj.as_data()
