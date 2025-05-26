import pygame
from cards import *
import os

pygame.init()

screen_width=610
screen_hight=410
screen=pygame.display.set_mode((screen_width,screen_hight))
pygame.display.set_caption("花札")


# ここで画像をロード
for card in cards:
    card.load_images()


#FPSの設定
FPS=60
clock=pygame.time.Clock()

#色の設定
GREEN =(0,255,0)


#背景画像の読み込み
base_dir = os.path.dirname(__file__)
bg_path = os.path.join(base_dir, "assets", "img", "other", "tatami.png")
background = pygame.image.load(bg_path)
background = pygame.transform.scale(background, (screen_width, screen_hight))  # 画面サイズにリサイズ



#メインループ================================================


card_x, card_y = 50, 50  # カードの表示位置
card=cards[0]
card_width, card_height = card.get_image().get_width(), card.get_image().get_height()

#アニメーション用変数
flipping = False  # カードがめくられているかどうか
flip_progress = 0  # めくりの進行度（0から1の範囲）
flip_speed = 2  # 1フレームあたりのめくり速度


run = True
while run:

    # screen.fill(background)
    screen.blit(background, (0, 0))  # 画像を左上に描画
     # 例: 1枚目のカードを表示
    screen.blit(cards[0].get_image(), (50, 50))

    #イベントの取得
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run = False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                run = False

        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:  # マウスボタンが押されたとき
            if event.button == 1:  # 左クリック
                mx, my = event.pos
                # カードの範囲内か判定
                if (card_x <= mx <= card_x + card_width and
                    card_y <= my <= card_y + card_height and not flipping):
                    flipping = True
                    flip_progress = 0

    # アニメーション処理
    if flipping:
        # 幅を縮める
        if flip_progress < card_width // 2:
            current_width = card_width - flip_progress * 2
            if current_width < 1:
                current_width = 1
            image = card.get_image()
            scaled = pygame.transform.scale(image, (current_width, card_height))
            screen.blit(scaled, (card_x + flip_progress, card_y))
            flip_progress += flip_speed
        # 画像を切り替えて幅を戻す
        elif flip_progress < card_width:
            if not card.is_face_up:
                card.is_face_up = True
            else:
                card.is_face_up = False
            current_width = (flip_progress - card_width // 2) * 2
            if current_width > card_width:
                current_width = card_width
            image = card.get_image()
            scaled = pygame.transform.scale(image, (current_width, card_height))
            screen.blit(scaled, (card_x + card_width // 2 - current_width // 2, card_y))
            flip_progress += flip_speed
        else:
            flipping = False
            flip_progress = 0
            screen.blit(card.get_image(), (card_x, card_y))
    else:
        screen.blit(card.get_image(), (card_x, card_y))
 



    
    pygame.display.update()
    clock.tick(FPS)



#===========================================================
pygame.quit()