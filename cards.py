import pygame
import os

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

    def load_images(self):
        import pygame
        base_dir = os.path.dirname(__file__)
        front_path = os.path.join(base_dir, self.front_image_path)
        back_path = os.path.join(base_dir, self.back_image_path)
        self.front_image = pygame.image.load(front_path).convert_alpha()
        self.back_image = pygame.image.load(back_path).convert_alpha()

    def get_image(self):
        return self.front_image if self.is_face_up else self.back_image

cards = [
    Cards((0,0), 1, "bright", "crane", "assets/img/cards/1_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "poetry_ribbon", "pine_tan", "assets/img/cards/1_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "plain", "pine_1", "assets/img/cards/1_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 1, "plain", "pine_2", "assets/img/cards/1_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 2, "bright", "plum_bird", "assets/img/cards/2_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "poetry_ribbon", "plum_tan", "assets/img/cards/2_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "plain", "plum_1", "assets/img/cards/2_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 2, "plain", "plum_2", "assets/img/cards/2_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 3, "bright", "cherry_curtain", "assets/img/cards/3_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "poetry_ribbon", "cherry_tan", "assets/img/cards/3_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "plain", "cherry_1", "assets/img/cards/3_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 3, "plain", "cherry_2", "assets/img/cards/3_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 4, "animal", "wagtail", "assets/img/cards/4_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "red_ribbon", "wisteria_tan", "assets/img/cards/4_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "plain", "wisteria_1", "assets/img/cards/4_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 4, "plain", "wisteria_2", "assets/img/cards/4_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 5, "animal", "bridge", "assets/img/cards/5_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "red_ribbon", "iris_tan", "assets/img/cards/5_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "plain", "iris_1", "assets/img/cards/5_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 5, "plain", "iris_2", "assets/img/cards/5_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 6, "animal", "butterfly", "assets/img/cards/6_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "blue_ribbon", "peony_tan", "assets/img/cards/6_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "plain", "peony_1", "assets/img/cards/6_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 6, "plain", "peony_2", "assets/img/cards/6_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 7, "animal", "boar", "assets/img/cards/7_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "blue_ribbon", "bush_clover_tan", "assets/img/cards/7_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "plain", "bush_clover_1", "assets/img/cards/7_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 7, "plain", "bush_clover_2", "assets/img/cards/7_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 8, "animal", "geese", "assets/img/cards/8_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "blue_ribbon", "pampas_tan", "assets/img/cards/8_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "plain", "pampas_1", "assets/img/cards/8_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 8, "plain", "pampas_2", "assets/img/cards/8_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 9, "animal", "sake_cup", "assets/img/cards/9_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "red_ribbon", "chrysanthemum_tan", "assets/img/cards/9_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "plain", "chrysanthemum_1", "assets/img/cards/9_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 9, "plain", "chrysanthemum_2", "assets/img/cards/9_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 10, "animal", "deer", "assets/img/cards/10_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "blue_ribbon", "maple_tan", "assets/img/cards/10_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "plain", "maple_1", "assets/img/cards/10_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 10, "plain", "maple_2", "assets/img/cards/10_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 11, "animal", "swallow", "assets/img/cards/11_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "red_ribbon", "paulownia_tan", "assets/img/cards/11_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "plain", "paulownia_1", "assets/img/cards/11_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 11, "plain", "paulownia_2", "assets/img/cards/11_4.png", "assets/img/cards/0_0.png", False),

    Cards((0,0), 12, "bright", "phoenix", "assets/img/cards/12_1.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_3", "assets/img/cards/12_2.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_4", "assets/img/cards/12_3.png", "assets/img/cards/0_0.png", False),
    Cards((0,0), 12, "plain", "paulownia_5", "assets/img/cards/12_4.png", "assets/img/cards/0_0.png", False),
]