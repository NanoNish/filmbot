from pydantic import BaseModel
from typing import List, Any


class Shot(BaseModel):
    description: str
    dialogues: List[str] = []
    camera_action: str = ""
    thumbnails: Any = None
    action: str = ""

class Shots(BaseModel):
    count: int
    shots: List[Shot]

class MainCharacter(BaseModel):
    name: str
    photo: Any = None
    dressing_style: str
    background: str

class Script(BaseModel):
    title: str
    additional_info: str = ""
    main_characters: List[MainCharacter]
    shots: List[Shot]
