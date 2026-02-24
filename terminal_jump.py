import curses
import time
import random


def main(stdscr):
    # curses setup
    curses.curs_set(0)          # hide cursor
    stdscr.nodelay(True)        # non-blocking input
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()

    # main game tuning knobs
    PLAYER_CHAR = "O"
    OBSTACLE_CHARS = ["X", "A"]
    GROUND_OFFSET_FROM_BOTTOM = 2
    JUMP_VELOCITY = -2.0        # bigger magnitude = higher jump
    GRAVITY = 0.25               # tweak this if jumps feel floaty
    BASE_SPEED = 0.4            # how fast stuff scrolls
    SPEED_INCREASE_PER_SEC = 0.03
    SPAWN_INTERVAL_MIN = 0.6
    SPAWN_INTERVAL_MAX = 1.4
    FRAME_TIME = 0.02           # target-ish FPS

    # simple session high score (per run of the script)
    high_score = 0

    # community high score record (updated via pull requests)
    RECORD_SCORE = 418
    RECORD_HOLDER = 'Github: Nicknikac'

    def reset_game():
        max_y, max_x = stdscr.getmaxyx()
        ground_y = max_y - GROUND_OFFSET_FROM_BOTTOM
        player_x = max_x // 8
        player_y = float(ground_y)

        return {
            "max_y": max_y,
            "max_x": max_x,
            "ground_y": ground_y,
            "player_x": player_x,
            "player_y": player_y,
            "player_vy": 0.0,
            "obstacles": [],
            "last_spawn_time": time.time(),
            "next_spawn_delay": random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX),
            "start_time": time.time(),
            "score": 0,
            "game_over": False,
        }

    state = reset_game()

    while True:
        # deal with terminal resizes
        new_max_y, new_max_x = stdscr.getmaxyx()
        if new_max_y != state["max_y"] or new_max_x != state["max_x"]:
            # reset layout, keep your score/time
            saved_score = state["score"]
            saved_start = state["start_time"]
            state = reset_game()
            state["score"] = saved_score
            state["start_time"] = saved_start

        if not state["game_over"]:
            # main game loop
            t_now = time.time()
            elapsed = t_now - state["start_time"]

            # speed creeps up over time
            speed = BASE_SPEED + elapsed * SPEED_INCREASE_PER_SEC

            # input handling
            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key in (ord("q"), ord("Q")):
                break

            # jump (only if on the ground)
            on_ground = abs(state["player_y"] - state["ground_y"]) < 0.01
            if key in (ord(" "), curses.KEY_UP) and on_ground:
                state["player_vy"] = JUMP_VELOCITY

            # tiny physics step
            state["player_vy"] += GRAVITY
            state["player_y"] += state["player_vy"]

            # don't fall through the floor
            if state["player_y"] > state["ground_y"]:
                state["player_y"] = float(state["ground_y"])
                state["player_vy"] = 0.0

            # maybe spawn a new obstacle
            if t_now - state["last_spawn_time"] >= state["next_spawn_delay"]:
                state["last_spawn_time"] = t_now
                state["next_spawn_delay"] = random.uniform(
                    SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX
                )
                # toss a new obstacle on the right
                state["obstacles"].append(
                    {
                        "x": float(state["max_x"] - 2),
                        "y": state["ground_y"],
                        "char": random.choice(OBSTACLE_CHARS),
                    }
                )

            # slide obstacles left
            for obs in state["obstacles"]:
                obs["x"] -= speed

            # drop anything that left the screen
            state["obstacles"] = [o for o in state["obstacles"] if o["x"] >= 0]

            # super simple collision check
            player_x = state["player_x"]
            player_y_int = int(round(state["player_y"]))

            for obs in state["obstacles"]:
                ox = int(round(obs["x"]))
                oy = int(obs["y"])
                if ox == player_x and oy == player_y_int:
                    state["game_over"] = True
                    break

            # score is basically time survived
            state["score"] = int(elapsed * 10)

            # draw everything
            stdscr.erase()

            # ground line
            try:
                for x in range(state["max_x"]):
                    stdscr.addch(state["ground_y"], x, "_")
            except curses.error:
                pass

            # player
            try:
                stdscr.addch(player_y_int, player_x, PLAYER_CHAR)
            except curses.error:
                pass

            # obstacles
            for obs in state["obstacles"]:
                ox = int(round(obs["x"]))
                oy = int(obs["y"])
                if 0 <= oy < state["max_y"] and 0 <= ox < state["max_x"]:
                    try:
                        stdscr.addch(oy, ox, obs["char"])
                    except curses.error:
                        pass

            # score up in the corner
            score_text = f"Score: {state['score']}"
            try:
                stdscr.addstr(
                    0, max(0, state["max_x"] - len(score_text) - 1), score_text
                )
            except curses.error:
                pass

            # high score up on the left
            high_text = f"High: {high_score}"
            try:
                stdscr.addstr(0, 1, high_text)
            except curses.error:
                pass

            stdscr.refresh()
            time.sleep(FRAME_TIME)

        else:
            # game over screen
            stdscr.nodelay(False) 
            stdscr.erase()

            # bump high score if you beat it
            if state["score"] > high_score:
                high_score = state["score"]

            msg = "GAME OVER"
            sub = "Press R to restart or Q to quit"
            score_line = f"Score: {state['score']}   High: {high_score}"
            record_line = f"Highest Score {RECORD_SCORE} \"{RECORD_HOLDER}\""

            max_y, max_x = state["max_y"], state["max_x"]

            def center_text(row_offset, text):
                y = max_y // 2 + row_offset
                x = max(0, (max_x - len(text)) // 2)
                try:
                    stdscr.addstr(y, x, text)
                except curses.error:
                    pass

            center_text(-1, msg)
            center_text(0, score_line)
            center_text(2, record_line)
            center_text(4, sub)

            stdscr.refresh()

            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key in (ord("q"), ord("Q")):
                break
            elif key in (ord("r"), ord("R")):
                state = reset_game()
                stdscr.nodelay(True)
                continue

            # anything else: keep waiting
            continue


if __name__ == "__main__":
    curses.wrapper(main)

