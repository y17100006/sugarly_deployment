from datetime import datetime as _datetime
from typing import Any, Optional
from pydantic import PlainSerializer
from typing_extensions import Annotated

# A custom datetime type for Pydantic v2 that serializes into 'YYYY-MM-DD hh:mmpm'
CustomDatetime = Annotated[
    _datetime,
    PlainSerializer(
        lambda dt: dt.strftime("%Y-%m-%d %I:%M%p").lower() if dt else None, 
        return_type=str
    )
]
