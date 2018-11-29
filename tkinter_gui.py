from collections import OrderedDict
from tkinter import *

from tkinter_cell import CellState
from tkinter_game_board import GameBoard, GameConfig, GameRules

WHITE = '#FFFFFF'
BLACK = '#000000'



# This file contains all the GUI elements used for the simulation
# The main class is GameApp, which is responsible for holding the other GUI elements.
# It is important to note that the GUI elements here are supposed to be the frontends to the corresponding
# elements of the logic part of the simulation held in game_board.py
# (except the Actions)

# These are the classes used for different aspects of the UI:
# GameBoardGUI:
# This class links to the gameboard class, which is the main class for the logic portion of the simulation
# The GUI holds the canvas on which the cells are drawn, as well as the info text. 
# Each cell in the logical gameboard is linked to a rectangle on the canvas through a dict.
# When changes are made and the gameboard is updated, a list of changes are sent to the GUI which
# sets the corresponding rects to the right color.

# GameConfigGUI:
# This class links to the game config in the logic portion, with methods for altering the config values
# these being the dimensions of the board, the scale of the rectangles and the fps of the simulation.
# The values are not changed as they are entered, but rather when the user hits the "set" button
# at this point, sanity checks are run on the entered values to see if the changes are to be allowed or not.
# If the size/scale are changed, the board and boardGUI need to be remade
# If the fps is changed as the simulation is running, the changes do not affect the delay between frames
# until the simulation is paused and started again

# GameRulesGUI:
# This class is connected to the rules class of the logic portion. It allows the user
# To set/unset rules in the dict of state-transitions used by the simulation

# ActionGUI:
# This class links buttons to methods of the GameApp for controlling the simulation



# This class provides a GUI connected to the gameboard class
class GameBoardGUI(Frame):
    def __init__(self, master, board_config, rules):
        super().__init__(master)
        self.master = master
        self._board_config = board_config
        self._rules = rules
        self._num_cells_x = board_config.get_num_cells_x()
        self._num_cells_y = board_config.get_num_cells_y()
        self._scale = board_config.get_scale()
        self._canvas_width = self._num_cells_x * self._scale
        self._canvas_height = self._num_cells_y * self._scale
        self.config(borderwidth=1, relief=GROOVE)
        self.pack(expand=YES, fill=BOTH)

        self._game_board = GameBoard(self._board_config, self._rules)

        self._widgets = {}
        self.vars = {}
        self._widgets['header'] = Label(self, text='Game of life')
        # The canvas is the class that allows us to draw the cell graphics
        self._widgets['canvas'] = Canvas(self, width=self._canvas_width, height=self._canvas_height, bg=WHITE)
        # We bind mousebutton 1 to the toggle_cell action, allowing the user to draw on the grid
        self._widgets['canvas'].bind('<Button 1>', self.toggle_cell)
        self.vars['info'] = StringVar(self)
        self._widgets['info_label'] = Label(self, textvariable=self.vars['info'])

        self.colors = {CellState.alive:BLACK, CellState.dead:WHITE}

        # Draw all the widgets
        for widget in self._widgets.values():
            widget.pack()

        # Create links between rectangles on the canvas and the cells
        self._create_cell_links()
        # Draw the initial state of the board
        self._draw_changes(self._game_board.get_initial_states())
        # Set the info string that displays generation number etc
        self.vars['info'].set(self._game_board.get_info_string())

    def update(self):
        # Update the gameboard and then the GUI
        celldata = self._game_board.update()
        self._draw_changes(celldata)
        self.vars['info'].set(self._game_board.get_info_string())

    def unpack(self):
        self.pack_forget()

    def toggle_cell(self, event):
        # Locate the index of the cell that was clicked based on the canvas scale
        scale = self._scale
        cell_x = event.x // scale
        cell_y = event.y // scale
        celldata = self._game_board.toggle_cell(cell_x, cell_y)
        self._draw_changes(celldata)
        print('Toggling cell at ({}, {}).'.format(cell_x, cell_y))

    def _draw_changes(self, celldata):
        # Given a list of updates to cells, change the colors of the corresponding rectangles
        for cell, state in celldata:
            color = self.colors[state]
            self._widgets['canvas'].itemconfig(self.links[cell], fill=color)

    def _create_cell_links(self):
        # Create a dict of cell to rectangle, linking each cell with a corresponding rectangle on the canvas
        graph = self._game_board.get_board()
        self.links = {}
        for row in graph:
            for cell in row:
                # Figure out where on the canvas the rectangle should be, and its size
                cellcoord = self._game_board.get_coord(cell)
                top = cellcoord[0] * self._scale
                left = cellcoord[1] * self._scale
                bottom = top + self._scale
                right = left + self._scale
                square = self._widgets['canvas'].create_rectangle(top, left, bottom, right, fill=self.colors[CellState.dead])
                self.links[cell] = square

    def clear(self):
        # Kill all the cells and update the canvas
        print('Clearing board')
        self._game_board.clear()
        celldata = [(cell, CellState.dead) for row in self._game_board.get_board() for cell in row]
        self._draw_changes(celldata)

    def reset(self):
        # Remove all the rectangles and remake them
        # Probably an inefficient way of doing it
        self._game_board.reset()
        self._widgets['canvas'].delete('all')
        self._create_cell_links()
        self.vars['info'].set(self._game_board.get_info_string())
        self._draw_changes(self._game_board.get_initial_states())

    def change_size(self):
        # Change the canvas size, reset everything and redraw
        self.pack_forget()
        self._widgets['info_label'].pack_forget()
        self._widgets['canvas'].pack_forget()
        self._num_cells_x = self._board_config.get_num_cells_x()
        self._num_cells_y = self._board_config.get_num_cells_y()
        self._scale = self._board_config.get_scale()
        self._canvas_width = self._num_cells_x * self._scale
        self._canvas_height = self._num_cells_y * self._scale
        self._widgets['canvas'] = Canvas(self, width=self._canvas_width, height=self._canvas_height, bg=WHITE)
        self._widgets['canvas'].bind('<Button 1>', self.toggle_cell)
        self.pack(expand=YES, fill=BOTH)
        self._widgets['canvas'].pack()
        self._widgets['info_label'].pack()
        self._game_board = GameBoard(self._board_config, self._rules)
        self.reset()


# This class is the gui which is linked to the config class
# It allows users to change things such as cellsize, board dimensions and a button for putting the changes
# into effect
class GameConfigGUI(Frame):
    def __init__(self, master, board_config):
        Frame.__init__(self, master, borderwidth=1, relief=GROOVE)
        self.pack(expand=YES, fill=BOTH)
        self._board_config = board_config
        self._board_needs_rebuild = False

        # Config
        self._widgets = OrderedDict()
        self._vars = {}

        self._header_label = Label(self, text='Config: ')
        self._header_label.pack()

        # For each configurable variable, we create a label, a variable and an entry field for entering new values
        self._widgets['scale_label'] = Label(self, text='Scale: ')
        self._vars['scale_input'] = StringVar(self, str(self._board_config.get_scale()))
        self._widgets ['scale'] = Entry(self,
                textvariable=self._vars['scale_input'])

        self._widgets['num_cells_x_label'] = Label(self, text="Cells x-axis:")
        self._vars['num_cells_x_input'] = StringVar(self, str(self._board_config.get_num_cells_x()))
        self._widgets ['num_cells_x'] = Entry(self, textvariable=self._vars['num_cells_x_input'])

        self._widgets['num_cells_y_label'] = Label(self, text="Cells y-axis:")
        self._vars['num_cells_y_input'] = StringVar(self, str(self._board_config.get_num_cells_y()))
        self._widgets ['num_cells_y'] = Entry(self,
                textvariable=self._vars['num_cells_y_input'])

        self._widgets['fps_label'] = Label(self, text='Fps: ')
        self._vars['fps_input'] = StringVar(self, str(self._board_config.get_fps()))
        self._widgets ['fps'] = Entry(self, textvariable=self._vars['fps_input'])

        self._widgets['set_options'] = Button(self, text='Set', command=self._set_options)

        for widget in self._widgets.values():
            widget.pack(side=LEFT)


    def _set_options(self):
        # Get window size
        screenwidth = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight()

        self._validate_scale()

        self._validate_num_cells('x', screenwidth)
        self._validate_num_cells('y', screenheight)
        self._validate_fps()

        if self._board_needs_rebuild:
            self.master.stop()
            self.master.rebuild_board()
        self._board_needs_rebuild = False

    def _validate_scale(self):
        # Do some sanity checks on the entered value before allowing changes
        input_var = self._vars['scale_input']
        current_value = self._board_config.get_scale()
        try:
            input_value = int(input_var.get())
        except ValueError:
                input_var.set(str(current_value))
                return
        if input_value == current_value:
            return
        if input_value < 1:
            self._board_config.set_scale(1)
            input_var.set('1')
            self._board_needs_rebuild = True
            return
        self._board_config.set_scale(input_value)
        self._board_needs_rebuild = True

    def _validate_num_cells(self, axis, screen_limit):
        # Sanity check for width fields
        if axis == 'x':
            input_var = self._vars['num_cells_x_input']
            current_value = self._board_config.get_num_cells_x()
            set_value_func = self._board_config.set_num_cells_x
        else:
            input_var = self._vars['num_cells_y_input']
            current_value = self._board_config.get_num_cells_y()
            set_value_func = self._board_config.set_num_cells_y
        try:
            input_value = int(input_var.get())
        except ValueError:
                input_var.set(str(current_value))
                return
        if input_value == current_value:
            return
        if input_value < 1:
            set_value_func(1)
            input_var.set('1')
            self._board_needs_rebuild = True
            return
        set_value_func(input_value)
        self._board_needs_rebuild = True

    def _validate_fps(self):
        # Sanity check for fps
        input_var = self._vars['fps_input']
        current_value = self._board_config.get_fps()
        set_value_func = self._board_config.set_fps
        try:
            input_value = int(input_var.get())
        except ValueError:
            input_var.set(current_value)
            return
        if input_value == current_value:
            return
        if input_value < 1:
            set_value_func(1)
            input_var.set('1')
            return
        # The smallest delay is 1 ms, so no point in going above
        if input_value > 1000:
            set_value_func(1000)
            input_var.set('1000')
            return
        set_value_func(input_value)

    def unpack(self):
        self.pack_forget()

    def repack(self):
        self.pack(expand=YES, fill=BOTH)

    def get_scale(self):
        return self._vars['current_scale']

    def get_num_cells_x(self):
        return self._vars['current_num_cells_x']

    def get_num_cells_y(self):
        return self._vars['current_num_cells_y']

    def get_fps(self):
        return self._vars['current_fps']


# Class which allows the user to change the game rules on the fly
class GameRulesGUI(Frame):
    def __init__(self, master, rules):
        Frame.__init__(self, master, borderwidth=1, relief=GROOVE)
        self.pack(expand=YES, fill=BOTH)
        self._rules = rules
        self._state_values = {0:CellState.dead, 1:CellState.alive}
        self._header_label = Label(self, text='Ruleset: ')
        self._header_label.pack()
        self._vars = {}
        self._widgets = {}

        # Create a bunch of labels, checkbuttons and corresponding variables for changing the
        # survival and birth rules
        for rule in ('survive', 'born'):
            if rule == 'survive':
                text = 'Survive: '
                state = CellState.alive
            else:
                text = '    Born: '
                state = CellState.dead
            newframe = Frame(self, borderwidth=1, relief=GROOVE)
            label = Label(newframe, text=text)
            self._widgets[rule + 'frame'] = newframe
            self._widgets[rule + 'label'] = label
            newframe.pack(expand=YES, fill=BOTH)
            label.pack(side=LEFT)
            for neighbors in range(9):
                button_label = Label(newframe, text=str(neighbors) + ':')
                var_name = rule + ' ' + str(neighbors)
                var = BooleanVar(self)
                button = Checkbutton(newframe, variable=var, onvalue=1, 
                        offvalue=0, command=self.set_value)
                self._widgets[var_name] = button
                self._vars[var_name] = var
                button_label.pack(side=LEFT)
                button.pack(side=LEFT)

        # Set the default game rules
        self._vars['born 3'].set(True)
        self._vars['survive 2'].set(True)
        self._vars['survive 3'].set(True)

    def unpack(self):
        self.pack_forget()

    def repack(self):
        self.pack(expand=YES, fill=BOTH)

    def set_value(self, *args):
        # Change the rule in the rule class
        for key, value in self._vars.items():
            name, neighbors = key.split()
            neighbors = int(neighbors)
            if name == 'survive':
                state = CellState.alive
            else:
                state = CellState.dead
            newrule = self._state_values[value.get()]
            self._rules.set_rule(state, neighbors, newrule)


# Gui which has various actions for running the simulation
class ActionGUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, borderwidth=1, relief=GROOVE)
        self.pack(expand=YES, fill=BOTH)
        self._widgets = OrderedDict()

        # We have a series of buttons bound to function callbacks to let the user play, reset etc
        self._widgets['label'] = Label(self, text='Actions: ')
        self._widgets['play_pause'] = Button(self, text='Play/Pause', command=self.master.play_pause)
        self._widgets['advance'] = Button(self, text='Advance', command=self.master.advance)
        self._widgets['clear'] = Button(self, text='Clear', command=self.master._game_board.clear)
        self._widgets['reset'] = Button(self, text='Reset', command=self.master.reset)
        self._widgets['quit'] = Button(self, text='Quit', command=self.quit)

        for widget in self._widgets.values():
            widget.pack(side=LEFT)

    def unpack(self):
        self.pack_forget()

    def repack(self):
        self.pack()


# The main application itself, holds all the other GUIs
class GameApp(Frame):
    def __init__(self):
        # Initialize top level window
        Frame.__init__(self, relief=FLAT)
        # Dialog allows floating windows in certain window managers
        self.master.attributes('-type', 'dialog')
        self.pack(expand=YES, fill=BOTH)

        # Variables related to play/pause and fps
        self._playing = False
        self._play_id = None
        self._delay = 30

        # Config and rules to bind to their corresponding guis
        self._board_config = GameConfig()
        self._rules = GameRules()

        # Game board and other guis
        self._game_board = GameBoardGUI(self, self._board_config, self._rules)
        self._action_gui = ActionGUI(self)
        self._config_gui = GameConfigGUI(self, self._board_config)
        self._rule_gui = GameRulesGUI(self, self._rules)

    def play_pause(self):
        # If we are not playing, calculate the delay between each frame and start 
        # a callback for playing the next frame
        # If we are playing, stop the callback and set playing to false
        if not self._playing:
            self._playing = True
            self._delay = 1000 // self._board_config.get_fps()
            self._play_id = self.after(0, self._play_frame)
        else:
            self.after_cancel(self._play_id)
            self._play_id = None
            self._playing = False

    def stop(self):
        # Function used when we change the board size etc
        if self._playing:
            self.after_cancel(self._play_id)
            self._play_id = None
            self._playing = False


    def _play_frame(self):
        # Update everything, then create a callback that will play the next frame
        self._game_board.update()
        self._play_id = self.after(self._delay, self._play_frame)

    def advance(self):
        # Single step the simulation
        self._game_board.update()

    def reset(self):
        self._game_board.reset()

    def quit(self):
        self.master.quit()

    def rebuild_board(self):
        # We unpack everything from the gui, change the canvas size and then repack everything
        self._rule_gui.unpack()
        self._config_gui.unpack()
        self._action_gui.unpack()
        self._game_board.unpack()

        num_cells_x = self._board_config.get_num_cells_x()
        num_cells_y = self._board_config.get_num_cells_y()
        scale = self._board_config.get_scale()
        print('Rebuilding - x: {} y: {} scale: {}.'.format(num_cells_x, num_cells_y, scale))
        self._game_board.change_size()

        self._action_gui.repack()
        self._config_gui.repack()
        self._rule_gui.repack()
