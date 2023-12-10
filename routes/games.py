import random
from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    request,
)
from flask_pydantic import validate
from sqlalchemy.orm.attributes import flag_modified

from app import db
from helpers import check_winner
from models import Game, PlayerMark, model_to_dict, GameStatus
from schemas import StartGameSchema, GameStatusSchema, NextTurnSchema

games_bp = Blueprint("games", __name__)


@games_bp.route("/games", methods=["GET"])
@validate(response_many=True)
def get_games():
    """Returns list of all games"""

    response = []
    for game in Game.query.all():
        response.append(GameStatusSchema(**model_to_dict(game)))

    return response


@games_bp.route("/games", methods=["POST"])
@validate()
def start_game(body: StartGameSchema):
    first_move = PlayerMark.x if random.choice([1, 2]) == 1 else PlayerMark.o

    game = Game(
        player1=body.player1,
        player2=body.player2,
        next_player=first_move,
    )
    db.session.add(game)
    db.session.commit()

    return GameStatusSchema(**model_to_dict(game))


@games_bp.route("/games/<game_id>", methods=["GET"])
@validate()
def get_game(game_id: int):
    """Returns game status"""

    game: Game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    return GameStatusSchema(**model_to_dict(game))


@games_bp.route("/games/<game_id>", methods=["PATCH"])
@validate()
def make_turn(game_id: int, body: NextTurnSchema):
    """Returns game status"""

    game: Game = db.session.get(Game, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game.status == GameStatus.done:
        return jsonify({"error": "Game is over already"}), 409

    if game.board[body.position - 1] != ".":
        return jsonify({"error": "Position already taken"}), 409

    game.board[body.position - 1] = game.next_player
    game.next_player = PlayerMark.x if game.next_player == PlayerMark.o else PlayerMark.o
    flag_modified(game, "board")

    winner = check_winner(game.board)
    if winner or not any([el == "." for el in game.board]):
        # and we have a WINNER! or a draw :)
        game.ended_at = datetime.utcnow()
        game.status = GameStatus.done
        if winner:
            game.winner = game.player1 if winner == PlayerMark.x else game.player2

    db.session.commit()

    return GameStatusSchema(**model_to_dict(game))
