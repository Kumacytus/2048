# Logic
from numpy import random, array, zeros, append, sum, concatenate, copy, ndenumerate, isnan, rot90, nan, int, float
DOWN, RIGHT, UP, LEFT = range(4)

class Game2048:
    def __init__(self):
        self._grid, self._score = zeros(16) + nan, 0
        self._grid[random.choice(16, 2, replace=False)] = random.choice([2]*9+[4], 2, replace=False) # init with 2 tiles
        self._grid = self._grid.reshape((4, 4))  # create 4x4 grid

    @staticmethod
    def _merge_down(grid):
        merge = concatenate((grid, [zeros(4) + nan])) - concatenate(([zeros(4) + nan], grid))  # find the mergable tiles
        merge[2][merge[3]==0], merge[1][merge[2]==0] = nan, nan     # remove redundant 0 by 3 same tiles
        score = sum(grid[merge[:4] == 0])
        grid[merge[:4] == 0], grid[merge[1:] == 0] = grid[merge[:4] == 0] * 2, nan # fill the merged  with new number
        return score

    def _create_tiles(self):
        avail = isnan(self._grid)
        if avail[avail==True].size > 0:
            new_tiles = append(random.choice([20]*9+[40]), zeros(avail[avail==True].size - 1) + nan)
            random.shuffle(new_tiles)
            self._grid[avail] = new_tiles

    def step(self, direction):
        self._grid[self._grid%10==0] /= 10
        merge_v, merge_h, grid_copy = copy(self._grid), copy(rot90(self._grid)), copy(self._grid)
        map(Game2048._merge_down, [merge_v, merge_h])       # try to merge tiles along two directions
        if merge_v[isnan(merge_v)].size is 0 and merge_h[isnan(merge_h)].size is 0:         # Check if game is over
            return False
        self._grid = rot90(self._grid, RIGHT - direction)
        self._grid = array([concatenate((x[isnan(x)], x[~isnan(x)])) for x in self._grid])  # move tiles
        self._grid = rot90(self._grid, -1)
        self._score += Game2048._merge_down(self._grid)                                     # merge tiles
        self._grid = rot90(self._grid, 1)
        self._grid = array([concatenate((x[isnan(x)], x[~isnan(x)])) for x in self._grid])  # move tiles
        self._grid = rot90(self._grid, direction - RIGHT)
        if not ((self._grid == grid_copy) | (isnan(self._grid) & isnan(grid_copy))).all():
            self._create_tiles()
        return True

    def get_grid(self):
        grid = copy(self._grid)
        grid[grid%10==0] /= 10
        return grid

    def get_new_tiles(self):
        grid = zeros((4, 4), int)
        grid[self._grid%10==0] = 1
        return grid

    def get_score(self):
        return self._score


# GUI
from Tkinter import Tk, Label, Frame, BOTH
from tkFont import Font
from game2048 import Game2048, UP, DOWN, LEFT, RIGHT, ndenumerate, copy, isnan

key_map = {'Up': UP, 'Down': DOWN, 'Left': LEFT, 'Right': RIGHT}
color_map = {2: ('#776e65', '#eee4da'), 4: ('#776e65', '#ede0c8'), 8: ('#f9f6f2', '#f2b179'), 16: ('#f9f6f2', '#f2b179'),
             32: ('#f9f6f2', '#f67c5f'), 64: ('#f9f6f2', '#f65e3b'), 128:('#f9f6f2', '#edcf72'), 256: ('#f9f6f2', '#edcc61'),
             512: ('#f9f6f2', '#edc850'), 1024: ('#f9f6f2', '#edc53f'), 2048: ('#f9f6f2', '#edc22e'), 'base': '#ccc0b3'}
color_map.update(dict.fromkeys([2**x for x in range(12, 18)], ('#f9f6f2', '#3c3a32')))

def input_listener(event=None, game=None, tk_root=None, labels=None):
    key = '{}'.format(event.keysym)
    if key in key_map and game and labels and tk_root:
        if game.step(key_map[key]):
            grid, new_tiles, score = game.get_grid(), game.get_new_tiles(), int(game.get_score())
            max_tile = int(grid[~isnan(grid)].max())
            tk_root.title('Move tiles to get {}! Score: {}'.format(2048 if max_tile < 2048 else max_tile * 2, score))
            for (i, j), value in ndenumerate(grid):
                text = '{}'.format('' if isnan(grid[i][j]) else int(grid[i][j]))
                font_color = color_map[32][1] if new_tiles[i][j] else color_map['base'] if isnan(value) else color_map[value][0]
                labels[4*i+j].config(text=text, fg=font_color, bg=color_map['base'] if isnan(value) else color_map[value][1])
        else:
            grid, new_tiles, score = game.get_grid(), game.get_new_tiles(), int(game.get_score())
            max_tile = int(grid[~isnan(grid)].max())
            [labels[i].config(text='' if i < 4 or i > 11 else 'GAMEOVER'[i-4], bg=color_map['base']) for i in xrange(16)]
            tk_root.title('Game Over! Tile acheived: {}, Score: {}'.format(max_tile, score))

if __name__ == '__main__':
    game, root, window_size = Game2048(), Tk(), 360
    root.title('Move tiles to get 2048! Score: 0')
    root.geometry('{0}x{0}+111+111'.format(window_size))
    root.config(background='#bbada0')

    grid, labels = game.get_grid(), []
    for (i, j), value in ndenumerate(grid):
        frame = Frame(root, width=window_size/4-2, height=window_size/4-2)
        font = Font(family='Helvetica', weight='bold', size=window_size/15)
        frame.pack_propagate(0)
        frame.place(x=j*window_size/4+1, y=i*window_size/4+1)
        (text, color) = ('', color_map['base']) if isnan(value) else ('{}'.format(int(value)), color_map[value][0])
        label = Label(frame, text=text, font=font, fg=color, bg=color_map['base'] if isnan(value) else color_map[value][1])
        label.pack(fill=BOTH, expand=True)
        labels.append(label)

    root.bind_all('<Key>', lambda event: input_listener(event, game=game, tk_root=root, labels=labels))
    root.mainloop()
