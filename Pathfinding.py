from tkinter import *
from tkinter import ttk
from math import sqrt
from numpy.random import randint
import time

path_info = 'Stand by'

cursor = (0, 0)

canvas_width = 700
canvas_height = 700

pixel = 20
rows = round(canvas_width / pixel)
columns = round(canvas_height / pixel)

obstacle_frequency = .2

animation_speed = 10

spot_width = round(canvas_width / rows)
spot_height = round(canvas_height / columns)

start = [0, 0]
destination = [rows - 1, columns - 1]

start_previous, destination_previous = [], []

start_previous.append(start)
destination_previous.append(destination)

on_loop = False

start_color = '#ee4540'
end_color = '#593E8B'
open_color = '#42e6a4'
close_color = '#018383'
path_color = '#f5dea3'

algorithm = 'A* Search'

cost_so_far = 0

num_of_visited_nodes = 0


class Node:
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

        self.neighbors = []
        self.obstacle = False

    def addNeighbors(self):

        if isChecked.get():
            moves = [[-1, 0],
                     [0, -1],
                     [1, 0],
                     [0, 1],
                     [-1, -1],
                     [-1, 1],
                     [1, -1],
                     [1, 1]]
        else:
            moves = [[-1, 0],
                     [0, -1],
                     [1, 0],
                     [0, 1]]

        for new_position in moves:

            node_position = (self.position[0] + new_position[0], self.position[1] + new_position[1])

            if node_position[0] > (rows - 1) or node_position[0] < 0 or node_position[1] > (columns - 1) or node_position[1] < 0:
                continue

            if grid[node_position[0]][node_position[1]].obstacle:
                continue

            self.neighbors.append(Node(self, node_position))

    def __eq__(self, other):
        return self.position == other.position

    def show(self, canvas, **kwargs):
        canvas.create_rectangle(self.position[0] * pixel,
                                self.position[1] * pixel,
                                self.position[0] * pixel + pixel,
                                self.position[1] * pixel + pixel, **kwargs)


class DisplayCanvas:

    def __init__(self, parent, width, height, side):
        self.frame = Frame(parent)
        self.frame.pack(side=side, expand=1, fill=X, padx=(0, 35), pady=(0, 40))

        style = ttk.Style()
        style.configure('algo.TMenubutton', font=('Helvetica', 18, 'bold'))

        self.options = ['', 'A* Search', 'Dijkstra\'s', 'Breadth-first']
        self.value = StringVar()
        self.value.set(self.options[1])

        self.Algorithm = ttk.OptionMenu(self.frame, self.value, *self.options, style='algo.TMenubutton', command=self.getAlgorithm)
        self.Algorithm.config(width=12)
        self.Algorithm.pack(anchor=N, pady=(0, 10))

        self.canvas = Canvas(self.frame, width=width + 1, height=height + 1, bg='white', bd=-2)
        self.canvas.bind('<Button-1>', lambda event: set_start(self.canvas))
        self.canvas.bind('<Button-2>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<B2-Motion>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<Control-Button-2>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Control-B2-Motion>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Button-3>', lambda event: set_destination(self.canvas))
        self.canvas.bind('<Motion>', lambda event: getCursorPosition(self.canvas, event))

        self.canvas.pack(pady=(10, 0))

    def getAlgorithm(self, value):
        global algorithm, on_loop, cost_so_far, num_of_visited_nodes
        algorithm = value

        on_loop = False

        cost_so_far = 0
        num_of_visited_nodes = 0

        cost_Label.config(text='Cost: %s' % cost_so_far)
        visited_Label.config(text='Visited: %s' % num_of_visited_nodes)

        if algorithm == 'A* Search':
            heur_4moves_optionMenu.config(state='normal')
            heur_8moves_optionMenu.config(state='normal')
        else:
            heur_4moves_optionMenu.config(state='disabled')
            heur_8moves_optionMenu.config(state='disabled')

        for i in range(columns):
            for j in range(rows):
                if grid[i][j].obstacle:
                    pass
                else:
                    grid[i][j] = Node(None, (i, j))
                    if borderAllowed.get():
                        grid[i][j].show(self.canvas, fill='white', outline='black')
                    else:
                        grid[i][j].show(self.canvas, fill='white', outline='white')

        if borderAllowed.get():
            grid[start[0]][start[1]].show(self.canvas, fill=start_color, outline='black')
            grid[destination[0]][destination[1]].show(self.canvas, fill=end_color, outline='black')
        else:
            grid[start[0]][start[1]].show(self.canvas, fill=start_color, outline='white')
            grid[destination[0]][destination[1]].show(self.canvas, fill=end_color, outline='white')

        self.canvas.bind('<Button-1>', lambda event: set_start(self.canvas))
        self.canvas.bind('<Button-2>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<B2-Motion>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<Control-Button-2>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Control-B2-Motion>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Button-3>', lambda event: set_destination(self.canvas))
        self.canvas.config(state='normal')

        button_Play.bind('<Button-1>', lambda event: setAlgorithm(self))
        button_Play.config(state='normal')

        checkbox_move.config(state='normal')

    def getCanvas(self):
        return self.canvas

    def getFrame(self):
        return self.frame


class DisplayOptionMenu:

    def __init__(self, canvas, frame, option, value, style):
        self.canvas = canvas
        self.option = option
        self.value = value
        self.style = style
        self.frame = frame

        self.heurisitic_optionMenu = ttk.OptionMenu(self.frame, self.value, *self.option, style=self.style, command=self.setHeuristic)
        self.heurisitic_optionMenu.config(width=17)
        self.heurisitic_optionMenu.pack(side=LEFT, padx=5, pady=6)

    def getOptionMenu(self):
        return self.heurisitic_optionMenu

    def setHeuristic(self, value):
        global on_loop, cost_so_far, num_of_visited_nodes

        on_loop = False

        cost_so_far = 0
        num_of_visited_nodes = 0

        for i in range(columns):
            for j in range(rows):
                if grid[i][j].obstacle:
                    pass
                else:
                    grid[i][j] = Node(None, (i, j))
                    if borderAllowed.get():
                        grid[i][j].show(self.canvas, fill='white', outline='black')
                    else:
                        grid[i][j].show(self.canvas, fill='white', outline='white')

        if borderAllowed.get():
            grid[start[0]][start[1]].show(self.canvas, fill=start_color, outline='black')
            grid[destination[0]][destination[1]].show(self.canvas, fill=end_color, outline='black')
        else:
            grid[start[0]][start[1]].show(self.canvas, fill=start_color, outline='white')
            grid[destination[0]][destination[1]].show(self.canvas, fill=end_color, outline='white')

        self.canvas.bind('<Button-1>', lambda event: set_start(self.canvas))
        self.canvas.bind('<Button-2>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<B2-Motion>', lambda event: createObstacle(self.canvas, event))
        self.canvas.bind('<Control-Button-2>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Control-B2-Motion>', lambda event: eraseObstacle(self.canvas, event))
        self.canvas.bind('<Button-3>', lambda event: set_destination(self.canvas))
        self.canvas.config(state='normal')

        button_Play.bind('<Button-1>', lambda event: setAlgorithm(gridCanvas))
        button_Play.config(state='normal')

        checkbox_move.config(state='normal')


def showBorder(canvas):
    for i in range(rows):
        for j in range(columns):
            if borderAllowed.get():
                grid[i][j].show(canvas, outline='black')
            else:
                grid[i][j].show(canvas, outline='white')


def eraseObstacle(canvas, event):
    global start, destination
    x, y = event.x // pixel, event.y // pixel
    try:
        obstacle = grid[x][y]
        if (x, y) != (start[0], start[1]) and (x, y) != (destination[0], destination[1]) and event.x >= 0 and event.y >= 0 and obstacle.obstacle is True:
            obstacle.obstacle = False
            obstacle.show(canvas, fill='white')

    except IndexError:
        pass


def createObstacle(canvas, event):
    global start, destination
    x, y = event.x // pixel, event.y // pixel
    try:
        obstacle = grid[x][y]
        if (x, y) != (start[0], start[1]) and (x, y) != (destination[0], destination[1]) and event.x >= 0 and event.y >= 0 and obstacle.obstacle is False:
            obstacle.obstacle = True
            obstacle.show(canvas, fill='black')

    except IndexError:
        pass


def getCursorPosition(canvas, event):
    global cursor
    cursor = event.x // pixel, event.y // pixel
    position_Label.config(text='Position: (%d, %d)' % (cursor[1], cursor[0]))
    try:
        if grid[cursor[0]][cursor[1]].obstacle is True or on_loop is True:
            canvas.unbind('<Button-1>')
            canvas.unbind('<Button-3>')
        elif grid[cursor[0]][cursor[1]].obstacle is False or on_loop is False:
            canvas.bind('<Button-1>', lambda event: set_start(canvas))
            canvas.bind('<Button-3>', lambda event: set_destination(canvas))

    except IndexError:
        pass


def randomObstacle(canvas):
    global on_loop, obstacle_frequency, cost_so_far, num_of_visited_nodes

    on_loop = False

    cost_so_far = 0
    num_of_visited_nodes = 0

    cost_Label.config(text='Cost: %s' % cost_so_far)
    visited_Label.config(text='Visited: %s' % num_of_visited_nodes)

    iteration = 0
    max_iterations = int((rows * columns) * obstacle_frequency)

    modified_spots = []

    canvas.delete(ALL)

    canvas.bind('<Button-1>', lambda event: set_start(canvas))
    canvas.bind('<Button-2>', lambda event: createObstacle(canvas, event))
    canvas.bind('<B2-Motion>', lambda event: createObstacle(canvas, event))
    canvas.bind('<Control-Button-2>', lambda event: eraseObstacle(canvas, event))
    canvas.bind('<Control-B2-Motion>', lambda event: eraseObstacle(canvas, event))
    canvas.bind('<Button-3>', lambda event: set_destination(canvas))
    canvas.config(state='normal')

    button_Play.bind('<Button-1>', lambda event: setAlgorithm(gridCanvas))
    button_Play.config(state='normal')

    checkbox_move.config(state='normal')

    if algorithm == 'A* Search':
        heur_4moves_optionMenu.config(state='normal')
        heur_8moves_optionMenu.config(state='normal')
    else:
        heur_4moves_optionMenu.config(state='disabled')
        heur_8moves_optionMenu.config(state='disabled')

    for i in range(rows):
        for j in range(columns):
            grid[i][j] = Node(None, (i, j))
            if borderAllowed.get():
                grid[i][j].show(canvas, fill='white', outline='black')
            else:
                grid[i][j].show(canvas, fill='white', outline='white')

    while iteration < max_iterations:

        spot = (randint(0, rows), randint(0, columns))

        if spot == (start[0], start[1]) \
                or spot == (start[0] + 1, start[1]) \
                or spot == (start[0] - 1, start[1]) \
                or spot == (start[0], start[1] + 1) \
                or spot == (start[0], start[1] - 1) \
                or spot == (start[0] + 1, start[1] - 1) \
                or spot == (start[0] + 1, start[1] + 1) \
                or spot == (start[0] - 1, start[1] - 1) \
                or spot == (start[0] - 1, start[1] + 1) \
                or spot == (destination[0], destination[1]) \
                or spot == (destination[0] + 1, destination[1]) \
                or spot == (destination[0] - 1, destination[1]) \
                or spot == (destination[0], destination[1] + 1) \
                or spot == (destination[0], destination[1] - 1) \
                or spot == (destination[0] + 1, destination[1] - 1) \
                or spot == (destination[0] + 1, destination[1] + 1) \
                or spot == (destination[0] - 1, destination[1] - 1) \
                or spot == (destination[0] - 1, destination[1] + 1):

            continue

        elif spot not in modified_spots:
            modified_spots.append(spot)
            grid[spot[0]][spot[1]].obstacle = True
            grid[spot[0]][spot[1]].show(canvas, fill='black', outline='black')

            iteration += 1

        else:
            continue

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    start_Label.config(text='Start: %s' % start)
    end_Label.config(text='End: %s' % destination)
    canvas.update()


def set_start(canvas):
    global start, start_previous, grid

    start = list(cursor)

    if len(start_previous) > 0:
        if borderAllowed.get():
            grid[start_previous[-1][0]][start_previous[-1][1]].show(canvas, fill='white', outline='black')
        else:
            grid[start_previous[-1][0]][start_previous[-1][1]].show(canvas, fill='white', outline='white')
        start_previous.pop(0)

    start_Label.config(text='Start: %s' % start)

    start_previous.append(start)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')


def set_destination(canvas):
    global destination, destination_previous, grid

    destination = list(cursor)

    if len(destination_previous) > 0:
        if borderAllowed.get():
            grid[destination_previous[-1][0]][destination_previous[-1][1]].show(canvas, fill='white', outline='black')
        else:
            grid[destination_previous[-1][0]][destination_previous[-1][1]].show(canvas, fill='white', outline='white')
        destination_previous.pop(0)

    end_Label.config(text='End: %s' % destination)

    destination_previous.append(destination)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')


def clear(canvas):
    global start, destination, start_previous, destination_previous, on_loop, cost_so_far, num_of_visited_nodes

    on_loop = False

    cost_so_far = 0
    num_of_visited_nodes = 0

    cost_Label.config(text='Cost: %s' % cost_so_far)
    visited_Label.config(text='Visited: %s' % num_of_visited_nodes)

    canvas.delete(ALL)

    canvas.bind('<Button-1>', lambda event: set_start(canvas))
    canvas.bind('<Button-2>', lambda event: createObstacle(canvas, event))
    canvas.bind('<B2-Motion>', lambda event: createObstacle(canvas, event))
    canvas.bind('<Control-Button-2>', lambda event: eraseObstacle(canvas, event))
    canvas.bind('<Control-B2-Motion>', lambda event: eraseObstacle(canvas, event))
    canvas.bind('<Button-3>', lambda event: set_destination(canvas))
    canvas.config(state='normal')

    button_Play.bind('<Button-1>', lambda event: setAlgorithm(gridCanvas))
    button_Play.config(state='normal')

    button_Random.bind('<Button-1>', lambda event: randomObstacle(gridCanvas.getCanvas()))
    button_Random.config(state='normal')

    checkbox_move.config(state='normal')

    if algorithm == 'A* Search':
        heur_4moves_optionMenu.config(state='normal')
        heur_8moves_optionMenu.config(state='normal')
    else:
        heur_4moves_optionMenu.config(state='disabled')
        heur_8moves_optionMenu.config(state='disabled')

    start_previous, destination_previous = [], []

    for i in range(rows):
        for j in range(columns):
            grid[i][j] = Node(None, (i, j))
            if borderAllowed.get():
                grid[i][j].show(canvas, fill='white', outline='black')
            else:
                grid[i][j].show(canvas, fill='white', outline='white')

    start_previous.append(start)
    destination_previous.append(destination)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    start_Label.config(text='Start: %s' % start)
    end_Label.config(text='End: %s' % destination)


def return_path(canvas, current_node):
    global on_loop, cost_so_far, num_of_visited_nodes

    path = []
    num_of_visited_nodes = len(visited_list) + len(yet_to_visit_list)

    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent

    for i in path[::-1]:
        cost_so_far += 1

        if not on_loop:
            break

        sleep = animation_speed / 1000
        time.sleep(sleep)

        if borderAllowed.get():
            grid[i[0]][i[1]].show(canvas, fill=path_color, outline='black')
        else:
            grid[i[0]][i[1]].show(canvas, fill=path_color, outline='')

        canvas.update()

    cost_Label.config(text='Cost: %s' % cost_so_far)
    visited_Label.config(text='Visited: %s' % num_of_visited_nodes)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    if algorithm == 'A* Search':
        heur_4moves_optionMenu.config(state='normal')
        heur_8moves_optionMenu.config(state='normal')
    else:
        heur_4moves_optionMenu.config(state='disabled')
        heur_8moves_optionMenu.config(state='disabled')


def calculateCost(current, neighbor):
    global cost_so_far

    cost = 1

    if abs(current.position[1] - neighbor.position[1]) + abs(current.position[0] - neighbor.position[0]) == 2:
        cost = round(sqrt(2), 1)

    return cost


def heuristics(current, goal):
    global algorithm, heur_4moves_value, heur_8moves_value

    dx = abs(current.position[0] - goal.position[0])
    dy = abs(current.position[1] - goal.position[1])

    if algorithm != 'Dijkstra\'s' and algorithm != 'Breadth-first':

        if isChecked.get():
            if heur_8moves_value.get() == 'Octile distance':
                return (dy + dx) + (round(sqrt(2), 1) - 1) * min(dy, dx)
            elif heur_8moves_value.get() == 'Chebyshev distance':
                return max(dx, dy)
            elif heur_8moves_value.get() == 'Euclidean distance':
                return sqrt(dx ** 2 + dy ** 2)

        if heur_4moves_value.get() == 'Euclidean distance':
            return sqrt(dx ** 2 + dy ** 2)
        elif heur_4moves_value.get() == 'Manhattan distance':
            return (dx + dy) * (1.0 + (1 / 10000))

    else:
        return 0


def a_star(canvas, src, dest):
    global on_loop, animation_speed, num_of_visited_nodes, visited_list, yet_to_visit_list

    canvas.unbind('<Button-1>')
    canvas.unbind('<Button-2>')
    canvas.unbind('<B2-Motion>')
    canvas.unbind('<Control-Button-2>')
    canvas.unbind('<Control-B2-Motion>')
    canvas.unbind('<Button-3>')
    canvas.config(state='disabled')

    button_Play.unbind('<Button-1>')
    button_Play.config(state='disabled')

    checkbox_move.config(state='disabled')

    heur_4moves_optionMenu.config(state='disabled')
    heur_8moves_optionMenu.config(state='disabled')

    on_loop = True

    starting_node = grid[src[0]][src[1]]
    ending_node = grid[dest[0]][dest[1]]

    starting_node.g = 0
    starting_node.h = heuristics(starting_node, ending_node)
    starting_node.f = starting_node.g + starting_node.h

    yet_to_visit_list, visited_list = [], []
    yet_to_visit_list.append(starting_node)

    while len(yet_to_visit_list) > 0:
        path_Label.config(text='Searching...')

        if not on_loop:
            break

        sleep = animation_speed / 1000
        time.sleep(sleep)

        current_node = yet_to_visit_list[0]
        current_index = 0

        for index, item in enumerate(yet_to_visit_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        if current_node == ending_node:
            path_Label.config(text='Path found!')
            return return_path(canvas, current_node)

        yet_to_visit_list.pop(current_index)
        visited_list.append(current_node)

        if borderAllowed.get():
            current_node.show(canvas, fill=close_color, outline='black')
        else:
            current_node.show(canvas, fill=close_color, outline='white')

        current_node.addNeighbors()
        neighbors = current_node.neighbors

        for neighbor in neighbors:

            if len([visited_neighbor for visited_neighbor in visited_list if visited_neighbor == neighbor]) > 0:
                continue

            neighbor.g = current_node.g + calculateCost(current_node, neighbor)
            neighbor.h = heuristics(neighbor, ending_node)
            neighbor.f = neighbor.g + neighbor.h

            if len([i for i in yet_to_visit_list if neighbor == i and neighbor.g >= i.g]) > 0:
                continue

            yet_to_visit_list.append(neighbor)

            if borderAllowed.get():
                neighbor.show(canvas, fill=open_color, outline='black')
            else:
                neighbor.show(canvas, fill=open_color, outline='white')

        canvas.update()

    path_Label.config(text='No path found')

    num_of_visited_nodes = len(visited_list)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    checkbox_move.config(state='normal')


def dijkstras(canvas):
    a_star(canvas.getCanvas(), start, destination)


def breadth_first(canvas, src, dest):
    global on_loop, animation_speed, num_of_visited_nodes, visited_list, yet_to_visit_list

    canvas.unbind('<Button-1>')
    canvas.unbind('<Button-2>')
    canvas.unbind('<B2-Motion>')
    canvas.unbind('<Control-Button-2>')
    canvas.unbind('<Control-B2-Motion>')
    canvas.unbind('<Button-3>')
    canvas.config(state='disabled')

    button_Play.unbind('<Button-1>')
    button_Play.config(state='disabled')

    checkbox_move.config(state='disabled')

    heur_4moves_optionMenu.config(state='disabled')
    heur_8moves_optionMenu.config(state='disabled')

    on_loop = True

    yet_to_visit_list, visited_list = [], []

    starting_node = grid[src[0]][src[1]]
    ending_node = grid[dest[0]][dest[1]]

    yet_to_visit_list.append(starting_node)

    while len(yet_to_visit_list) > 0:

        if not on_loop:
            break

        sleep = animation_speed / 1000
        time.sleep(sleep)

        current_node = yet_to_visit_list.pop(0)
        visited_list.append(current_node)

        if borderAllowed.get():
            visited_list[-1].show(canvas, fill=close_color, outline='black')
        else:
            visited_list[-1].show(canvas, fill=close_color, outline='white')

        if current_node == ending_node:
            return return_path(canvas, current_node)

        current_node.addNeighbors()
        neighbors = current_node.neighbors

        for neighbor in neighbors:

            if len([visited_neighbor for visited_neighbor in visited_list if visited_neighbor == neighbor]) > 0:
                continue

            if len([yet_to_visit_neighbor for yet_to_visit_neighbor in yet_to_visit_list if yet_to_visit_neighbor == neighbor]) > 0:
                continue

            yet_to_visit_list.append(neighbor)

            if borderAllowed.get():
                yet_to_visit_list[-1].show(canvas, fill=open_color, outline='black')
            else:
                yet_to_visit_list[-1].show(canvas, fill=open_color, outline='white')

        canvas.update()

    path_Label.config(text='No path found')

    num_of_visited_nodes = len(visited_list)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    checkbox_move.config(state='normal')


def set_values():
    global animation_Label, obstacle_Label, obstacle_frequency, animation_speed

    try:

        input_animation_value = animation_text.get()
        input_obstacle_frequency = obstacle_text.get()

        animation_speed = int(input_animation_value)
        obstacle_frequency = float(input_obstacle_frequency) / 100

        animation_Label.config(text='Animation(ms): %sms' % animation_speed)
        obstacle_Label.config(text='Obstacle(%%): %s%%' % int((obstacle_frequency * 100)))

    except:

        animation_Label.config(text='Animation(ms): %sms' % animation_speed)
        obstacle_Label.config(text='Obstacle(%%): %s%%' % int((obstacle_frequency * 100)))

    settings_window.destroy()


def show_maze(canvas):
    global start, destination, start_previous, destination_previous, on_loop, cost_so_far, num_of_visited_nodes

    on_loop = True

    canvas.delete(ALL)

    cost_so_far = 0
    num_of_visited_nodes = 0

    cost_Label.config(text='Cost: %s' % cost_so_far)
    visited_Label.config(text='Visited: %s' % num_of_visited_nodes)

    canvas.unbind('<Button-1>')
    canvas.unbind('<Button-2>')
    canvas.unbind('<B2-Motion>')
    canvas.unbind('<Control-Button-2>')
    canvas.unbind('<Control-B2-Motion>')
    canvas.unbind('<Button-3>')
    canvas.config(state='disabled')

    button_Play.unbind('<Button-1>')
    button_Play.config(state='disable')

    button_Maze.unbind('<Button-1>')
    button_Maze.config(state='disable')

    button_Random.unbind('<Button-1>')
    button_Random.config(state='disable')

    checkbox_move.config(state='normal')

    initial_complexity = .01
    initial_density = 2

    adjusted_complexity = int(initial_complexity * (5 * (rows + columns)))
    adjusted_density = int(initial_density * ((rows // 2) * (columns // 2)))

    for i in range(columns):
        for j in range(rows):
            grid[i][j] = Node(None, (i, j))
            if borderAllowed.get():
                grid[i][j].show(canvas, fill='white', outline='black')
            else:
                grid[i][j].show(canvas, fill='white', outline='white')

    for i in range(adjusted_density):
        if not on_loop:
            break

        x, y = randint(0, rows // 2) * 2, randint(0, columns // 2) * 2

        grid[x][y].obstacle = True
        if borderAllowed:
            grid[x][y].show(canvas, fill='black', outline='black')
        else:
            grid[x][y].show(canvas, fill='black', outline='white')

        for j in range(adjusted_complexity):
            neighbors = []
            if x > 1:
                neighbors.append((x - 2, y))
            if x < columns - 2:
                neighbors.append((x + 2, y))
            if y > 1:
                neighbors.append((x, y - 2))
            if y < rows - 2:
                neighbors.append((x, y + 2))
            if len(neighbors):
                x_, y_ = neighbors[randint(0, len(neighbors))]
                if grid[x_][y_].obstacle is False:

                    grid[x_][y_].obstacle = True
                    if borderAllowed:
                        grid[x_][y_].show(canvas, fill='black', outline='black')
                    else:
                        grid[x_][y_].show(canvas, fill='black', outline='white')

                    grid[x_ + (x - x_) // 2][y_ + (y - y_) // 2].obstacle = True
                    if borderAllowed:
                        grid[x_ + (x - x_) // 2][y_ + (y - y_) // 2].show(canvas, fill='black', outline='black')
                    else:
                        grid[x_ + (x - x_) // 2][y_ + (y - y_) // 2].show(canvas, fill='black', outline='white')

                    x, y = x_, y_

        canvas.update()

    # ******* BORDERS *******
    for i in range(columns):
        grid[i][0].obstacle = True
        if borderAllowed:
            grid[i][0].show(canvas, fill='black', outline='black')
        else:
            grid[i][0].show(canvas, fill='black', outline='white')

    for i in range(rows):
        grid[0][i].obstacle = True
        if borderAllowed:
            grid[0][i].show(canvas, fill='black', outline='black')
        else:
            grid[0][i].show(canvas, fill='black', outline='white')

    for i in range(columns):
        grid[i][columns - 1].obstacle = True
        if borderAllowed:
            grid[i][columns - 1].show(canvas, fill='black', outline='black')
        else:
            grid[i][columns - 1].show(canvas, fill='black', outline='white')

    for i in range(rows):
        grid[rows - 1][i].obstacle = True
        if borderAllowed:
            grid[rows - 1][i].show(canvas, fill='black', outline='black')
        else:
            grid[rows - 1][i].show(canvas, fill='black', outline='white')

    start_previous, destination_previous = [], []

    while True:
        start = [randint(1, rows - 2), randint(1, columns - 2)]

        if grid[start[0]][start[1]].obstacle is False:
            break

    while True:
        destination = [randint(1, rows - 2), randint(1, columns - 2)]

        if grid[destination[0]][destination[1]].obstacle is False:
            break

    start_previous.append(start)
    destination_previous.append(destination)

    if borderAllowed.get():
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='black')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='black')
    else:
        grid[start[0]][start[1]].show(canvas, fill=start_color, outline='white')
        grid[destination[0]][destination[1]].show(canvas, fill=end_color, outline='white')

    start_Label.config(text='Start: %s' % start)
    end_Label.config(text='End: %s' % destination)

    button_Random.bind('<Button-1>', lambda event: randomObstacle(gridCanvas.getCanvas()))
    button_Random.config(state='normal')

    button_Play.bind('<Button-1>', lambda event: setAlgorithm(gridCanvas))
    button_Play.config(state='normal')

    button_Maze.bind('<Button-1>', lambda event: show_maze(gridCanvas.getCanvas()))
    button_Maze.config(state='normal')

    if algorithm == 'A* Search':
        heur_4moves_optionMenu.config(state='normal')
        heur_8moves_optionMenu.config(state='normal')
    else:
        heur_4moves_optionMenu.config(state='disabled')
        heur_8moves_optionMenu.config(state='disabled')

    on_loop = False


def show_settings_window(canvas):
    global settings_window, animation_value, animation_text, obstacle_text, settings_window, animation_speed
    try:
        if settings_window.state() == 'normal':
            settings_window.focus()

    except:
        settings_window = Toplevel(root)
        settings_window.focus()
        settings_window.title('Settings')
        settings_window.resizable(False, False)

        input_frame = Frame(settings_window)
        input_frame.pack()

        animation_label = Label(input_frame, text='Animation(ms):', font='Helvetica 10')
        animation_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5))

        animation_text = Entry(input_frame)
        animation_text.insert(END, animation_speed)
        animation_text.grid(row=0, column=1, padx=(0, 10), pady=(10, 5))

        obstacle_label = Label(input_frame, text='Obstacle(%):', font='Helvetica 10')
        obstacle_label.grid(row=1, column=0, stick=E, padx=(10, 5), pady=(5, 10))

        obstacle_text = Entry(input_frame)
        obstacle_text.insert(END, int(obstacle_frequency * 100))
        obstacle_text.grid(row=1, column=1, padx=(0, 10), pady=(5, 10))

        button_frame = Frame(settings_window)
        button_frame.pack()

        button_save = Button(button_frame, text='Save', width=10, command=set_values)
        button_save.grid(row=0, column=0, padx=5, pady=(5, 10), stick=E)

        button_cancel = Button(button_frame, text='Cancel', width=10, command=settings_window.destroy)
        button_cancel.grid(row=0, column=1, padx=5, pady=(5, 10), stick=W)


def setAlgorithm(canvas):
    global algorithm

    if algorithm == 'A* Search':
        a_star(canvas.getCanvas(), start, destination)

    elif algorithm == 'Dijkstra\'s':
        dijkstras(canvas)

    elif algorithm == 'Breadth-first':
        breadth_first(canvas.getCanvas(), start, destination)


def showOptionMenu():
    if isChecked.get():
        heur_4moves_optionMenu.pack_forget()
        heur_8moves_optionMenu.pack(side=LEFT, padx=5, pady=7)
    else:

        heur_4moves_optionMenu.pack(side=LEFT, padx=5, pady=7)
        heur_8moves_optionMenu.pack_forget()


# ******* App *******
root = Tk()
root.title('Pathfinding Algorithm Visualization')
# root.state('zoomed')
root.resizable(False, False)

# ******* Toolbar *******
toolbar = Frame(root)
toolbar.pack(fill=X, pady=(0, 20))

# ******* Status *******
status_Frame = Frame(root, width=230)
status_Frame.pack(side=LEFT, fill=Y, expand=1)
status_Frame.pack_propagate(0)

label_frame = Frame(status_Frame, height=30, width=400)
label_frame.pack(fill=BOTH)

start_Label = Label(label_frame, text='Start: %s' % str(start), font='Helvetica 12')
start_Label.grid(row=0, stick=W, padx=(35, 0), pady=(55, 0))

end_Label = Label(label_frame, text='End: %s' % str(destination), font='Helvetica 12')
end_Label.grid(row=1, stick=W, padx=(35, 0), pady=(20, 20))

animation_Label = Label(label_frame, text='Animation(ms): %sms' % animation_speed, font='Helvetica 12')
animation_Label.grid(row=2, stick=W, padx=(35, 0), pady=(0, 20))

obstacle_Label = Label(label_frame, text='Obstacle(%%): %s%%' % int((obstacle_frequency * 100)), font='Helvetica 12')
obstacle_Label.grid(row=3, stick=W, padx=(35, 0), pady=(0, 20))

position_Label = Label(label_frame, text='Position: (%d, %d)' % cursor, font='Helvetica 12')
position_Label.grid(row=4, stick=W, padx=(35, 0), pady=(0, 20))

cost_Label = Label(label_frame, text='Cost: %s' % cost_so_far, font='Helvetica 12')
cost_Label.grid(row=5, stick=W, padx=(35, 0), pady=(0, 20))

visited_Label = Label(label_frame, text='Visited: %s' % num_of_visited_nodes, font='Helvetica 12')
visited_Label.grid(row=6, stick=W, padx=(35, 0), pady=(0, 20))

path_Label = Label(label_frame, text='%s' % path_info, font='Helvetica 12')
path_Label.grid(row=7, stick=W, padx=(35, 0), pady=(0, 10))

legend_Frame = Frame(status_Frame, width=400)
legend_Frame.pack(fill=Y, expand=1)

legend_canvas = Canvas(legend_Frame, width=165, bd=-2)
legend_canvas.pack(fill=Y, expand=1)

legend_canvas.create_text(90, 44, font='Helvetica 12', text='=  Start node')
legend_canvas.create_text(88, 88, font='Helvetica 12', text='=  End node')
legend_canvas.create_text(92, 132, font='Helvetica 12', text='=  Open node')
legend_canvas.create_text(93, 176, font='Helvetica 12', text='=  Close node')
legend_canvas.create_text(88, 220, font='Helvetica 12', text='=  Path node')
legend_canvas.create_text(103, 264, font='Helvetica 12', text='=  Unvisited node')
legend_canvas.create_text(102, 308, font='Helvetica 12', text='=  Obstacle node')

startLegend = legend_canvas.create_rectangle(6, 26, 35, 56, fill=start_color)
endLegend = legend_canvas.create_rectangle(6, 70, 35, 100, fill=end_color)
openLegend = legend_canvas.create_rectangle(6, 115, 35, 145, fill=open_color)
closeLegend = legend_canvas.create_rectangle(6, 160, 35, 190, fill=close_color)
pathLegend = legend_canvas.create_rectangle(6, 205, 35, 235, fill=path_color)
unvisitedLegend = legend_canvas.create_rectangle(6, 249, 35, 279, fill='white')
obstacleLegend = legend_canvas.create_rectangle(6, 293, 35, 323, fill='black')

# ******* Canvas *******
gridCanvas = DisplayCanvas(root, canvas_width, canvas_height, LEFT)

# ******* Buttons *******
button_Map_Settings = Button(toolbar, text='Settings', font='Helvetica 10')
button_Map_Settings.bind('<Button-1>', lambda event: show_settings_window(gridCanvas.getCanvas()))
button_Map_Settings.pack(side=LEFT, padx=5, pady=5)

button_Clear = Button(toolbar, text='Clear', font='Helvetica 10')
button_Clear.bind('<Button-1>', lambda event: clear(gridCanvas.getCanvas()))
button_Clear.pack(side=LEFT, padx=5, pady=5)

button_Play = Button(toolbar, text='Play', font='Helvetica 10')
button_Play.bind('<Button-1>', lambda event: setAlgorithm(gridCanvas))
button_Play.pack(side=LEFT, padx=5, pady=5)

button_Random = Button(toolbar, text='Random', font='Helvetica 10')
button_Random.bind('<Button-1>', lambda event: randomObstacle(gridCanvas.getCanvas()))
button_Random.pack(side=LEFT, padx=5, pady=5)

button_Maze = Button(toolbar, text='Maze', font='Helvetica 10')
button_Maze.bind('<Button-1>', lambda event: show_maze(gridCanvas.getCanvas()))
button_Maze.pack(side=LEFT, padx=5, pady=5)

# ******* Checkbox *******
isChecked = IntVar()
checkbox_move = Checkbutton(toolbar, text='Allow diagonal movement', font='Helvetica 10', onvalue=1, offvalue=0, variable=isChecked, command=lambda: showOptionMenu())
checkbox_move.pack(side=LEFT, padx=5, pady=7)

borderAllowed = IntVar()
checkbox_border = Checkbutton(toolbar, text='Show border', font='Helvetica 10', onvalue=1, offvalue=0, variable=borderAllowed, command=lambda: showBorder(gridCanvas.getCanvas()))
checkbox_border.select()
checkbox_border.pack(side=LEFT, padx=5, pady=7)

# ******* Dropdown *******

heur_style = ttk.Style()
heur_style.configure('heur.TMenubutton', font=('Helvetica', 10))

heur_4moves_options = ['', 'Manhattan distance', 'Euclidean distance']
heur_4moves_value = StringVar()
heur_4moves_value.set(heur_4moves_options[1])

heur_4moves_optionMenu = DisplayOptionMenu(gridCanvas.getCanvas(), toolbar, heur_4moves_options, heur_4moves_value, 'heur.TMenubutton').getOptionMenu()

heur_8moves_options = ['', 'Chebyshev distance', 'Octile distance', 'Euclidean distance']
heur_8moves_value = StringVar()
heur_8moves_value.set(heur_8moves_options[1])

heur_8moves_optionMenu = DisplayOptionMenu(gridCanvas.getCanvas(), toolbar, heur_8moves_options, heur_8moves_value, 'heur.TMenubutton').getOptionMenu()
heur_8moves_optionMenu.pack_forget()

# ******* Grid *******
grid = [[0 for j in range(columns)] for i in range(rows)]

for i in range(columns):
    for j in range(rows):
        grid[i][j] = Node(None, (i, j))

for i in range(columns):
    for j in range(rows):
        grid[i][j].show(gridCanvas.getCanvas())
        grid[i][j].addNeighbors()

grid[start[0]][start[1]].show(gridCanvas.getCanvas(), fill=start_color)
grid[destination[0]][destination[1]].show(gridCanvas.getCanvas(), fill=end_color)

mainloop()
