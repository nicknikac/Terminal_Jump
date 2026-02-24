## Terminal Jump

Terminal Jump is a small Chrome dinosaur style runner for your terminal, written in a single Python file using curses.

## Requirements

You need Python 3.11 or newer.  
On Windows you also need windows-curses:

```bash
python -m pip install windows-curses
```

## Running

Open a terminal in this folder and run:

```bash
python terminal_jump.py
```

If you have multiple Python versions installed you can also run:

```bash
py -3.11 terminal_jump.py
```

## Controls

Space or Up Arrow to jump  
Q to quit  
R to restart after game over

## High score and screenshots

If you want to show off a run, take a screenshot of the game over screen and add it to the screenshots folder, then open a pull request.

Use a filename that includes your score and GitHub handle, for example `418-nicknikac.png`.

When someone beats the global record, the pull request can also update the record line in the code so the game shows the new name.

Right now the baked in record is:

Highest Score 418 "Github: Nicknikac"

