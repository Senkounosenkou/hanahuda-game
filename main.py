import pygame
from cards import *
import os

pygame.init()

screen_width = 610
screen_hight = 410
screen = pygame.display.set_mode((screen_width, screen_hight))
pygame.display.set_caption("花札")

# 画像をロード
for card in cards:
    card.load_images()

# FPSの設定
FPS = 60
clock = pygame.time.Clock()

# 背景画像の読み込み
base_dir = os.path.dirname(__file__)
bg_path = os.path.join(base_dir, "assets", "img", "other", "tatami.png")
background = pygame.image.load(bg_path)
background = pygame.transform.scale(background, (screen_width, screen_hight))

# カード情報
card_x, card_y = 50, 50
card = cards[0]
card_width, card_height = card.get_image().get_width(), card.get_image().get_height()

# アニメーション用変数
flipping = False
flip_progress = 0
flip_speed = 4  # めくりの速さ（数値を上げると速くなる）
flip_switched = False  # 裏表を切り替えたかどうか

run = True
while run:
    screen.blit(background, (0, 0))  # 背景描画

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:    #左クリック
            # マウスの位置を取得 mx = event.pos[0] my = event.pos[1]と同じ
            mx, my = event.pos   
            #カードの位置からカードの幅までの範囲かどうかをチェック                                           
            if (card_x <= mx <= card_x + card_width and 
            #カードの位置からカードの高さまでの範囲かどうかをチェック    
                card_y <= my <= card_y + card_height and not flipping):
                flipping = True
                flip_progress = 0
                flip_switched = False

    # カードのアニメーション処理
    if flipping:
        if flip_progress < card_width // 2:
            # カードを縮小中
            current_width = max(1, card_width - flip_progress * 2)
            image = card.get_image()
            scaled = pygame.transform.scale(image, (current_width, card_height))
            screen.blit(scaled, (card_x + flip_progress, card_y))
            flip_progress += flip_speed
        elif not flip_switched:
            # 裏表を切り替える（1回だけ）
            card.is_face_up = not card.is_face_up
            flip_switched = True
            flip_progress += flip_speed
        elif flip_progress < card_width:
            # カードを拡大中
            current_width = max(1, (flip_progress - card_width // 2) * 2)
            image = card.get_image()
            scaled = pygame.transform.scale(image, (current_width, card_height))
            screen.blit(scaled, (card_x + card_width // 2 - current_width // 2, card_y))
            flip_progress += flip_speed
        else:
            # アニメーション完了
            flipping = False
            flip_progress = 0
            screen.blit(card.get_image(), (card_x, card_y))
    else:
        # 通常表示
        screen.blit(card.get_image(), (card_x, card_y))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
