from tkinter import *
from PIL import Image, ImageTk, ImageOps
import pygame
import random
import time


class SpaceGame:
    def __init__(self):
        self.window = Tk()
        self.window.title("Wormhole Escape")
        self.window.geometry("1200x1000")
        self.center_window(1200, 1000)
        self.window.configure(bg="black")
        self.window.resizable(0, 0)

        # pygame으로 배경음악 설정
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load("space.mp3")
        pygame.mixer.music.play(-1)

        # 메인 메뉴 캔버스
        self.menu_canvas = Canvas(self.window, bg="black", highlightthickness=0)
        self.menu_canvas.pack(fill="both", expand=True)

        self.menu_canvas.create_text(
            600,
            200,
            text="극악의 우주 환경에서 생존 역량 키우기",
            font=("Arial", 48, "bold"),
            fill="white",
        )

        self.buttons = ["게임 시작", "종료"]
        self.current_selection = 0
        self.button_labels = []
        self.render_buttons()

        self.window.bind("<Up>", self.move_selection_up)
        self.window.bind("<Down>", self.move_selection_down)
        self.window.bind("<Return>", self.select_option)

        self.window.mainloop()

    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def render_buttons(self):
        y_position = 400
        for i, label in enumerate(self.buttons):
            arrow = "👉" if i == self.current_selection else "  "
            btn_text = f"{arrow} {label}"
            button = self.menu_canvas.create_text(
                600, y_position, text=btn_text, font=("Arial", 32, "bold"), fill="white"
            )
            self.button_labels.append(button)
            y_position += 100

    def move_selection_up(self, event):
        self.current_selection = (self.current_selection - 1) % len(self.buttons)
        self.update_menu()

    def move_selection_down(self, event):
        self.current_selection = (self.current_selection + 1) % len(self.buttons)
        self.update_menu()

    def update_menu(self):
        for i, button in enumerate(self.button_labels):
            arrow = "👉" if i == self.current_selection else "  "
            text = f"{arrow} {self.buttons[i]}"
            self.menu_canvas.itemconfig(button, text=text)

    def select_option(self, event):
        if self.current_selection == 0:
            self.start_game()
        elif self.current_selection == 1:
            self.window.quit()

    def start_game(self):
        self.window.destroy()  # 메인 윈도우 닫기
        GameScreen()


class GameScreen:
    def __init__(self):
        self.window = Tk()
        self.window.title("Wormhole Escape - Stage 1")
        self.window.geometry("1200x1000")
        self.center_window(1200, 1000)
        self.window.configure(bg="black")
        self.window.resizable(0, 0)

        # 캔버스 설정
        self.canvas = Canvas(self.window, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 배경 이미지
        self.bg_img = Image.open("space5.png").resize((1200, 1000))
        self.bg_photo = ImageTk.PhotoImage(self.bg_img)
        self.bg_img_flipped = ImageOps.flip(self.bg_img)
        self.bg_photo_flipped = ImageTk.PhotoImage(self.bg_img_flipped)

        self.bg1 = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        self.bg2 = self.canvas.create_image(0, -1000, anchor="nw", image=self.bg_photo)

        # 플레이어 설정
        self.player_image = Image.open("rocket5.png").resize((50, 50))
        self.player_photo = ImageTk.PhotoImage(self.player_image)
        self.player = self.canvas.create_image(
            600, 500, image=self.player_photo, anchor="center"
        )  # 초기 위치
        self.player_speed = 15
        self.health = 3
        self.health_text = self.canvas.create_text(
            100, 20, text=f"Health: {self.health}", font=("Arial", 16), fill="white"
        )

        # 운석 설정
        self.meteor_image = Image.open("meteor2.png").resize((10, 10))
        self.meteor_photo = ImageTk.PhotoImage(self.meteor_image)
        self.meteors = []
        self.meteor_speed = 5
        self.meteor_size = 10  # 운석 크기 줄임
        self.target_meteor_count = 40  # 화면에 유지할 운석 개수 잠시 1

        # 생존 시간 및 운석 개수
        self.start_time = time.time()
        self.timer_text = self.canvas.create_text(
            600, 20, text="Time: 0s", font=("Arial", 16), fill="white"
        )
        self.meteor_count_text = self.canvas.create_text(
            1100,
            20,
            text=f"Meteors: {len(self.meteors)}",
            font=("Arial", 16),
            fill="white",
        )

        # 키 입력 설정
        self.keys_pressed = set()  # 현재 눌려 있는 키 저장
        self.window.bind("<KeyPress>", self.key_press)
        self.window.bind("<KeyRelease>", self.key_release)

        self.increase_meteor_count()

        # 게임 루프 시작
        self.game_loop()
        self.window.mainloop()

    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def move_background(self):
        # 배경 위아래로 이동
        self.canvas.move(self.bg1, 0, 7)
        self.canvas.move(self.bg2, 0, 7)

        # 배경이 화면 아래로 완전히 내려갔을 경우 초기화
        if self.canvas.coords(self.bg1)[1] >= 1000:
            self.flip_background(1)
            self.canvas.moveto(self.bg1, 0, -1000)
        if self.canvas.coords(self.bg2)[1] >= 1000:
            self.flip_background(2)
            self.canvas.moveto(self.bg2, 0, -1000)

    def flip_background(self, bg_number):
        """지정된 배경(bg1 또는 bg2)을 위아래로 반전"""
        if bg_number == 1:
            # bg1을 반전된 이미지로 교체
            current_image = self.canvas.itemcget(self.bg1, "image")
            new_image = (
                self.bg_photo_flipped
                if current_image == str(self.bg_photo)
                else self.bg_photo
            )
            self.canvas.itemconfig(self.bg1, image=new_image)
        elif bg_number == 2:
            # bg2를 반전된 이미지로 교체
            current_image = self.canvas.itemcget(self.bg2, "image")
            new_image = (
                self.bg_photo_flipped
                if current_image == str(self.bg_photo)
                else self.bg_photo
            )
            self.canvas.itemconfig(self.bg2, image=new_image)

    def key_press(self, event):
        self.keys_pressed.add(event.keysym)

    def key_release(self, event):
        self.keys_pressed.discard(event.keysym)

    def move_player(self):
        player_size = 25  # 플레이어 이미지 반경 (이미지 크기의 절반)
        # 위쪽 이동
        if (
            "Up" in self.keys_pressed
            and self.canvas.coords(self.player)[1] - player_size > 0
        ):
            self.canvas.move(self.player, 0, -self.player_speed)

        # 아래쪽 이동
        if (
            "Down" in self.keys_pressed
            and self.canvas.coords(self.player)[1] + player_size < 1000
        ):
            self.canvas.move(self.player, 0, self.player_speed)

        # 왼쪽 이동
        if (
            "Left" in self.keys_pressed
            and self.canvas.coords(self.player)[0] - player_size > 0
        ):
            self.canvas.move(self.player, -self.player_speed, 0)

        # 오른쪽 이동
        if (
            "Right" in self.keys_pressed
            and self.canvas.coords(self.player)[0] + player_size < 1200
        ):
            self.canvas.move(self.player, self.player_speed, 0)

    def spawn_meteor(self):
        spawn_side = random.choice(["top", "left", "right", "bottom"])
        target_x, target_y = None, None

        if spawn_side == "top":
            x = random.randint(0, 1200 - self.meteor_size)
            meteor = self.canvas.create_image(
                x, 0, image=self.meteor_photo, anchor="center"
            )
            target_x = random.randint(0, 1200)
            target_y = 1000

        elif spawn_side == "left":
            y = random.randint(0, 1000 - self.meteor_size)
            meteor = self.canvas.create_image(
                0, y, image=self.meteor_photo, anchor="center"
            )
            target_x = 1200
            target_y = random.randint(0, 1000)

        elif spawn_side == "right":
            y = random.randint(0, 1000 - self.meteor_size)
            meteor = self.canvas.create_image(
                1200, y, image=self.meteor_photo, anchor="center"
            )
            target_x = 0
            target_y = random.randint(0, 1000)

        else:  # bottom
            x = random.randint(0, 1200 - self.meteor_size)
            meteor = self.canvas.create_image(
                x, 1000, image=self.meteor_photo, anchor="center"
            )
            target_x = random.randint(0, 1200)
            target_y = 0

        self.meteors.append({"id": meteor, "target_x": target_x, "target_y": target_y})
        print(
            f"Spawned meteor at ({spawn_side}): {self.canvas.coords(meteor)}, target=({target_x}, {target_y})"
        )

    def ensure_meteor_count(self):
        print(f"Before spawning, meteors: {len(self.meteors)}")  # 디버깅 로그
        while len(self.meteors) < self.target_meteor_count:
            self.spawn_meteor()
        print(f"After spawning, meteors: {len(self.meteors)}")  # 디버깅 로그
        self.canvas.itemconfig(
            self.meteor_count_text, text=f"Meteors: {len(self.meteors)}"
        )

    def increase_meteor_count(self):
        self.target_meteor_count += 1  # 운석 개수 증가
        self.window.after(1000, self.increase_meteor_count)  # 5초마다 호출

    def move_meteors(self):
        print("무브 운석")
        for meteor in self.meteors[:]:
            coords = self.canvas.coords(meteor["id"])
            # 좌표가 비어 있거나 유효하지 않은 경우 건너뛰기 (추가 디버깅 로그 포함)
            if not coords or len(coords) < 2:
                print(f"Invalid coordinates for meteor {meteor}: {coords}")
                continue  # 삭제하지 않고 건너뜁니다.
            dx = meteor["target_x"] - coords[0]
            dy = meteor["target_y"] - coords[1]
            distance = max((dx**2 + dy**2) ** 0.5, 1)  # Avoid division by zero
            move_x = (dx / distance) * self.meteor_speed
            move_y = (dy / distance) * self.meteor_speed
            self.canvas.move(meteor["id"], move_x, move_y)

            # 디버깅: 운석 이동 로그
            print(
                f"Meteor at {coords} moving to ({meteor['target_x']}, {meteor['target_y']})"
            )

            # 운석이 목적지에 도달하면 삭제
            if (
                abs(coords[0] - meteor["target_x"]) < 5
                and abs(coords[1] - meteor["target_y"]) < 5
            ):
                print("목적지에 도달")
                self.canvas.delete(meteor["id"])
                self.meteors.remove(meteor)
                continue
            if not coords or len(coords) < 2:
                print(f"Meteor {meteor} has invalid coordinates: {coords}. Removing.")
                self.canvas.delete(meteor["id"])
                self.meteors.remove(meteor)
                continue

            # 플레이어와 충돌 감지
            if self.check_collision(meteor):
                self.health -= 1
                self.canvas.itemconfig(self.health_text, text=f"Health: {self.health}")
                self.canvas.delete(meteor["id"])
                self.meteors.remove(meteor)
                if self.health <= 0:
                    self.end_game()

    # def check_collision(self, meteor):
    #     player_coords = self.canvas.coords(self.player)
    #     meteor_coords = self.canvas.coords(meteor["id"])
    #     if not player_coords or not meteor_coords:  # 좌표가 비어 있으면 False 반환
    #         return False

    #     return (
    #         player_coords[2] > meteor_coords[0]
    #         and player_coords[0] < meteor_coords[2]
    #         and player_coords[3] > meteor_coords[1]
    #         and player_coords[1] < meteor_coords[3]
    #     )
    def check_collision(self, meteor):
        player_coords = self.canvas.coords(self.player)  # 플레이어 중심 좌표
        meteor_coords = self.canvas.coords(meteor["id"])  # 운석 중심 좌표
        player_size = 25  # 플레이어 이미지 반경
        meteor_size = 5  # 운석 이미지 반경

        if not player_coords or not meteor_coords:
            return False

        # 거리 기반 충돌 계산
        distance = (
            (player_coords[0] - meteor_coords[0]) ** 2
            + (player_coords[1] - meteor_coords[1]) ** 2
        ) ** 0.5
        return distance < (player_size + meteor_size)

    def update_timer(self):
        elapsed_time = int(time.time() - self.start_time)
        self.canvas.itemconfig(self.timer_text, text=f"Time: {elapsed_time}s")

    def game_loop(self):
        self.move_background()
        self.move_player()  # 키보드 입력에 따라 플레이어 이동
        self.update_timer()  # 타이머 업데이트
        self.move_meteors()  # 운석 이동
        self.ensure_meteor_count()  # 운석 개수 유지
        self.window.after(16, self.game_loop)

    def end_game(self):
        self.canvas.create_text(
            600,
            500,
            text="Game Over!",
            font=("Arial", 48, "bold"),
            fill="red",
        )
        self.window.after(3000, self.window.destroy)


if __name__ == "__main__":
    SpaceGame()
