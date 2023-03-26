from pydantic import BaseModel


class From(BaseModel):
    id: int
    username: str


class Message(BaseModel):
    text: str
    from_: From

    class Config:
        fields = {
            'from_': 'from'
        }
