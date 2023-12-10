from datetime import datetime
from textwrap import wrap
from typing import Optional

from pydantic import BaseModel, model_validator, field_validator
from pydantic_core import PydanticCustomError

from models import PlayerMark


class StartGameSchema(BaseModel):
    player1: str
    player2: str

    @model_validator(mode="after")
    def check_player_names(self) -> "StartGameSchema":
        if self.player1 == self.player2:
            raise PydanticCustomError("names_clash", "Players should have different names")
        return self


class GameStatusSchema(BaseModel):
    class Config:
        # Set the default behavior for exclude_unset
        # this will exclude unset fields when exporting model to json
        #
        # for some reason, this thing is not working in pydantic v2.5 ¯\_(ツ)_/¯
        # only instance.model_dump(exclude_unset=True) can provide desired behavior
        exclude_unset = True

    id: int
    player1: str
    player2: str
    next_player: Optional[PlayerMark] = None
    board: list
    winner: Optional[str] = None
    status: str
    ended_at: Optional[datetime] = None

    @field_validator("player1")
    @classmethod
    def player1_name(cls, val: str):
        return f"{val} ({PlayerMark.x.value})"

    @field_validator("player2")
    @classmethod
    def player2_name(cls, val: str):
        return f"{val} ({PlayerMark.o.value})"

    @field_validator("board")
    @classmethod
    def format_board(cls, val: list):
        return wrap("".join(val), 3)


class NextTurnSchema(BaseModel):
    position: int

    @field_validator("position")
    @classmethod
    def check_range(cls, val: int):
        if not 1 <= val <= 9:
            raise PydanticCustomError("range_error", "'position' should be in range [1-9]")
        return val
