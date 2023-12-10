from textwrap import wrap
from typing import Any

import pytest
from app import app, db
from flask import url_for

from helpers import check_winner
from models import Game, PlayerMark, GameStatus


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_get_games_list(client):
    response = client.get(url_for("games.get_games"))

    assert response.status_code == 200


def test_start_game(client):
    data = {"player1": "Alice", "player2": "Bob"}
    response = client.post(url_for("games.start_game"), json=data)

    assert response.status_code == 200
    assert response.json["id"]
    assert response.json["player1"] == data["player1"] + " (x)"
    assert response.json["player2"] == data["player2"] + " (o)"


def test_get_game(client):
    game = Game(player1="Alice", player2="Bob", next_player=PlayerMark.x)
    db.session.add(game)
    db.session.commit()

    response = client.get(url_for("games.get_game", game_id=game.id))

    assert response.status_code == 200
    assert response.json["id"] == game.id
    assert response.json["player1"] == "Alice (x)"
    assert response.json["player2"] == "Bob (o)"
    assert response.json["next_player"] == "x"


def test_make_turn(client):
    game = Game(player1="Alice", player2="Bob", next_player=PlayerMark.x)
    db.session.add(game)
    db.session.commit()

    url = url_for("games.make_turn", game_id=game.id)

    data = {"position": 1}
    response = client.patch(url, json=data)

    assert response.status_code == 200
    assert response.json["board"] == ["x..", "...", "..."]

    # send the same position, expecting the error
    response = client.patch(url, json=data)
    assert response.status_code == 409

    # send another position, check for "o" to appear
    data["position"] = 5
    response = client.patch(url, json=data)
    assert response.status_code == 200
    assert response.json["board"] == ["x..", ".o.", "..."]


def test_play_to_win(client):
    game = Game(player1="Alice", player2="Bob", next_player=PlayerMark.x)  # start game from the "x"
    db.session.add(game)
    db.session.commit()

    url = url_for("games.make_turn", game_id=game.id)
    client.patch(url, json={"position": 5})  # x in the center
    client.patch(url, json={"position": 1})  # o in the top left
    client.patch(url, json={"position": 8})  # x in the middle bottom
    client.patch(url, json={"position": 2})  # o in the middle top
    response = client.patch(url, json={"position": 7})  # x in the bottom left
    """ at this moment, the board should look like this, let's check it
        o o .
        . x .
        x x .
    """
    assert response.json["board"] == ["oo.", ".x.", "xx."]

    # now the last move by "o"
    response = client.patch(url, json={"position": 3})  # o in the top right

    assert response.json["winner"] == "Bob"
    assert response.json["status"] == GameStatus.done
    assert response.json["ended_at"]

    # subsequent moves should trigger an error
    response = client.patch(url, json={"position": 3})
    assert response.status_code == 409


def test_play_to_draw(client):
    game = Game(player1="Alice", player2="Bob", next_player=PlayerMark.x)  # start game from the "x"
    db.session.add(game)
    db.session.commit()

    url = url_for("games.make_turn", game_id=game.id)
    client.patch(url, json={"position": 1})  # x -> top left
    client.patch(url, json={"position": 5})  # o -> center center
    client.patch(url, json={"position": 3})  # x -> top right
    client.patch(url, json={"position": 2})  # o -> top middle
    client.patch(url, json={"position": 8})  # x -> bottom center
    client.patch(url, json={"position": 4})  # o -> center left
    client.patch(url, json={"position": 6})  # x -> center right
    client.patch(url, json={"position": 9})  # o -> bottom right
    response = client.patch(url, json={"position": 7})  # x -> bottom left
    """ at this moment, the board should look like this, let's check it
        x o x
        o o x
        x x o
    """
    assert response.json["board"] == ["xox", "oox", "xxo"]

    assert response.json["winner"] is None
    assert response.json["status"] == GameStatus.draw
    assert response.json["ended_at"]

    # subsequent moves should trigger an error
    response = client.patch(url, json={"position": 3})
    assert response.status_code == 409


@pytest.mark.parametrize(
    "board,expected",
    [
        (wrap(".........", 1), None),
        (wrap("xxx......", 1), "x"),
        (wrap("...ooo...", 1), "o"),
        (wrap("......xxx", 1), "x"),
        (wrap("o..o..o..", 1), "o"),
        (wrap(".x..x..x.", 1), "x"),
        (wrap("..o..o..o", 1), "o"),
        (wrap("..x.x.x..", 1), "x"),  # "x" wins diagonally
        (wrap("oxoxoxoxo", 1), "o"),  # "o" wins diagonally
        (wrap("xoooxxoxo", 1), None),  # a draw
    ],
)
def test_check_winner(board: list, expected: Any):
    assert check_winner(board) == expected
