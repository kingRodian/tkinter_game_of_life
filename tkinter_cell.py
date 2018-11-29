from enum import Enum


class CellState(Enum):
    dead = 0
    alive = 1


class Cell:
    def __init__(self):
        self._state = CellState.dead

    def set_dead(self):
        self._state = CellState.dead

    def set_alive(self):
        self._state = CellState.alive

    def get_state(self):
        return self._state

    def toggle_state(self):
        # This method lets the user flip the cell using the GUI
        if self._state == CellState.dead:
            self._state = CellState.alive
            return self._state
        else:
            self._state = CellState.dead
            return self._state
