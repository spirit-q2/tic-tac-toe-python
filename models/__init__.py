import enum

from sqlalchemy import Column, Integer, DateTime, func, String, types
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

from app import db


class GameStatus(str, enum.Enum):
    in_progress = "in_progress"
    draw = "draw"
    done = "done"


class PlayerMark(str, enum.Enum):
    x = "x"  # player1
    o = "o"  # player2


class Game(db.Model):
    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=func.current_timestamp())
    ended_at = Column(DateTime)

    # an 'x' player
    player1 = Column(String(256))
    # an 'o' player
    player2 = Column(String(256))

    next_player = Column(types.Enum(PlayerMark))

    winner = Column(String(256))

    # comma separated list of moves
    board = Column(ARRAY(String(17)), default=["."] * 9)

    status = Column(
        types.Enum(GameStatus),
        nullable=False,
        index=True,
        default=GameStatus.in_progress,
    )


def model_to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}
