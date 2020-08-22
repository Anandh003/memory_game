from random import shuffle
from typing import Text
import pygame
from pygame.locals import QUIT, MOUSEMOTION, MOUSEBUTTONUP, K_y, K_n, K_s
import sys

GRAY = (100, 100, 100)
NAVY_BLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255,   0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)


class Board:
    def __init__(self):
        self.ROWS = 7
        self.COLUMNS = 10

        self.ALL_COLORS = (
            GRAY,
            RED,
            GREEN,
            BLUE,
            YELLOW,
            ORANGE,
            PURPLE,
            CYAN,
            BLACK
        )
        self.ALL_SHAPES = (
            'donut',
            'square',
            'diamond',
            'line',
            'oval'
        )
        assert \
            (len(self.ALL_COLORS) * len(self.ALL_SHAPES) * 2
                > self.ROWS * self.COLUMNS), \
            'Board is too big for the number of shapes/colors defined.'
        self.board = []
        self.initialize_board()
        self.revealed_boxes = self.init_revealed_boxes(False)

    def __getitem__(self, pos):
        pos_x, pos_y = pos
        return self.board[pos_x][pos_y]

    def init_revealed_boxes(self, isreveal):
        return [[isreveal] * self.COLUMNS for _ in range(self.ROWS)]

    def initialize_board(self):
        board = []
        for color in self.ALL_COLORS:
            for shape in self.ALL_SHAPES:
                board.append((shape, color))
        board = board[:(self.ROWS * self.COLUMNS) // 2] * 2
        shuffle(board)
        for row in range(self.ROWS):
            self.board.append(board[row * self.COLUMNS:(row+1) * self.COLUMNS])


class Game:
    def __init__(self):
        self.BG_COLOR = (60, 60, 100)
        self.board = Board()
        self.BOX_SIZE = 40
        self.GAP_SIZE = 10
        self.BOX_COLOR = (255, 255, 255)
        self.game_width = 640
        self.game_height = 480
        self.X_MARGIN = (
            self.game_width
            - (self.board.COLUMNS * (self.BOX_SIZE + self.GAP_SIZE))
        ) // 2
        self.Y_MARGIN = (
            self.game_height
            - (self.board.ROWS * (self.BOX_SIZE + self.GAP_SIZE))
        ) // 2
        self.FPS_CLOCK = pygame.time.Clock()
        self.FPS = 30
        self.mouse_x = 0
        self.mouse_y = 0
        self.reveal_speed = 8
        self.hilight_color = BLUE
        pygame.init()
        self.SCREEN = pygame.display.set_mode(
            (self.game_width, self.game_height)
        )
        self.SCREEN.fill(self.BG_COLOR)
        # while True:
        self.start_game_animation()

    def start_game_animation(self):
        boxes = [(x, y) for x in range(self.board.ROWS)
                 for y in range(self.board.COLUMNS)
                 ]
        shuffle(boxes)
        self.draw_board(self.board.revealed_boxes)
        box_groups = [boxes[box: box+8] for box in range(0, len(boxes), 8)]
        for box_group in box_groups:
            self.reveal_box(box_group)
            self.cover_box(box_group)

    def draw_board(self, reveled_boxes):
        for box_x in range(self.board.ROWS):
            for box_y in range(self.board.COLUMNS):
                left, top = self.find_left_top_coordinates((box_x, box_y))
                if not reveled_boxes[box_x][box_y]:
                    pygame.draw.rect(
                        self.SCREEN,
                        self.BOX_COLOR,
                        (left, top, self.BOX_SIZE, self.BOX_SIZE)
                    )
                else:
                    shape, color = self.find_shape_color((box_x, box_y))
                    self.draw_icon((box_x, box_y), shape, color)

    def cover_box(self, boxes_to_cover):
        for coverage in range(
            0,
            self.BOX_SIZE+self.reveal_speed,
            self.reveal_speed
        ):
            self.draw_box_covers(boxes_to_cover, coverage)

    def reveal_box(self, boxes_to_reveal):
        for coverage in range(
             self.BOX_SIZE,
             -(self.reveal_speed) - 1,
             -self.reveal_speed
        ):
            self.draw_box_covers(boxes_to_reveal, coverage)

    def draw_box_covers(self, boxes, coverage):
        for box in boxes:
            left, top = self.find_left_top_coordinates(box)
            pygame.draw.rect(
                self.SCREEN,
                self.BOX_COLOR,
                (left, top, self.BOX_SIZE, self.BOX_SIZE)
            )
            shape, color = self.find_shape_color(box)
            self.draw_icon(box, shape, color)
            if coverage > 0:
                pygame.draw.rect(
                    self.SCREEN,
                    self.BOX_COLOR,
                    (left, top, coverage, self.BOX_SIZE)
                )
        pygame.display.update()
        self.FPS_CLOCK.tick(self.FPS)

    def find_left_top_coordinates(self, box):
        left_position = (
            (box[1] * (self.GAP_SIZE + self.BOX_SIZE))
            + self.X_MARGIN
        )
        top_position = (
            (box[0] * (self.GAP_SIZE + self.BOX_SIZE))
            + self.Y_MARGIN
        )
        return left_position, top_position

    def draw_icon(self, box, shape, color):
        quater = int(self.BOX_SIZE * 0.25)
        half = int(self.BOX_SIZE * 0.5)

        left, top = self.find_left_top_coordinates(box)
        if shape == 'donut':
            pygame.draw.circle(
                self.SCREEN, color,
                (left+half, top+half),
                half - 5
            )
            pygame.draw.circle(
                self.SCREEN,
                self.BG_COLOR,
                (left+half, top+half),
                quater - 5
                )
        elif shape == 'square':
            pygame.draw.rect(
                self.SCREEN,
                color,
                (
                 left + quater,
                 top + quater,
                 self.BOX_SIZE - half,
                 self.BOX_SIZE - half
                )
            )
        elif shape == 'diamond':
            pygame.draw.polygon(
                self.SCREEN,
                color,
                (
                    (left + half, top),
                    (left + self.BOX_SIZE - 1, top + half),
                    (left + half, top + self.BOX_SIZE - 1),
                    (left, top + half)
                )
            )
        elif shape == 'oval':
            pygame.draw.ellipse(
                self.SCREEN,
                color,
                (left, top + quater, self.BOX_SIZE, half)
            )
        elif shape == 'line':
            for i in range(0, self.BOX_SIZE, 4):
                pygame.draw.line(
                    self.SCREEN,
                    color,
                    (left, top + i), (left + i, top)
                )
                pygame.draw.line(
                    self.SCREEN,
                    color,
                    (left + i, top + self.BOX_SIZE - 1),
                    (left + self.BOX_SIZE - 1, top + i)
                )

    def find_shape_color(self, box):
        box_x, box_y = box
        return self.board[box_x, box_y]

    def get_box_at_pixel(self, x_coordinate, y_coordinate):
        for row in range(self.board.ROWS):
            for column in range(self.board.COLUMNS):
                left, top = self.find_left_top_coordinates((row, column))
                box_rect = pygame.Rect(left, top, self.BOX_SIZE, self.BOX_SIZE)
                if box_rect.collidepoint((x_coordinate, y_coordinate)):
                    return row, column
        return None, None

    def highlight_box(self, box):
        left, top = self.find_left_top_coordinates(box)
        pygame.draw.rect(
            self.SCREEN,
            self.hilight_color,
            (left - 5, top - 5, self.BOX_SIZE + 10, self.BOX_SIZE + 10),
            4
        )

    def has_won(self):
        for i in self.board.revealed_boxes:
            if False in i:
                return False
        return True

    def won_game_animation(self):
        for i in range(13):
            self.SCREEN.fill(GRAY)
            self.draw_board(self.board.revealed_boxes)

    def ask_again(self):
        self.SCREEN.fill(BLACK)
        text = pygame.font.SysFont('Comic Sans MS', 30)
        text_sur = text.render(
            'You WIN !!! Do you want to continue? (y/n)',
            True,
            WHITE
        )
        text_width = text_sur.get_width()
        text_height = text_sur.get_height()
        self.SCREEN.blit(
            text_sur,
            (
                (self.game_width - text_width) // 2,
                (self.game_height // 2) - text_height
            )
        )
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_y:
                            self.check_new_game = False
                            self.board = Board()
                            self.start_game_animation()
                        elif event.key == K_n:
                            self.check_new_game = False
                            pygame.quit()
                            sys.exit()

    def start(self):
        first_selection = None
        while True:
            mouse_clicked = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    self.mouse_x, self.mouse_y = event.pos
                elif event.type == MOUSEBUTTONUP:
                    self.mouse_x, self.mouse_y = event.pos
                    mouse_clicked = True
                elif event.type == pygame.KEYDOWN and event.key == K_s:
                    self.board.revealed_boxes = (
                        self.board.init_revealed_boxes(True)
                    )

            self.SCREEN.fill(self.BG_COLOR)
            self.draw_board(self.board.revealed_boxes)
            box_x, box_y = self.get_box_at_pixel(self.mouse_x, self.mouse_y)

            if box_x is not None and box_y is not None:
                # print(f'Box Positon: {box_x} {box_y}')
                if not self.board.revealed_boxes[box_x][box_y]:
                    self.highlight_box((box_x, box_y))
                if (
                    not self.board.revealed_boxes[box_x][box_y] and
                    mouse_clicked
                ):
                    self.reveal_box([(box_x, box_y)])
                    self.board.revealed_boxes[box_x][box_y] = True
                    if not first_selection:
                        first_selection = (box_x, box_y)
                    else:
                        box1_x, box1_y = first_selection
                        icon_shape_1, icon_color_1 = self.find_shape_color(
                            (box1_x, box1_y)
                        )
                        icon_shape_2, icon_color_2 = self.find_shape_color(
                            (box_x, box_y)
                        )
                        if (
                            icon_shape_1 != icon_shape_2 or
                            icon_color_1 != icon_color_2
                        ):
                            pygame.time.wait(750)
                            self.cover_box([(box1_x, box1_y), (box_x, box_y)])
                            self.board.revealed_boxes[box_x][box_y] = False
                            self.board.revealed_boxes[box1_x][box1_y] = False
                        elif self.has_won():
                            self.won_game_animation()
                            self.ask_again()

                        first_selection = None
                self.ask_again()

            pygame.display.update()
            self.FPS_CLOCK.tick(self.FPS)


game = Game()
game.start()
