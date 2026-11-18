from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовые атрибуты игрового объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле."""
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self, position=None, body_color=APPLE_COLOR):
        """Инициализирует яблоко."""
        super().__init__(position, body_color)
        if position is None:
            self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайное положение яблока на поле."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку на игровом поле."""

    def __init__(self, position=None, body_color=SNAKE_COLOR):
        """Инициализирует змейку."""
        super().__init__(position, body_color)
        self.apple = None
        self.last = None
        self.reset()
        if position is not None:
            self.position = position
            self.positions = [position]

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку в текущем направлении."""
        cur_head = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (cur_head[0] + dx * GRID_SIZE) % SCREEN_WIDTH,
            (cur_head[1] + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)
        self.position = new_head
        if self.apple is not None and new_head == self.apple.position:
            self.apple.randomize_position()
        else:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.positions = [self.position]
        self.direction = choice([RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает события клавиатуры и закрытия окна."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            directions = {
                pygame.K_UP: (UP, DOWN),
                pygame.K_DOWN: (DOWN, UP),
                pygame.K_LEFT: (LEFT, RIGHT),
                pygame.K_RIGHT: (RIGHT, LEFT),
            }
            if event.key in directions:
                new_dir, forbidden = directions[event.key]
                if game_object.direction != forbidden:
                    game_object.next_direction = new_dir


def main():
    """Основной игровой цикл."""
    pygame.init()
    apple = Apple()
    snake = Snake()
    snake.apple = apple

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
