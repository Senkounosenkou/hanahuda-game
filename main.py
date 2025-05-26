import pygame
from cards import *
import os

pygame.init()

screen_width = 610
screen_height = 410
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("花札")

# 背景読み込み
base_dir = os.path.dirname(__file__)
bg_path = os.path.join(base_dir, "assets", "img", "other", "tatami.png")
background = pygame.image.load(bg_path)
background = pygame.transform.scale(background, (screen_width, screen_height))

# カードの読み込みと初期化（最初の1枚だけ表示）
card = cards[0]
card.position = (50, 50)
card.load_images()

# アニメーション変数
flipping = False
flip_progress = 0
flip_speed = 4
flip_switched = False
flip_card = None

# FPS設定
FPS = 60
clock = pygame.time.Clock()

run = True
while run:
    screen.blit(background, (0, 0))

    # カードの描画
    if not (flipping and flip_card == card):
        card.draw(screen)

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not flipping:
            if card.is_clicked(event.pos):
                flipping = True
                flip_card = card
                flip_progress = 0
                flip_switched = False

    # アニメーション処理
    if flipping and flip_card:
        image = flip_card.get_image()
        w, h = image.get_width(), image.get_height()

        if flip_progress < w // 2:
            current_width = max(1, w - flip_progress * 2)
            scaled = pygame.transform.scale(image, (current_width, h))
            screen.blit(scaled, (flip_card.rect.x + flip_progress, flip_card.rect.y))
            flip_progress += flip_speed
        elif not flip_switched:
            flip_card.is_face_up = not flip_card.is_face_up
            flip_switched = True
            flip_progress += flip_speed
        elif flip_progress < w:
            current_width = max(1, (flip_progress - w // 2) * 2)
            image = flip_card.get_image()
            scaled = pygame.transform.scale(image, (current_width, h))
            x = flip_card.rect.x + w // 2 - current_width // 2
            screen.blit(scaled, (x, flip_card.rect.y))
            flip_progress += flip_speed
        else:
            flipping = False
            flip_progress = 0
            flip_card = None

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
