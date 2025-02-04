import pygame
import os
import sys
import random
import math
import sql_work
import time

# Инициализация Pygame
pygame.init()

pygame.display.set_caption('Пикма dog')

# Настройки экрана
SCREEN_SIZE = WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode(SCREEN_SIZE, vsync=1)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (224, 93, 125)
BUTTON_HOVER_COLOR = (230, 116, 142)

# Шрифты
FONT = pygame.font.Font('TeletactileRus.ttf', 74)
BUTTON_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font('TeletactileRus.ttf', 30)

# Часы и FPS
clock = pygame.time.Clock()
FPS = 60

button_rect = pygame.Rect(WIDTH - 950, HEIGHT // 8 + 60, 200, 50)
nick = ''


def load_photo(filename, xsize=None):
    fullname = os.path.join('main_data', filename)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except Exception as e:
        print(f'Не удалось загрузить файл {filename}, Ошибка: {e}')
        raise SystemExit(e)

    if xsize is not None:
        w, h = image.get_size()
        new_size = (int(w * xsize), int(h * xsize))
        image = pygame.transform.scale(image, new_size)

    return image


icon = load_photo('icon.png')
pygame.display.set_icon(icon)


def load_particle(filename, xsize=None):
    fullname = os.path.join('main_data', 'particles', filename)
    image = pygame.image.load(fullname).convert_alpha()

    if xsize is not None:
        w, h = image.get_size()
        new_size = (int(w * xsize), int(h * xsize))
        image = pygame.transform.scale(image, new_size)

    return image


def draw_login_button(is_login=False, nick=None):
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect)

    text = SMALL_FONT.render(nick if is_login else "Войти", True, WHITE)
    text_x = button_rect.x + (button_rect.width // 2 - text.get_width() // 2)
    screen.blit(text, (text_x, button_rect.y + 10))


def draw_button(text, x, y):
    button_rect = pygame.Rect(x, y, 220, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    label = SMALL_FONT.render(text, True, WHITE)
    label_x = x + (10 if text != 'Выйти' else 60)
    screen.blit(label, (label_x, y + 10))
    return button_rect


def button_y(bh, bg):
    return (HEIGHT - (bh * 4 + bg * (4 - 1))) // 2


BUTTON_HEIGHT = 122
BUTTON_GAP = 20  # Отступ между кнопками
buttons = {
    'Играть': (load_photo('ИГРАТЬ.png', 1.75), ((WIDTH - 350) // 2, button_y(BUTTON_HEIGHT, BUTTON_GAP))),
    'Лидеры': (load_photo('ЛИДЕРЫ.png', 1.75), (
        (WIDTH - 350) // 2, button_y(BUTTON_HEIGHT, BUTTON_GAP) + BUTTON_HEIGHT // 1.5 + BUTTON_GAP)),
    'Магазин': (load_photo('МАГАЗИН.png', 1.75), (
        (WIDTH - 350) // 2, button_y(BUTTON_HEIGHT, BUTTON_GAP) + 2 * (BUTTON_HEIGHT // 1.5 + BUTTON_GAP))),
    'Выход': (load_photo('ВЫХОД.png', 1.75), (
        (WIDTH - 350) // 2, button_y(BUTTON_HEIGHT, BUTTON_GAP) + 3 * (BUTTON_HEIGHT // 1.5 + BUTTON_GAP)))
}


def terminate():
    pygame.quit()
    sys.exit()


# Загрузка текстур
textures = [
    [load_photo('flower.png', 1.25), load_photo('flower.png', 1.2).get_rect().height],
    [load_photo('carrier.png', 1.25), load_photo('carrier.png', 1.2).get_rect().height],
    [load_photo('packet.png', 1.25), load_photo('packet.png', 1.2).get_rect().height]
]

buffs = {
    1: [load_photo('clock.png', xsize=2), 'freeze_time'],
    2: [load_photo('barrier_icon.png', xsize=2), 'barrier'],
    3: [load_photo('dj_icon.png', xsize=2), 'bow']
}

particles_textures = {
    textures[0][0]: [load_particle('ff_1.png'), load_particle('ff_2.png'), load_particle('ff_3.png'),
                     load_particle('ff_4.png')],
    textures[1][0]: [load_particle('cf_1.png'), load_particle('cf_2.png'), load_particle('cf_3.png'),
                     load_particle('cf_4.png')],
    textures[2][0]: [load_particle('pf_1.png'), load_particle('pf_2.png'), load_particle('pf_3.png'),
                     load_particle('pf_4.png')]
}

all_skins = {
    '1': [load_photo('red_skin.png'), (), (950, 70)],
    '2': [load_photo('orange_skin.png'), (), (950, 200)],
    '3': [load_photo('green_skin.png'), (), (950, 320)],
    '4': [load_photo('blue_skin.png'), (), (950, 460)],
    '5': [load_photo('gold_bow.png'), (), (950, 600)]
}

# Загрузка текстур для различных элементов
coin_texture = load_photo('coin.png', 1.25)
equip_icon = load_photo('equip.png')
barrier_texture = load_photo('barrier_texture.png')
slow_jump_texture = load_photo('dj.png')
pause_icon = load_photo('pause.png')
test_texture_bg = load_photo('bg.png')
ex = load_photo('ex.png')

# Позиционирование элемента
ex_rect = ex.get_rect()
ex_rect.x, ex_rect.y = WIDTH - 760, HEIGHT // 8 + 115

# Загрузка изображений для счета
score_frame = load_photo('score_box.png')

# Загрузка изображений чисел от 0 до 9
images = {str(i): load_photo(f'{i}.png') for i in range(10)}

# Активный буст
enable_buff = False

# Инициализация переменных
score, money = 0, 0
nickname = ''
eq_skin = None


def calculate_y_position(img):
    if img == textures[1]:
        return HEIGHT - (180 + img[1])
    elif img == textures[2]:
        return HEIGHT - (190 + img[1] + 10)
    return HEIGHT - (190 + img[1])


class Obstacle:
    def __init__(self):
        global enable_buff
        heights = [player_rect.height, 200, player_rect.height - 30]

        self.buff = False
        self.speed = 10

        if random.randint(1, 100) <= 15 and not enable_buff:
            self.buff = True
            enable_buff = True
            buff = random.randint(1, 3)
            self.image = buffs[buff][0]
            self.buff_type = buffs[buff][1]
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH
            self.rect.y = HEIGHT - (190 + random.choice(heights))
        else:
            img = random.choice(textures)
            self.image = img[0]
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH
            self.rect.y = calculate_y_position(img)

    def move(self):
        self.rect.x -= self.speed  # Скорость движения препятствия

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Coin:
    def __init__(self):
        heights = [player_rect.height, 200, player_rect.height - 30]
        self.img = coin_texture
        self.speed = 10
        self.rect = self.img.get_rect()
        self.rect.x = WIDTH
        self.rect.y = HEIGHT - (190 + random.choice(heights))

    def move(self):
        self.rect.x -= self.speed

    def draw(self, surface):
        surface.blit(self.img, self.rect)


screen_rect = (0, 0, WIDTH, HEIGHT)
gravity = 0.25
all_sprites = pygame.sprite.Group()


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, obst):
        super().__init__(all_sprites)
        self.fire = particles_textures[obst.image]
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # У каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # И свои координаты
        self.rect.x, self.rect.y = pos

        # Гравитация будет одинаковой
        self.gravity = gravity

    def update(self):
        # Применяем гравитационный эффект
        self.velocity[1] += self.gravity
        # Перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # Убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position, radius, obst):
    particle_count = 20
    numbers = range(-5, 6)

    for _ in range(particle_count):
        # Вычисляем угол для каждой частицы
        angle = random.uniform(0, 2 * math.pi)
        # Вычисляем скорость на основе угла
        speed = radius * math.sin(angle) * random.choice(numbers)
        # Вычисляем вектор направления, используя угол
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        Particle(position, dx, dy, obst)


def restart_game():
    global jump_vel, jv, temp_jump_diff, obstacles, coins, k
    global obs_frame, diff, left_diff, temp_diff, ground_x, bg_x
    global bg_speed, ground_speed, player, player_rect, player_y
    global original_y, is_jumping, is_down, key_press, jump_count
    global slow_time, bow_time, barrier_time, running, frame_cnt
    global buff_type, mbg_x, start_bg_speed, score, enable_buff

    # Параметры прыжка
    jump_vel = 9.5
    jv = 0.7
    temp_jump_diff = jv

    # Переменные состояния игры
    obstacles = []
    coins = []
    k = 0
    obs_frame = 0

    # Настройки сложности
    diff = 12
    left_diff = 200
    temp_diff = 12

    # Настройки фона и земли
    mbg_x = 0
    ground_x = 0
    bg_x = 0
    bg_speed = diff // 10
    ground_speed = diff

    # Настройки игрока
    player = run_imgs[1]
    player_rect = player.get_rect()
    player_rect.x = WIDTH // 8
    player_y = HEIGHT - player_rect.height - 176
    original_y = player_y
    score = 0

    # Флаги состояния игры
    is_jumping = False
    is_down = False
    key_press = None
    enable_buff = False

    # Механика прыжка
    jump_count = 11
    slow_time = 0
    bow_time = 0
    barrier_time = 0

    # Управление игровым циклом
    running = True
    frame_cnt = 0
    buff_type = None

    # Инициализация фона
    mbg_x = 0
    start_bg_speed = 2

    # Альфа-каналы иконок
    for i in range(1, 4):
        buffs[i][0].set_alpha(255)


def input_nickname(old_nick=''):
    global nickname, eq_skin, mbg_x
    input_active = True

    while input_active:

        screen.fill((0, 0, 0))
        screen.blit(start_bg, (mbg_x, 0))
        screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))
        if mbg_x <= -start_bg.get_width():
            screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))

        mbg_x -= 0.1

        if not nickname:
            draw_login_button()
        else:
            draw_login_button(True, nickname)
        for button in buttons:
            screen.blit(buttons[button][0], buttons[button][1])

        if len(nickname) == 11:
            if old_nick != nickname[:-1]:
                eq_skin = None
            return nickname[:-1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if ex_rect.collidepoint(mouse_pos):
                    return old_nick
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_SPACE:
                    continue
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    nickname += event.unicode

        pygame.draw.rect(screen, (103, 47, 61), (WIDTH - 950, HEIGHT // 8 + 120, 200, 35))
        input_surface = SMALL_FONT.render(nickname, True, (255, 255, 255))
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 950, HEIGHT // 8 + 120, 200, 35), 3)

        screen.blit(input_surface, (WIDTH - 945, HEIGHT // 8 + 120))
        screen.blit(ex, (WIDTH - 760, HEIGHT // 8 + 115))
        pygame.display.flip()

    if old_nick != nickname:
        eq_skin = None
    return nickname


def draw_nomoney():
    global mbg_x
    text = "Не достаточно монет!"
    text_surface = FONT.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    alpha = 255  # Прозрачность текста
    fade_out = True  # Флаг затухания

    while fade_out:
        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(start_bg, (mbg_x, 0))
        screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))

        if mbg_x <= -start_bg.get_width():
            mbg_x += start_bg.get_width()  # Зацикливание фона

        mbg_x -= 0.1  # Движение фона

        # Отрисовка элементов магазина
        screen.blit(shop_ground, (100, 40))
        screen.blit(shop_ex, (1075, 27))

        # Затухание текста
        alpha -= 0.2  # Уменьшаем прозрачность
        if alpha < 0:
            fade_out = False  # Остановить затухание

        # Отображение купленных скинов
        for index, skin in enumerate(skins):
            if skin in all_skins:
                item_rects[index] = None
                screen.blit(accept, all_skins[skin][2])

        # Отображение иконки выбранного скина
        for index, icon_rect in enumerate(icon_rects):
            if eq_skin == all_skins[str(index + 1)][0]:
                offset_y = 10 if index >= 3 else 0
                screen.blit(equip_icon, (icon_rect.x + 5, icon_rect.y + offset_y))

        pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 1050, HEIGHT // 2 - 50, 900, 100))
        text_surface.set_alpha(alpha)  # Установка прозрачности текста
        screen.blit(text_surface, text_rect)
        pygame.display.flip()


# Инициализация фона и других изображений
start_bg = load_photo('bg.png')
mbg_x = 0
start_bg_speed = 2
shop_ground = load_photo('shop_2.png')
accept = load_photo('accept.png')
lb_ground = load_photo('leaderbord.png')
lb_ground_2 = load_photo('leaderboard_2.png')


def leaderboard():
    global mbg_x
    top_10 = sql_work.get_top_10()

    shop_ex = load_photo('ex.png', 2.5)
    shop_ex_rect = shop_ex.get_rect(topleft=(1075, 27))

    while True:
        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(start_bg, (mbg_x, 0))
        screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))
        if mbg_x <= -start_bg.get_width():
            mbg_x += start_bg.get_width()

        mbg_x -= 0.1

        # Отрисовка элементов магазина
        screen.blit(lb_ground, (100, 40))
        screen.blit(shop_ex, (1075, 27))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.K_ESCAPE:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if shop_ex_rect.collidepoint(mouse_pos):
                    return

        yy = 65

        for player, score in top_10:
            player_text_surface = SMALL_FONT.render(f'{player}', True, WHITE)
            screen.blit(player_text_surface, (120, yy + 60))

            score_text_surface = SMALL_FONT.render(f'{score}', True, WHITE)
            screen.blit(score_text_surface, (375 if yy <= 200 else 350, yy + 60))
            yy += 60

        pygame.display.flip()


def shop(nick):
    global money, eq_skin, mbg_x, shop_ex, skins, item_rects, icon_rects

    shop_ex = load_photo('ex.png', 2.5)
    shop_ex_rect = shop_ex.get_rect(topleft=(1075, 27))

    # Определение прямоугольников для кнопок
    item_rects = [
        pygame.Rect(920, 50, 170, 115),
        pygame.Rect(920, 170, 170, 115),
        pygame.Rect(920, 300, 170, 115),
        pygame.Rect(920, 420, 170, 140),
        pygame.Rect(920, 570, 170, 140)
    ]

    icon_rects = [
        pygame.Rect(760, 50, 155, 115),
        pygame.Rect(760, 170, 155, 115),
        pygame.Rect(760, 300, 155, 115),
        pygame.Rect(760, 420, 155, 145),
        pygame.Rect(760, 570, 155, 145)
    ]

    while True:
        skins = sql_work.get_stat(nick, 'skins')
        skins = skins.split() if skins else []

        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(start_bg, (mbg_x, 0))
        screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))
        if mbg_x <= -start_bg.get_width():
            mbg_x += start_bg.get_width()

        mbg_x -= 0.1

        # Отрисовка элементов магазина
        screen.blit(shop_ground, (100, 40))
        screen.blit(shop_ex, (1075, 27))

        # Отображение купленных скинов
        for index, skin in enumerate(skins):
            if skin in all_skins:
                item_rects[index] = None
                screen.blit(accept, all_skins[skin][2])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.K_ESCAPE:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if shop_ex_rect.collidepoint(mouse_pos):
                    return

                # Проверка нажатия и покупка скинов
                for index, rect in enumerate(item_rects):
                    if rect and rect.collidepoint(mouse_pos):
                        price = (50, 100, 200, 500, 1000)[index]
                        if money >= price:
                            money -= price
                            sql_work.update_player(nickname, score, money, str(index + 1))
                            item_rects[index] = None
                        else:
                            draw_nomoney()

                # Проверка на выбор скина
                for index, icon_rect in enumerate(icon_rects):
                    if icon_rect.collidepoint(mouse_pos) and str(index + 1) in skins:
                        eq_skin = all_skins[str(index + 1)][0]

        # Отображение иконки выбранного скина
        for index, icon_rect in enumerate(icon_rects):
            if eq_skin == all_skins[str(index + 1)][0]:
                offset_y = 10 if index >= 3 else 0
                screen.blit(equip_icon, (icon_rect.x + 5, icon_rect.y + offset_y))

        pygame.display.flip()


def start_screen():
    global score, money, nickname, mbg_x

    while True:
        screen.fill(BLACK)

        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(start_bg, (mbg_x, 0))
        screen.blit(start_bg, (mbg_x + start_bg.get_width(), 0))
        if mbg_x <= -start_bg.get_width():
            mbg_x += start_bg.get_width()

        mbg_x -= 0.1

        # Отрисовка кнопки входа
        draw_login_button(True, nickname) if nickname else draw_login_button()

        # Отрисовка всех кнопок
        for button in buttons:
            screen.blit(buttons[button][0], buttons[button][1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for name, btn in buttons.items():
                    hit_box = btn[0].get_rect(topleft=btn[1])
                    hit_box.inflate_ip(-85, -52)  # Уменьшение hitbox
                    hit_box.topleft = (hit_box.x, hit_box.y)
                    if hit_box.collidepoint(mouse_pos):
                        if name != 'Играть':
                            handle_button_click(name)
                        else:
                            return
                if button_rect.collidepoint(event.pos):
                    nickname = input_nickname(nickname)
                    if nickname:
                        stats = sql_work.get_player(nickname)
                        money = stats[1] if stats else 0
                        score = 0  # Сбросить счет, если игрок новый

        pygame.display.flip()


def handle_button_click(name):
    if name == "Магазин":
        shop(nickname)
    elif name == "Лидеры":
        leaderboard()
    elif name == "Выход":
        pygame.quit()
        sys.exit()


# Запуск стартового экрана
start_screen()

# Загрузка изображений
run_imgs = [load_photo('first_step.png'), load_photo('idle.png'), load_photo('third_step.png')]
step_index = 0
DOWN = load_photo('dog_down.png')

player = run_imgs[1]
player_rect = player.get_rect(topleft=(WIDTH // 8, HEIGHT - player.get_height() - 176))
player_hitbox = pygame.Rect(
    player_rect.x + 5,
    player_rect.y + 65,
    player_rect.width - 25,
    player_rect.height - 36
)

# Игровые переменные
is_jumping = False
is_down = False
jump_count = 11
slow_time = 0
bow_time = 0
barrier_time = 0
running = True
frame_cnt = 0
buff_type = None
key_press = None
player_y = HEIGHT - player_rect.height - 176
original_y = player_y

# Список препятствий
obstacles = []
coins = []
k = 0
obs_frame = 0
diff = 12
left_diff = 200
temp_diff = 12

fg = load_photo('fg_texture.png')
bg = load_photo('bg.png')
ground_x = 0
bg_x = 0
bg_speed = diff // 10
ground_speed = diff

# jump
DJU = load_photo('dog_jump_up.png')
DJD = load_photo('dog_jump_down.png')
jump_vel = 9.5
JUMP_VEL = 9.5
jv = 0.7
temp_jump_diff = jv

# Переменные для затухания
fade_duration = 8  # Время затухания в секундах
fade_steps = 60  # Количество шагов обновления в секунду
fade_out_steps = fade_duration * fade_steps
alpha_step = 255 / fade_out_steps
current_step = 0


def pause():
    global score

    while True:
        continue_button = draw_button("Продолжить", 300, 250)
        exit_button = draw_button("Выйти", 650, 250)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.collidepoint(event.pos):
                    return
                elif exit_button.collidepoint(event.pos):
                    if nickname:
                        sql_work.update_player(nickname, score, money, None)
                    restart_game()
                    start_screen()
                    return

        pygame.display.flip()


# Основной игровой цикл
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if nickname != '':
                sql_work.update_player(nickname, score, money, None)
            restart_game()
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            hit_box = pause_icon.get_rect()
            hit_box.x = WIDTH - 80
            hit_box.y = 18
            if hit_box.collidepoint(mouse_pos):
                pause()

        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_s or event.key == pygame.K_DOWN) and not is_down:
                is_down = True
                if not is_jumping:
                    original_y = player_y
                key_press = pygame.K_s if event.key == pygame.K_s else pygame.K_DOWN

            if event.key == pygame.K_p:
                pause()
        elif event.type == pygame.KEYUP:
            if event.key == key_press:
                is_down = False

    keys = pygame.key.get_pressed()

    # Управление
    if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w] or pygame.mouse.get_pressed()[0]:
        if not is_jumping and player_y == original_y:
            is_jumping = True

    # update speed
    if frame_cnt % 1000 == 0:
        diff += 1
        if left_diff >= 150:
            left_diff -= 1
        ground_speed = diff
        bg_speed = diff // 10
    if frame_cnt % 200 == 0:
        coins.append(Coin())

    if step_index >= 27:
        step_index = 0

    if not is_jumping and not is_down:
        step_index += 1
        player = run_imgs[0 if step_index <= 9 else 1 if step_index in range(9, 18) else 2]
    if is_jumping:
        player_y -= jump_vel * 4
        jump_vel -= jv
        if jump_vel < 0:
            player = DJD
        else:
            player = DJU
        if jump_vel < -JUMP_VEL:
            is_jumping = False
            jump_vel = JUMP_VEL
            player = run_imgs[0 if step_index <= 9 else 1 if step_index in range(9, 18) else 2]
    if is_down:
        if is_jumping:
            jump_count -= 0.05
        else:
            player = DOWN
            player_y = original_y + 25
    elif not is_down and not is_jumping:
        player = run_imgs[0 if step_index <= 9 else 1 if step_index in range(9, 18) else 2]
        player_y = original_y

    if obs_frame == 0 or (not obstacles and obs_frame >= 50):
        obstacles.append(Obstacle())
    if k == 0:
        k = random.randint(1, 3)
    if obs_frame == 0:
        k -= 1
        obs_frame = random.randint(50, left_diff)
    obs_frame -= 1

    for coin in coins:
        for obstacle in obstacles:
            if coin.rect.colliderect(obstacle.rect) or (abs(coin.rect.x - obstacle.rect.x) < 40 and not obstacle.buff):
                coins.remove(coin)
                break

    for obstacle in obstacles:
        obstacle.speed = diff
        obstacle.move()
        if obstacle.rect.x < -obstacle.rect.width:
            if obstacle.buff:
                enable_buff = False
            obstacles.remove(obstacle)

    for coin in coins:
        coin.speed = diff
        coin.move()
        if coin.rect.x < -coin.rect.width:
            coins.remove(coin)

    # Проверка на столкновение
    for obstacle in obstacles:
        if player_hitbox.colliderect(obstacle.rect):
            if obstacle.buff:
                if obstacle.buff_type == 'freeze_time':
                    buff_type = 'freeze_time'
                    if slow_time == 0:
                        temp_diff = diff
                        diff = temp_diff // 2 if temp_diff // 2 > 12 else 12
                        ground_speed = diff
                        bg_speed = diff // 10
                        slow_time = 500
                        obstacles.remove(obstacle)
                elif obstacle.buff_type == 'barrier':
                    buff_type = 'barrier'
                    if barrier_time == 0:
                        barrier_time = 500
                        obstacles.remove(obstacle)
                elif obstacle.buff_type == 'bow':
                    buff_type = 'bow'
                    if bow_time == 0:
                        temp_jump_diff = jv
                        jv = 0.55
                        bow_time = 500
                        obstacles.remove(obstacle)
            elif buff_type != 'barrier':
                if nickname != '':
                    sql_work.update_player(nickname, score, money, None)
                running = False
                time.sleep(5)
                restart_game()
                start_screen()
            else:
                create_particles((obstacle.rect.x, obstacle.rect.y), 2, obstacle)
                obstacles.remove(obstacle)
            break

    for coin in coins:
        if player_hitbox.colliderect(coin.rect):
            money += 1
            coins.remove(coin)

    # Отрисовка
    screen.fill((0, 0, 0))
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + bg.get_width(), 0))
    if bg_x <= -bg.get_width():
        screen.blit(bg, (bg_x + bg.get_width(), 0))
    player_rect.y = player_y
    player_hitbox.y = player_y + 25
    screen.blit(fg, (ground_x, 610))
    screen.blit(fg, (ground_x + fg.get_width(), 610))  # Дублирование фона
    if ground_x <= -fg.get_width():
        screen.blit(fg, (ground_x + fg.get_width(), 610))  # Дублирование фона
        ground_x = 0
    ground_x -= ground_speed
    bg_x -= bg_speed
    screen.blit(pause_icon, (WIDTH - 80, 18))
    screen.blit(player, player_rect)
    if eq_skin is not None:
        screen.blit(eq_skin, (player_rect.x, player_rect.y))

    for obstacle in obstacles:
        obstacle.draw(screen)

    for coin in coins:
        coin.draw(screen)

    # Отображение счета
    screen.blit(score_frame, (10, 10))
    score_text = str(score).zfill(5)
    x, y = 178 + 32 - (images['0'].get_width() // 2), 35
    screen.blit(images['0'], (x, y))
    i = 0
    for char in score_text:

        if char in images:
            if char != '0' and char != '1':
                x = 178 + (66 * i) + (64 - images[char].get_width()) // 2
            elif char == '1':
                x = 188 + (66 * i) + (64 - images[char].get_width()) // 4
            else:
                x = 178 + (66 * i) + (64 - images[char].get_width()) // 2
            i += 1
            if i != 1:
                screen.blit(images[char], (x, y))

    text = SMALL_FONT.render(f'Количество монет: {money}', True, WHITE)
    screen.blit(text, (15, 120))

    frame_cnt += 1
    if frame_cnt % 10 == 0:
        score += 1
    if slow_time != 0 and buff_type == 'freeze_time':
        # Уменьшение альфа-канала изображения
        if current_step < fade_out_steps:
            current_alpha = 255 - (alpha_step * current_step)
            buffs[1][0].set_alpha(current_alpha)
            current_step += 1
        buff_rect = buffs[1][0].get_rect()
        screen.blit(buffs[1][0], (530, 30))
        if slow_time - 1 == 0:
            enable_buff = False
            buff_type = None
            buffs[1][0].set_alpha(255)
            # Переменные для затухания
            fade_duration = 8  # время затухания в секундах
            fade_steps = 60  # количество шагов обновления в секунду
            fade_out_steps = fade_duration * fade_steps
            alpha_step = 255 / fade_out_steps
            current_step = 0
            diff = temp_diff
            ground_speed = diff
        slow_time -= 1
    elif barrier_time != 0 and buff_type == 'barrier':
        screen.blit(barrier_texture, player_rect)
        if current_step < fade_out_steps:
            current_alpha = 255 - (alpha_step * current_step)
            buffs[2][0].set_alpha(current_alpha)
            current_step += 1
        buff_rect = buffs[2][0].get_rect()
        screen.blit(buffs[2][0], (540, 30))
        if barrier_time - 1 == 0:
            enable_buff = False
            buff_type = None
            buffs[2][0].set_alpha(255)
            fade_duration = 8
            fade_steps = 60
            fade_out_steps = fade_duration * fade_steps
            alpha_step = 255 / fade_out_steps
            current_step = 0
        barrier_time -= 1
    elif bow_time != 0 and buff_type == 'bow':
        screen.blit(slow_jump_texture, player_rect)
        if current_step < fade_out_steps:
            current_alpha = 255 - (alpha_step * current_step)
            buffs[3][0].set_alpha(current_alpha)
            current_step += 1
        buff_rect = buffs[3][0].get_rect()
        screen.blit(buffs[3][0], (540, 30))
        if bow_time - 1 == 0:
            enable_buff = False
            buff_type = None
            jv = temp_jump_diff
            buffs[3][0].set_alpha(255)
            fade_duration = 8
            fade_steps = 60
            fade_out_steps = fade_duration * fade_steps
            alpha_step = 255 / fade_out_steps
            current_step = 0
        bow_time -= 1

    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.update()
