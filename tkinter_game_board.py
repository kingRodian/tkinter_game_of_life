from itertools import product
from random import choice, randint

from tkinter_cell import Cell, CellState


# Separating the rules out makes the code cleaner
class GameRules:
    def __init__(self):
        self._transitions = {}
        # Default transitions for living cells
        self._transitions[CellState.alive] = {i:CellState.dead for i in [0,1,4,5,6,7,8]}
        self._transitions[CellState.alive].update({2:CellState.alive, 3:CellState.alive})
        # Default transitions for dead cells
        self._transitions[CellState.dead] = {i:CellState.dead for i in [0,1,2,4,5,6,7,8]}
        self._transitions[CellState.dead].update({3:CellState.alive})

    def get_next_state(self, state, neighbors):
        return self._transitions[state][neighbors]

    def set_rule(self, state, neighbors, newrule):
        self._transitions[state][neighbors] = newrule


# 
class GameConfig:
    def __init__(self):
        self._default_scale = 16
        self._default_num_cells_x = 50
        self._default_num_cells_y = 50
        self._default_fps = 30

        self._current_scale = self._default_scale
        self._current_num_cells_x = self._default_num_cells_x
        self._current_num_cells_y = self._default_num_cells_y
        self._current_fps = self._default_fps

    def set_scale(self, value):
        self._current_scale = value

    def set_num_cells_x(self, value):
        self._current_num_cells_x = value

    def set_num_cells_y(self, value):
        self._current_num_cells_y = value

    def set_fps(self, value):
        self._current_fps = value

    def get_scale(self):
        return self._current_scale

    def get_num_cells_x(self):
        return self._current_num_cells_x

    def get_num_cells_y(self):
        return self._current_num_cells_y

    def get_fps(self):
        return self._current_fps


class GameBoard:
    """
    A _board containing cells that can be alive or dead. We iterate over these and
    using their internal rules, they will flip on or off, hopefully
    giving us a cool pattern.
    """
    _DIRECTIONS = tuple((item for item in product([-1, 0, 1], repeat=2) if item != (0, 0)))

    def __init__(self, config, rules):
        self._config = config
        self._rules = rules
        self._num_cells_x = self._config.get_num_cells_x()
        self._num_cells_y = self._config.get_num_cells_y()
        self._rules = rules
        self._board = []
        # Cell to coord dict for finding coords fast
        self._cell_positions = {}
        self._neighbors = {}
        self._generation = 0
        self._live_count = 0

        self._generate()
        self._create_neighbor_map()


    def _generate(self):
        # This is a list for drawing the first state in tkinter
        self._initial_changes = []
        # Create the board itself
        for y in range(self._num_cells_y):
            row = []
            for x in range(self._num_cells_x):
                cell = Cell()
                self._cell_positions[cell] = (x, y)
                # Cells have a 1/3 chance of starting out alive
                rand_num = randint(0, 2)
                if rand_num == 0:
                    cell.set_alive()
                    self._live_count += 1
                    self._initial_changes.append((cell, CellState.alive))

                row.append(cell)
            self._board.append(row)

    def _create_neighbor_map(self):
        """Create a dict of cell to neighbors to save execution time."""
        for row in self._board:
            for cell in row:
                self._neighbors[cell] = self._find_neighbors(cell)

    def _find_neighbors(self, cell):
        """
        Compile a list of neighbors given a cell.
        """
        neighbors = []
        pos = self._cell_positions[cell]
        for direction in GameBoard._DIRECTIONS:
            x_pos = pos[0] + direction[0]
            y_pos = pos[1] + direction[1]
            if x_pos < 0 or x_pos >= self._num_cells_x:
                continue
            if y_pos < 0 or y_pos >= self._num_cells_y:
                continue
            cell = self._board[y_pos][x_pos]
            neighbors.append(cell)
        return neighbors

    def _get_num_live_neighbors(self, cell):
        live_neighbors = [neighbor for neighbor in self._neighbors[cell] if neighbor.get_state() == CellState.alive]
        num_live_neighbors = len(live_neighbors)
        return num_live_neighbors

    def _get_total_live_cells(self):
        return self._live_count

    def update(self):
        # This is pretty much the same as the original update method, except
        # we need to make a list of data to pass to the gameboardGUI
        self._generation += 1
        spawning = []
        dying = []
        tkinter_data = []
        for row in self._board:
            for cell in row:
                num_live_neighbors = self._get_num_live_neighbors(cell)
                current_state = cell.get_state()
                next_state = self._rules.get_next_state(current_state, num_live_neighbors)
                # No point in updating states that don't change
                # especially with tkinter where we have to set lots of pixels
                if next_state != current_state:
                    tkinter_data.append((cell, next_state))
                    if next_state == CellState.alive:
                        spawning.append(cell)
                        self._live_count += 1
                    else:
                        dying.append(cell)
                        self._live_count -= 1
        # Change the states
        for cell in spawning:
            cell.set_alive()
        for cell in dying:
            cell.set_dead()
        # Return data to tkinter
        return tkinter_data

    def get_coord(self, cell):
        return self._cell_positions[cell]

    def get_cell(self, x, y):
        return self._board[y][x]

    def get_board(self):
        return self._board

    def clear(self):
        for row in self._board:
            for cell in row:
                cell.set_dead()

    def reset(self):
        self._generation = 0
        self.clear()
        self._live_count = 0
        self._initial_changes = []
        for row in self._board:
            for cell in row:
                rand_num = randint(0, 2)
                if rand_num == 0:
                    cell.set_alive()
                    self._live_count += 1
                    self._initial_changes.append((cell, CellState.alive))

    def get_initial_states(self):
        return self._initial_changes

    def get_info_string(self):
        return 'Generation: {} - Live cells: {}'.format(self._generation, self._get_total_live_cells())

    def toggle_cell(self, x, y):
        cell = self.get_cell(x, y)
        state = cell.toggle_state()
        return [(cell, state)]

