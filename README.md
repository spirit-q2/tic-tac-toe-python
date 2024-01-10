## tic-tac-toe-python
An API backend for Tic-Tac-Toe game

### Requirements
* docker

## How to run the application
1. Clone the repository
2. Run `docker-compose up --build -d` in the root directory

## How to run the tests
1. Run `docker-compose exec api-server pytest` in the root directory

## How to play the game

### 1. Start the server 
See above

### 2. To start the game
Send a **POST** request to `http://localhost:5000/games` with the following body:
```
{
    "player1": "Alice",
    "player2": "Bob"
}
```
example response:
```
{
    "id": "123",
    "player1": "Alice (x)",
    "player2": "Bob (o)",
    "next_player": "x",
    "board": [
        ["..."],
        ["..."],
        ["..."]
    ],
    "status": "in_progress",
    "winner": null
}
```
where 
* `id` is the game id (will be used in the subsequent requests),
* `player1` and `player2` are the names of the players (in parentheses are the symbols they use),
* `next_player` is the player who should make the next move,
* `board` is the current state of the board,
* `status` is the status of the game (can be `in_progress`, `draw` or `done`),
* and `winner` is the winner of the game (if any).
                                                        
### 3. To make a move
Send a **PATCH** request to `http://localhost:5000/games/<game_id>` with the following body:
```
{
    "position": 1
}
```
where `position` is the position on the board where the player wants to make a move
(from 1 to 9, starting from the top left corner).
Like in the following board:

| 1 | 2 | 3 |
| - | - | - |
| 4 | 5 | 6 |
| 7 | 8 | 9 |

**Note:** you don't have to specify the player in the request body, the server will figure it out.

Example response:
```
{
    "id": "123",
    "player1": "Alice (x)",
    "player2": "Bob (o)",
    "next_player": "o",
    "board": [
        ["x.."],
        ["..."],
        ["..."]
    ],
    "status": "in_progress",
    "winner": null
}
```

### 4. To get the current state of the game
Send a **GET** request to `http://localhost:5000/games/<game_id>`

### 5. To finish the game
Repeat [step 3](#3-to-make-a-move) until the game is finished.
That is, until one of the players wins or the game ends in a draw.

Example response for a finished game:
```
{
    "id": "123",
    "player1": "Alice (x)",
    "player2": "Bob (o)",
    "next_player": null,
    "board": [
        ["x.."],
        ["ox."],
        ["o.x"]
    ],
    "status": "done",
    "winner": "Alice"
    "ended_at": "2021-01-01T00:00:00Z"
}
```
