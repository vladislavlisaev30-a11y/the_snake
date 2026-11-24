from random import randint

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

# Цвет фона - тёмно-синий, чтобы поле не сливалось с рамкой окна:
BOARD_BACKGROUND_COLOR = (24, 26, 42)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Стартовая скорость движения змейки, кадров в секунду:
SPEED = 6
# Прибавка к скорости за каждое съеденное яблоко:
SPEED_STEP = 1
# Предельная скорость движения змейки:
MAX_SPEED = 12

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

    def randomize_position(self, snake_positions=None):
        """Устанавливает случайное положение яблока на поле."""
        occupied = snake_positions or ()
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied:
                self.position = position
                return

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
        self.apples = []
        self.last = None
        self.score = 0
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
        ate_apple = False
        for apple in self.apples:
            if new_head == apple.position:
                other_positions = [
                    a.position for a in self.apples if a is not apple
                ]
                apple.randomize_position(self.positions + other_positions)
                self.score += 1
                self.last = None
                ate_apple = True
                break

        if not ate_apple:
            self.last = self.positions.pop()
        self.length = len(self.positions)

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions[1:]:
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
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.score = 0
        apples = getattr(self, 'apples', [])
        occupied = list(self.positions)
        for apple in apples:
            apple.randomize_position(occupied)
            occupied.append(apple.position)


def handle_keys(game_object):
    """Обрабатывает события клавиатуры и закрытия окна."""
    for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_object.reset()
                continue
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
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


def draw_buttons(buttons=None):
    """Отрисовывает кнопки перезапуска и выхода на игровом поле."""
    if not pygame.font.get_init():
        pygame.font.init()
    btn_restart = pygame.Rect(444, 8, 90, 26)
    btn_exit = pygame.Rect(542, 8, 90, 26)
    if isinstance(buttons, dict):
        btn_restart = buttons.get('restart', btn_restart)
        btn_exit = buttons.get('exit', btn_exit)
    elif isinstance(buttons, (list, tuple)) and len(buttons) >= 2:
        btn_restart, btn_exit = buttons[0], buttons[1]

    font = pygame.font.SysFont('arial', 16)
    for rect, label in ((btn_restart, 'Заново'), (btn_exit, 'Выход')):
        pygame.draw.rect(screen, (70, 70, 70), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))


def handle_buttons(buttons, snake, apples=None):
    """Обрабатывает клики мыши по кнопкам управления."""
    btn_restart = pygame.Rect(444, 8, 90, 26)
    btn_exit = pygame.Rect(542, 8, 90, 26)
    if isinstance(buttons, dict):
        btn_restart = buttons.get('restart', btn_restart)
        btn_exit = buttons.get('exit', btn_exit)
    elif isinstance(buttons, (list, tuple)) and len(buttons) >= 2:
        btn_restart, btn_exit = buttons[0], buttons[1]

    for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
        if event.button == 1:
            if btn_restart.collidepoint(event.pos):
                snake.reset()
                if apples and not getattr(snake, 'apples', None):
                    occupied = list(snake.positions)
                    for apple in apples:
                        apple.randomize_position(occupied)
                        occupied.append(apple.position)
            elif btn_exit.collidepoint(event.pos):
                pygame.quit()
                raise SystemExit


def main():
    """Основной игровой цикл."""
    pygame.init()
    score_font = pygame.font.SysFont('arial', 18)
    snake = Snake()
    apples = []
    occupied = list(snake.positions)
    for _ in range(3):
        apple = Apple()
        apple.randomize_position(occupied)
        occupied.append(apple.position)
        apples.append(apple)
    snake.apples = apples

    buttons = {
        'restart': pygame.Rect(444, 8, 90, 26),
        'exit': pygame.Rect(542, 8, 90, 26),
    }

    while True:
        speed = min(SPEED + snake.score * SPEED_STEP, MAX_SPEED)
        clock.tick(speed)
        handle_keys(snake)
        handle_buttons(buttons, snake, apples)
        pygame.event.clear()
        snake.update_direction()
        snake.move()
        screen.fill(BOARD_BACKGROUND_COLOR)
        for apple in snake.apples:
            apple.draw()
        snake.draw()
        draw_buttons(buttons)
        score_text = score_font.render(
            f'Очки: {snake.score}', True, (255, 255, 255)
        )
        screen.blit(score_text, (10, 10))
        pygame.display.update()


if __name__ == '__main__':
    main()
