import pygame
import os
import sys

class Cards:
    def __init__(self, position, month, type, name, front_image_path, back_image_path, is_face_up):
        self.position = position
        self.month = month
        self.type = type
        self.name = name
        self.front_image_path = front_image_path
        self.back_image_path = back_image_path
        self.is_face_up = is_face_up
        self.front_image = None
        self.back_image = None

        
        self.flipping = False
        self.flip_progress = 0
        self.flip_switched = False

        
        self.x = 0
        self.y = 0

    def load_images(self):
        # pyinstaller対応: 実行ファイルか開発環境かを判定
        if getattr(sys, 'frozen', False):
            # pyinstallerで作成された実行ファイルの場合
            base_dir = sys._MEIPASS
        else:
            # 開発環境（.pyファイル実行）の場合
            base_dir = os.path.dirname(__file__)
            
        front_path = os.path.join(base_dir, self.front_image_path)
        back_path = os.path.join(base_dir, self.back_image_path)
        self.front_image = pygame.image.load(front_path).convert_alpha()
        self.back_image = pygame.image.load(back_path).convert_alpha()

        card_width = self.front_image.get_width()
        card_height = self.front_image.get_height()
    
    # カードサイズを小さく調整
        new_width = 60
        new_height = 80
    
        self.front_image = pygame.transform.scale(self.front_image, (new_width, new_height))
        self.back_image = pygame.transform.scale(self.back_image, (new_width, new_height))


    def get_image(self):
        return self.front_image if self.is_face_up else self.back_image
    
    def start_flip(self):
        if not self.flipping:
            self.flipping = True
            self.flip_progress = 0
            self.flip_switched = False
    
    def update_and_draw(self, screen):
        if self.flipping:
            self.flip_progress += 0.1
            if self.flip_progress > 0.5 and not self.flip_switched:
                self.is_face_up = not self.is_face_up
                self.flip_switched = True

            if self.flip_progress >= 1.0:
                self.flipping = False
                self.flip_progress = 0

        current_image = self.get_image()
        if current_image:
            if self.flipping:
                scale_x = abs(1 - 2 * self.flip_progress)
                scaled_image = pygame.transform.scale(current_image,
                    (int(current_image.get_width() * scale_x), int(current_image.get_height())))
                screen.blit(scaled_image, (self.x, self.y))
            else:
                # アニメーション中でない場合は通常描画
                screen.blit(current_image, (self.x, self.y))
        else:
            print(f"Error: Image not loaded for {self.name} at {self.position}")
    

cards = [
    Cards((0,0), 1, "bright", "pine_crane", "assets/img/cards/1_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "red_ribbon", "pine_tan", "assets/img/cards/1_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "plain", "pine_1", "assets/img/cards/1_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "plain", "pine_2", "assets/img/cards/1_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 2, "tane", "plum_bird", "assets/img/cards/2_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "red_ribbon", "plum_tan", "assets/img/cards/2_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "plain", "plum_1", "assets/img/cards/2_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "plain", "plum_2", "assets/img/cards/2_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 3, "bright", "cherry_curtain", "assets/img/cards/3_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "red_ribbon", "cherry_tan", "assets/img/cards/3_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "plain", "cherry_1", "assets/img/cards/3_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "plain", "cherry_2", "assets/img/cards/3_4.png", "assets/img/cards/0_0.png", False),
                            #セキレイと藤
    Cards((0,0), 4, "tane", "wagtail", "assets/img/cards/4_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "red_ribbon", "wisteria_tan", "assets/img/cards/4_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "plain", "wisteria_1", "assets/img/cards/4_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "plain", "wisteria_2", "assets/img/cards/4_4.png", "assets/img/cards/0_0.png", False),
                    #あやめ
    Cards((0,0), 5, "tane", "iris_bridge", "assets/img/cards/5_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "red_ribbon", "iris_tan", "assets/img/cards/5_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "plain", "iris_1", "assets/img/cards/5_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "plain", "iris_2", "assets/img/cards/5_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 6, "tane", "peony_butterfly", "assets/img/cards/6_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "blue_ribbon", "peony_tan", "assets/img/cards/6_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "plain", "peony_1", "assets/img/cards/6_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "plain", "peony_2", "assets/img/cards/6_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 7, "tane", "boar", "assets/img/cards/7_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "red_ribbon", "bush_clover_tan", "assets/img/cards/7_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "plain", "bush_clover_1", "assets/img/cards/7_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "plain", "bush_clover_2", "assets/img/cards/7_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 8, "bright", "full_moon_pampas", "assets/img/cards/8_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "tane", "pampas_geese", "assets/img/cards/8_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "plain", "pampas_1", "assets/img/cards/8_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "plain", "pampas_2", "assets/img/cards/8_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 9, "tane", "chrysanthemum_sake_cup", "assets/img/cards/9_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "blue_ribbon", "chrysanthemum_tan", "assets/img/cards/9_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "plain", "chrysanthemum_1", "assets/img/cards/9_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "plain", "chrysanthemum_2", "assets/img/cards/9_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 10, "tane", "maple_deer", "assets/img/cards/10_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "blue_ribbon", "maple_tan", "assets/img/cards/10_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "plain", "maple_1", "assets/img/cards/10_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "plain", "maple_2", "assets/img/cards/10_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 11, "bright", "michikaze_willows", "assets/img/cards/11_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "tane", "willows_swallow", "assets/img/cards/11_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "tan", "willows_tan", "assets/img/cards/11_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "plain", "willows_1", "assets/img/cards/11_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 12, "bright", "paulownia_phoenix", "assets/img/cards/12_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_1", "assets/img/cards/12_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_2", "assets/img/cards/12_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_3", "assets/img/cards/12_4.png", "assets/img/cards/0_0.png", False),
]