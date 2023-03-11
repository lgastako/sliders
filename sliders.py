import fire
import json
import numpy as np
import streamlit as st

def random_grid():
    grid = np.arange(1, 10, dtype="object")
    grid[grid == 9] = None
    np.random.shuffle(grid)
    grid = grid.reshape(3, 3)
    return grid

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def to_numpy(s):
    return np.array(json.loads(s))

def adjacent(a, b):
    (y1, x1) = a
    (y2, x2) = b
    return abs(y1 - y2) + abs(x1 - x2) == 1

class Board:
    def __init__(self):
        self.grid = random_grid()

    def is_win_state(self):
        return np.array_equal(self.grid,
                              np.array([[1, 2, 3],
                                        [4, 5, 6],
                                        [7, 8, None]]))

    @classmethod
    def load(cls):
        try:
            with open("board.json", "r") as f:
                grid = to_numpy(f.read())
        except FileNotFoundError:
            grid = random_grid()
        board = cls()
        board.grid = np.array(grid)
        return board

    def as_json_string(self):
        return json.dumps(self.grid, cls=NumpyArrayEncoder)

    def as_ai_string(self):
        # render the board as text in rows and columns with a space for the empty square
        s = "\n"
        for i in range(3):
            for j in range(3):
                if self.grid[i, j] is None:
                    s += " "
                else:
                    s += str(self.grid[i, j])
                s += " "
            s += "\n"
        return s


    def open_pos(self):
        (y, x) = np.where(self.grid == None)
        return (y[0], x[0])

    def location_of_n(self, n: int):
        (y, x) = np.where(self.grid == n)
        return (y[0], x[0])

    def move(self, n: int, streamlit=False):
        if n not in range(1, 9):
            return (False, f"n of {n} not in [1-8].", self.as_json_string())
        (to_y, to_x) = self.open_pos()
        (from_y, from_x) = self.location_of_n(n)
        if adjacent((from_y, from_x), (to_y, to_x)):
            self.grid[to_y, to_x] = self.grid[from_y, from_x]
            self.grid[from_y, from_x] = None
            self.save()
            if streamlit:
                board.display(streamlit=streamlit)
            return (True, "", self.as_json_string())
        else:
            return (False, f"{n} is not adjacent to the empty spot", self.as_json_string())

    def save(self):
        with open("board.json", "w") as f:
            f.write(self.as_json_string())

    def display(self, win: bool = False, streamlit:bool = False):
        if streamlit:
            g = self.grid.copy()
            cols = st.columns(3)

            for i in range(3):
                for j in range(3):
                    with cols[j]:
                        st.write(g[i, j])

            if win:
                st.write("You won!")
                print("You won!")

class CLI:
    def new(self, streamlit=False):
        board = Board()
        if streamlit:
            board.display(streamlit=streamlit)
        board.save()
        print(board.as_json_string())

    def move(self, num, streamlit=False):
        board = Board.load()
        if board.is_win_state():
            board.display(win=True, streamlit=streamlit)
        else:
            (result, out) = board.move(num)
            if result:
                board.save()
            else:
                print("Invalid move.")

    def ai(self, streamlit=False):
        import pandas as pd
        board = Board()
        while board.is_win_state():
            board = Board()
        from langchain.agents import load_tools
        from langchain.agents import initialize_agent
        from langchain.agents import Tool
        from langchain.llms import OpenAI

        # set OPENAI_API_KEY in your environment
        llm = OpenAI(temperature=0)

        def format(n):
            if n is None:
                return " "
            else:
                return n

        table_container = None

        if streamlit:
            table_container = st.empty()

        def update_container():
            #df = pd.DataFrame(board.grid,
            #                  columns=["A", "B", "C"],
            #                  index=["1", "2", "3"])
            #table_container.dataframe(df)
            pass

        update_container()

        def get_board(*args, **kwargs):
            return board.as_ai_string()

        def get_board_as_json(*args, **kwargs):
            return board.as_json_string()

        def submit_feedback(feedback):
            # TODO: send feedback to a database
            return "Thanks for the feedback!"

        def move(n: int):
            n = int(n)
            #import ipdb; ipdb.set_trace()
#            if streamlit:
#                st.write(f"Move: {n}")
            (result, error, out) = board.move(n)
            if streamlit:
                update_container()
            if result:
                return board.as_ai_string()
            else:
                return f"Invalid move: {error}"
        tools = [Tool(name="move",
                      description="Provide a number from 0-8 to move that number to the open space, if and only if it is adjacent to the open space.",
                      func=move),
                 Tool(name="get_board_as_string",
                      description="Get the current board state as a string.",
                      func=get_board),
                 Tool(name="get_board_as_json",
                      description="Get the current board state as JSON.",
                      func=get_board_as_json),
                 Tool(name="submit_feedback",
                      description="If you have suggestions for improvements to the tools, please submit them here.",
                      func=submit_feedback)
                 ]
        agent = initialize_agent(tools,
                                 llm,
                                 agent="zero-shot-react-description",
                                 verbose=True)
        agent.run("Use logical thinking to swap adjacent numbers with the empty space one by one until the board looks like this:\n\n1 2 3\n4 5 6\n7 8  \n\nDo not skip any steps.")

if __name__ == '__main__':
    fire.Fire(CLI)