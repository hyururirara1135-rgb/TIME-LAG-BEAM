import pyxel
import random

# =====================
# 定数
# =====================
WIDTH = 160
HEIGHT = 120
FPS = 30

PLAYER_FOOT_Y = 92
PLAYER_SPEED = 2

INITIAL_LIGHTNING = 10
INCREASE_EVERY = FPS * 10
INCREASE_AMOUNT = 5

WARNING_TIME_BASE = 30
WARNING_TIME_MIN = 10

LIGHTNING_SPEED = 14
SPAWN_INTERVAL = 10
FAKE_RATE = 0.25

FLOOR_Y = PLAYER_FOOT_Y + 1

# =====================
# 稲妻
# =====================
class Lightning:
    def __init__(self, x, fake, warning_time):
        self.x = x
        self.fake = fake
        self.warning_time = warning_time
        self.state = "warning"
        self.timer = 0
        self.y = 0

    def update(self):
        self.timer += 1

        if self.state == "warning" and self.timer > self.warning_time:
            if self.fake:
                self.state = "end"
            else:
                self.state = "fall"
                self.y = 0

        elif self.state == "fall":
            self.y += LIGHTNING_SPEED
            if self.y > HEIGHT:
                self.state = "end"

    def is_danger(self):
        return self.state == "fall"

    def draw(self):
        if self.state == "warning":
            blink_interval = max(2, self.warning_time // 6)
            if (self.timer // blink_interval) % 2 == 0:
                pyxel.line(self.x, 0, self.x, HEIGHT, 7)

        elif self.state == "fall":
            for i in range(6):
                dx = random.choice([-2, -1, 0, 1, 2])
                pyxel.line(
                    self.x + dx,
                    self.y - i * 6,
                    self.x - dx,
                    self.y - i * 6 + 6,
                    10
                )

# =====================
# メインアプリ
# =====================
class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, fps=FPS, title="TIME LAG GAME")
        self.best_time = 0
        self.state = "title"
        pyxel.run(self.update, self.draw)

    def start_game(self):
        self.player_x = WIDTH // 2
        self.lightnings = []
        self.spawn_timer = 0
        self.frame = 0
        self.max_lightning = INITIAL_LIGHTNING
        self.warning_time = WARNING_TIME_BASE
        self.state = "game"

    # -----------------
    def update(self):
        if self.state == "title":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.start_game()

        elif self.state == "game":
            self.update_game()

        elif self.state == "gameover":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.state = "title"

    def update_game(self):
        self.frame += 1

        # プレイヤー移動
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x += PLAYER_SPEED
        self.player_x = max(8, min(WIDTH - 8, self.player_x))

        # 難易度上昇
        if self.frame % INCREASE_EVERY == 0:
            self.max_lightning += INCREASE_AMOUNT
            self.warning_time = max(
                WARNING_TIME_MIN,
                self.warning_time - 2
            )

        # 稲妻生成
        self.spawn_timer += 1
        if self.spawn_timer > SPAWN_INTERVAL:
            self.spawn_timer = 0
            if len(self.lightnings) < self.max_lightning:
                x = random.randint(10, WIDTH - 10)
                fake = random.random() < FAKE_RATE
                self.lightnings.append(
                    Lightning(x, fake, self.warning_time)
                )

        # 更新 & 判定
        for l in self.lightnings:
            l.update()
            if l.is_danger():
                if abs(l.x - self.player_x) < 6 and abs(l.y - PLAYER_FOOT_Y) < 14:
                    self.state = "gameover"

        self.lightnings = [l for l in self.lightnings if l.state != "end"]

    # -----------------
    def draw(self):
        pyxel.cls(0)

        if self.state == "title":
            self.draw_title()
        else:
            self.draw_game()

        if self.state == "gameover":
            pyxel.text(52, 50, "GAME OVER", 8)
            pyxel.text(28, 65, "CLICK TO TITLE", 7)

    def draw_title(self):
        pyxel.text(38, 30, "TIME LAG GAME", 11)
        pyxel.text(40, 48, f"BEST {self.best_time:.1f}s", 10)
        pyxel.rect(55, 70, 50, 14, 5)
        pyxel.text(70, 74, "START", 7)

    def draw_game(self):
        time_sec = self.frame / FPS
        pyxel.text(5, 5, f"{time_sec:.1f}s", 7)

        # 床
        pyxel.rect(0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y, 5)

        # プレイヤー
        self.draw_player(self.player_x, PLAYER_FOOT_Y)

        # 稲妻
        for l in self.lightnings:
            l.draw()

        # 感電演出（勇者周辺）
        if self.state == "gameover":
            self.best_time = max(self.best_time, time_sec)
            if pyxel.frame_count % 6 < 3:
                pyxel.rect(
                    self.player_x - 10,
                    PLAYER_FOOT_Y - 22,
                    20,
                    24,
                    7
                )

    def draw_player(self, x, foot_y):
        # 足
        pyxel.rect(x - 3, foot_y - 4, 2, 4, 6)
        pyxel.rect(x + 1, foot_y - 4, 2, 4, 6)
        # 体
        pyxel.rect(x - 3, foot_y - 10, 6, 6, 3)
        # 頭
        pyxel.rect(x - 2, foot_y - 14, 4, 3, 11)
        pyxel.rect(x - 3, foot_y - 15, 6, 2, 0)
        # 剣
        pyxel.line(x + 4, foot_y - 10, x + 4, foot_y - 2, 7)
        # 盾
        pyxel.rect(x - 7, foot_y - 9, 3, 6, 12)

# =====================
App()
