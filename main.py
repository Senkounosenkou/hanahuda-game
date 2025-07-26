import pygame  # Pygameライブラリをインポート
from cards import cards  # カードデータをインポート
import os  # OSモジュールをインポート（ファイルパス操作用）
import sys  # コマンドライン引数処理用
import random  # ランダム処理用
from deck import Deck  # デッキクラスをインポート
from logic import (  # ロジックモジュールから各関数をインポート
    draw_sorted_captured_cards,  # 取り札描画関数
    capture_cards_with_animation,  # アニメーション付きカード取得関数
    capture_multiple_cards_with_animation,  # 複数カード取得関数（新規追加）
    draw_from_yama_deck,  # 山札からカードを引く関数
    update_field_positions,  # 場札位置更新関数
    update_animations,  # アニメーション更新関数
    is_animations_active,  # アニメーション実行中チェック関数
    draw_overlays,  # 重ね合わせ表示描画関数
    draw_yama_highlights,  # 山札強調表示描画関数
    process_cutin_queue,  # カットインキュー処理関数
    draw_captured_highlights,  # 新規追加: 取り札ハイライト描画関数
    draw_merge_animations,  # 新規追加: 重なり合いアニメーション描画関数
    draw_normal_animations,  # 新規追加: 通常のアニメーション描画関数
    draw_cutin_animations,  # 新規追加: カットインアニメーション描画関数
    calculate_score,  # 新規追加: 役計算関数
    active_yama_highlights,  # アクティブな山札強調表示リスト
    active_merge_animations,  # 新規追加: アクティブな重なり合いアニメーションリスト
    active_animations  # 新規追加: アクティブな通常のアニメーションリスト
)

pygame.init()  # Pygameを初期化

def get_japanese_font(size=36):
    font_path = [
        "C:/Windows/Fonts/msgothic.ttc",  # MSゴシックフォントのパス
        "C:/Windows/Fonts/meiryo.ttc",  # メイリオフォントのパス
        "C:/windows/Fonts/msmincho.ttc",  # MS明朝フォントのパス
        "C:/windows/Fonts/yugothic.ttc"  # Yu Gothicフォントのパス
    ]

    for path in font_path:
        if os.path.exists(path):
            return pygame.font.Font(path, size)

    # すべてのフォントが見つからない場合はデフォルトフォントを返す
    return pygame.font.Font(None, size)

def get_card_type_by_name(card_name):
    """カード名からカードタイプを判定"""
    bright_cards = ['pine_crane', 'cherry_curtain', 'full_moon_pampas', 'michikaze_willows', 'paulownia_phoenix']
    animal_cards = ['plum_bird', 'wagtail', 'iris_bridge', 'peony_butterfly', 'boar', 'pampas_geese', 'chrysanthemum_sake_cup', 'maple_deer', 'willows_swallow']
    ribbon_cards = ['pine_tan', 'plum_tan', 'cherry_tan', 'wisteria_tan', 'iris_tan', 'peony_tan', 'bush_clover_tan', 'chrysanthemum_tan', 'maple_tan', 'willows_tan']
    
    if card_name in bright_cards:
        return 'bright'
    elif card_name in animal_cards:
        return 'animal'
    elif card_name in ribbon_cards:
        return 'ribbon'
    else:
        return 'plain'

def choose_best_cpu_card(cpu_hand, cpu_captured, field_cards):
    """CPUが最適なカードを選択する関数"""
    
    def get_card_priority(card):
        """カードの優先度を計算（高い値ほど優先）"""
        priority = 0
        
        # 1. 場札とマッチするカードを最優先
        matching_field_cards = [fc for fc in field_cards if fc.month == card.month]
        if matching_field_cards:
            priority += 1000  # 非常に高い優先度
            
            # マッチするカードの価値も考慮
            for field_card in matching_field_cards:
                card_type = get_card_type_by_name(field_card.name)
                if card_type == 'bright':
                    priority += 500  # 光札は高価値
                elif card_type == 'animal':
                    priority += 200  # 種札は中価値
                elif card_type == 'ribbon':
                    priority += 100  # 短冊は低価値
                else:
                    priority += 50   # カス札は最低価値
        
        # 2. 現在の取り札で役が成立しそうなカードを優先
        # 花見酒・月見酒の判定
        if card.name == 'cherry_curtain':  # 桜の幕
            # 菊の杯があるかチェック
            has_sake_cup = any(c.name == 'chrysanthemum_sake_cup' for c in cpu_captured)
            if has_sake_cup:
                priority += 800  # 花見酒完成
        elif card.name == 'chrysanthemum_sake_cup':  # 菊の杯
            # 桜の幕または満月があるかチェック
            has_cherry = any(c.name == 'cherry_curtain' for c in cpu_captured)
            has_moon = any(c.name == 'full_moon_pampas' for c in cpu_captured)
            if has_cherry or has_moon:
                priority += 800  # 花見酒または月見酒完成
        elif card.name == 'full_moon_pampas':  # 満月
            # 菊の杯があるかチェック
            has_sake_cup = any(c.name == 'chrysanthemum_sake_cup' for c in cpu_captured)
            if has_sake_cup:
                priority += 800  # 月見酒完成
        
        # 3. 光札は常に高優先度
        card_type = get_card_type_by_name(card.name)
        if card_type == 'bright':
            priority += 300
        
        # 4. 猪鹿蝶の判定
        if card.name in ['boar', 'maple_deer', 'peony_butterfly']:
            # 他の猪鹿蝶カードがあるかチェック
            ino_shika_cho = ['boar', 'maple_deer', 'peony_butterfly']
            existing_count = sum(1 for c in cpu_captured if c.name in ino_shika_cho)
            if existing_count >= 1:
                priority += 400  # 猪鹿蝶に近づく
        
        return priority
    
    # 全てのカードの優先度を計算
    card_priorities = [(card, get_card_priority(card)) for card in cpu_hand]
    
    # 優先度順にソート（降順）
    card_priorities.sort(key=lambda x: x[1], reverse=True)
    
    # デバッグ情報を出力
    print("🤖 CPU カード選択分析:")
    for card, priority in card_priorities:
        matching = [fc.name for fc in field_cards if fc.month == card.month]
        match_info = f" -> {matching}" if matching else " (マッチなし)"
        print(f"  {card.name}: 優先度{priority}{match_info}")
    
    # 最高優先度のカードを選択
    best_card = card_priorities[0][0]
    print(f"🎯 CPU選択: {best_card.name} (優先度: {card_priorities[0][1]})")
    
    return best_card

def draw_koikoi_choice_screen(screen, game_state, japanese_font, small_font):
    """こいこい選択画面を描画する関数"""
    # 半透明の背景オーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 選択画面の背景
    choice_width = 600
    choice_height = 400
    choice_x = (SCREEN_WIDTH - choice_width) // 2
    choice_y = (SCREEN_HEIGHT - choice_height) // 2
    
    pygame.draw.rect(screen, (50, 50, 100), (choice_x, choice_y, choice_width, choice_height))
    pygame.draw.rect(screen, (255, 255, 255), (choice_x, choice_y, choice_width, choice_height), 3)
    
    # 役成立の表示
    title_text = japanese_font.render("役が成立しました！", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, choice_y + 50))
    screen.blit(title_text, title_rect)
    
    # 現在の得点と役を表示
    score_text = small_font.render(f"得点: {game_state['current_round_score']}文", True, (255, 255, 0))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, choice_y + 100))
    screen.blit(score_text, score_rect)
    
    # 成立した役を表示
    y_offset = 140
    for i, yaku in enumerate(game_state['current_yakus']):
        if i >= 3:  # 最大3つまで表示
            break
        yaku_text = small_font.render(f"• {yaku}", True, (200, 255, 200))
        yaku_rect = yaku_text.get_rect(center=(SCREEN_WIDTH//2, choice_y + y_offset + i * 30))
        screen.blit(yaku_text, yaku_rect)
    
    # 選択肢のボタン
    button_width = 200
    button_height = 60
    agari_x = SCREEN_WIDTH//2 - button_width - 20
    koikoi_x = SCREEN_WIDTH//2 + 20
    button_y = choice_y + choice_height - 120
    
    # 上がりボタン
    pygame.draw.rect(screen, (100, 200, 100), (agari_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (agari_x, button_y, button_width, button_height), 2)
    agari_text = japanese_font.render("上がり", True, (255, 255, 255))
    agari_rect = agari_text.get_rect(center=(agari_x + button_width//2, button_y + button_height//2))
    screen.blit(agari_text, agari_rect)
    
    # こいこいボタン
    pygame.draw.rect(screen, (200, 100, 100), (koikoi_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (koikoi_x, button_y, button_width, button_height), 2)
    koikoi_text = japanese_font.render("こいこい", True, (255, 255, 255))
    koikoi_rect = koikoi_text.get_rect(center=(koikoi_x + button_width//2, button_y + button_height//2))
    screen.blit(koikoi_text, koikoi_rect)
    
    # 操作説明
    instruction_text = small_font.render("選択してください", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, choice_y + choice_height - 40))
    screen.blit(instruction_text, instruction_rect)
    
    return {
        'agari_button': (agari_x, button_y, button_width, button_height),
        'koikoi_button': (koikoi_x, button_y, button_width, button_height)
    }

def draw_cpu_choice_message(screen, choice_type, japanese_font, small_font):
    """CPUの選択メッセージを表示する関数
    Args:
        screen: 描画対象のスクリーン
        choice_type: 選択タイプ（'koikoi' または 'agari'）
        japanese_font: 日本語フォント
        small_font: 小さいフォント
    """
    # 半透明の背景オーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # メッセージボックス
    box_width = 500
    box_height = 200
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = (SCREEN_HEIGHT - box_height) // 2
    
    # 背景色を選択に応じて変更
    if choice_type == "koikoi":
        bg_color = (100, 50, 50)  # 赤系（こいこい）
        main_text = "こいこい！"
        sub_text = "ゲームを続行します"
        text_color = (255, 100, 100)
    else:  # agari
        bg_color = (50, 100, 50)  # 緑系（上がり）
        main_text = "上がり！"
        sub_text = "CPUの勝利です"
        text_color = (100, 255, 100)
    
    pygame.draw.rect(screen, bg_color, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 3)
    
    # CPUラベル
    cpu_label = small_font.render("CPU", True, (200, 200, 200))
    cpu_rect = cpu_label.get_rect(center=(SCREEN_WIDTH//2, box_y + 30))
    screen.blit(cpu_label, cpu_rect)
    
    # メインメッセージ
    main_message = japanese_font.render(main_text, True, text_color)
    main_rect = main_message.get_rect(center=(SCREEN_WIDTH//2, box_y + 80))
    screen.blit(main_message, main_rect)
    
    # サブメッセージ
    sub_message = small_font.render(sub_text, True, (255, 255, 255))
    sub_rect = sub_message.get_rect(center=(SCREEN_WIDTH//2, box_y + 130))
    screen.blit(sub_message, sub_rect)

def setup_test_scenario(test_type, deck):
    """テスト用のカード配置を設定する関数
    Args:
        test_type: テストタイプ（3=三光、5=五光、など）
        deck: デッキオブジェクト
    Returns:
        tuple: (player_hand, cpu_hand, field_cards, yama_deck)
    """
    print(f"🎮 テストモード: {test_type}を設定中...")
    
    # カードを名前で検索するヘルパー関数
    def find_card(card_name):
        for card in deck.cards:
            if card.name == card_name:
                return card
        return None
    
    if test_type == "3":  # 三光テスト
        print("📝 三光テスト配置を設定")
        # 三光に必要なカード: 松の鶴、桜の幕、満月
        player_cards = ['pine_crane', 'cherry_curtain', 'full_moon_pampas']
        # 対応する場札（同じ月のカード）
        field_card_names = ['pine_tan', 'cherry_tan', 'pampas_geese']
        # 残りは通常配置
        remaining_player = ['plum_bird', 'wagtail', 'peony_butterfly', 'boar']
        remaining_field = ['plum_tan', 'wisteria_tan', 'peony_tan']
        
    elif test_type == "5":  # 五光テスト
        print("📝 五光テスト配置を設定")
        # 五光に必要なカード: 松の鶴、桜の幕、満月、雨の柳、桐の鳳凰
        player_cards = ['pine_crane', 'cherry_curtain', 'full_moon_pampas', 'michikaze_willows', 'paulownia_phoenix']
        # 対応する場札
        field_card_names = ['pine_tan', 'cherry_tan', 'pampas_geese', 'willows_tan', 'paulownia_1']
        # 残りは通常配置
        remaining_player = ['plum_bird', 'wagtail']
        remaining_field = ['plum_tan']
        
    elif test_type == "猪鹿蝶" or test_type == "inosika":
        print("📝 猪鹿蝶テスト配置を設定")
        # 猪鹿蝶: 萩の猪、鹿、牡丹の蝶
        player_cards = ['boar', 'maple_deer', 'peony_butterfly']
        field_card_names = ['bush_clover_tan', 'maple_tan', 'peony_tan']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'cherry_curtain', 'full_moon_pampas', 'wagtail']
        remaining_field = ['pine_tan', 'cherry_tan', 'pampas_geese']
        
    elif test_type == "花見酒" or test_type == "hanami":
        print("📝 花見酒テスト配置を設定")
        # 花見酒: 桜の幕、菊の杯
        player_cards = ['cherry_curtain', 'chrysanthemum_sake_cup']
        field_card_names = ['cherry_tan', 'chrysanthemum_tan']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'full_moon_pampas', 'plum_bird', 'wagtail', 'peony_butterfly']
        remaining_field = ['pine_tan', 'pampas_geese', 'plum_tan', 'wisteria_tan']
        
    elif test_type == "月見酒" or test_type == "tsukimi":
        print("📝 月見酒テスト配置を設定")
        # 月見酒: 満月、菊の杯
        player_cards = ['full_moon_pampas', 'chrysanthemum_sake_cup']
        field_card_names = ['pampas_geese', 'chrysanthemum_tan']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'cherry_curtain', 'plum_bird', 'wagtail', 'peony_butterfly']
        remaining_field = ['pine_tan', 'cherry_tan', 'plum_tan', 'wisteria_tan']
        
    elif test_type == "花見月見" or test_type == "hanami_tsukimi":
        print("📝 花見酒＋月見酒同時テスト配置を設定")
        # 花見酒: 桜の幕、菊の杯
        # 月見酒: 満月、菊の杯（菊の杯が共通）
        player_cards = ['cherry_curtain', 'full_moon_pampas', 'chrysanthemum_sake_cup']
        field_card_names = ['cherry_tan', 'pampas_geese', 'chrysanthemum_tan']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'plum_bird', 'wagtail', 'peony_butterfly']
        remaining_field = ['pine_tan', 'plum_tan', 'wisteria_tan']
        
    elif test_type == "3枚取り" or test_type == "triple":
        print("📝 3枚取りテスト配置を設定")
        # 3枚取りテスト: プレイヤーが松のカードを持ち、場に松のカードが3枚
        player_cards = ['pine_crane']  # 松の鶴（プレイヤー手札）
        field_card_names = ['pine_tan', 'pine_1', 'pine_2']  # 松の短冊、松カス2枚（場札）
        # 残りは通常配置
        remaining_player = ['plum_bird', 'wagtail', 'peony_butterfly', 'boar', 'cherry_curtain', 'full_moon_pampas']
        remaining_field = ['plum_tan', 'wisteria_tan', 'peony_tan']
        
    elif test_type == "CPU花見酒" or test_type == "cpu_hanami":
        print("📝 CPU花見酒テスト配置を設定")
        # CPU花見酒: CPUが桜の幕、菊の杯を持つ
        player_cards = ['pine_crane', 'plum_bird', 'wagtail', 'peony_butterfly', 'boar', 'full_moon_pampas', 'maple_deer']
        field_card_names = ['cherry_tan', 'chrysanthemum_tan']  # 桜・菊の短冊を場に配置
        # CPUが花見酒の役札を持つように設定
        cpu_cards = ['cherry_curtain', 'chrysanthemum_sake_cup']  # 桜の幕、菊の杯
        # 残りは通常配置
        remaining_player = []
        remaining_field = ['pine_tan', 'plum_tan', 'wisteria_tan', 'peony_tan']
        remaining_cpu = ['willows_tan', 'paulownia_1', 'bush_clover_1', 'maple_1', 'pampas_1']
        
    elif test_type == "CPU月見酒" or test_type == "cpu_tsukimi":
        print("📝 CPU月見酒テスト配置を設定")
        # CPU月見酒: CPUが満月、菊の杯を持つ
        player_cards = ['pine_crane', 'cherry_curtain', 'plum_bird', 'wagtail', 'peony_butterfly', 'boar', 'maple_deer']
        field_card_names = ['pampas_geese', 'chrysanthemum_tan']  # 芒・菊の短冊を場に配置
        # CPUが月見酒の役札を持つように設定
        cpu_cards = ['full_moon_pampas', 'chrysanthemum_sake_cup']  # 満月、菊の杯
        # 残りは通常配置
        remaining_player = []
        remaining_field = ['pine_tan', 'cherry_tan', 'plum_tan', 'wisteria_tan']
        remaining_cpu = ['willows_tan', 'paulownia_1', 'bush_clover_1', 'maple_1', 'peony_1']
        
    elif test_type == "CPU三光" or test_type == "cpu_3":
        print("📝 CPU三光テスト配置を設定")
        # CPU三光: CPUが松の鶴、桜の幕、満月を持つ
        player_cards = ['plum_bird', 'wagtail', 'peony_butterfly', 'boar', 'maple_deer', 'chrysanthemum_sake_cup', 'willows_tan']
        field_card_names = ['pine_tan', 'cherry_tan', 'pampas_geese']  # 松・桜・芒の短冊を場に配置
        # CPUが三光の役札を持つように設定
        cpu_cards = ['pine_crane', 'cherry_curtain', 'full_moon_pampas']  # 松の鶴、桜の幕、満月
        # 残りは通常配置
        remaining_player = []
        remaining_field = ['plum_tan', 'wisteria_tan', 'peony_tan']
        remaining_cpu = ['paulownia_1', 'bush_clover_1', 'maple_1', 'chrysanthemum_1']
        
    else:
        print("❌ 不明なテストタイプ、通常配置にします")
        return None  # 通常のシャッフル配置を使用
    
    # カードを実際に検索して配置
    player_hand = []
    field_cards = []
    used_cards = set()
    
    # プレイヤー手札の設定
    for card_name in player_cards:
        card = find_card(card_name)
        if card:
            player_hand.append(card)
            used_cards.add(card)
            print(f"  🃏 プレイヤー手札: {card.name}")
    
    # 残りのプレイヤー手札
    for card_name in remaining_player:
        if len(player_hand) >= 7:
            break
        card = find_card(card_name)
        if card and card not in used_cards:
            player_hand.append(card)
            used_cards.add(card)
    
    # 場札の設定
    for card_name in field_card_names:
        card = find_card(card_name)
        if card and card not in used_cards:
            field_cards.append(card)
            used_cards.add(card)
            print(f"  🎴 場札: {card.name}")
    
    # 残りの場札
    for card_name in remaining_field:
        if len(field_cards) >= 6:
            break
        card = find_card(card_name)
        if card and card not in used_cards:
            field_cards.append(card)
            used_cards.add(card)
    
    # CPU手札（残りからランダム選択）
    if 'cpu_cards' in locals():
        # CPU専用カード配置がある場合
        cpu_hand = []
        for card_name in cpu_cards:
            card = find_card(card_name)
            if card and card not in used_cards:
                cpu_hand.append(card)
                used_cards.add(card)
                print(f"  🤖 CPU手札: {card.name}")
        
        # 残りのCPU手札
        if 'remaining_cpu' in locals():
            for card_name in remaining_cpu:
                if len(cpu_hand) >= 7:
                    break
                card = find_card(card_name)
                if card and card not in used_cards:
                    cpu_hand.append(card)
                    used_cards.add(card)
        
        # まだ7枚に足りない場合は残りからランダム
        if len(cpu_hand) < 7:
            remaining_cards = [card for card in deck.cards if card not in used_cards]
            random.shuffle(remaining_cards)
            needed = 7 - len(cpu_hand)
            cpu_hand.extend(remaining_cards[:needed])
            used_cards.update(remaining_cards[:needed])
    else:
        # 通常のCPU手札配置
        remaining_cards = [card for card in deck.cards if card not in used_cards]
        random.shuffle(remaining_cards)
        cpu_hand = remaining_cards[:7]
        used_cards.update(cpu_hand)
    
    # 山札（残りすべて）
    yama_deck = [card for card in deck.cards if card not in used_cards]
    random.shuffle(yama_deck)
    
    print(f"✅ テスト配置完了: プレイヤー{len(player_hand)}枚, CPU{len(cpu_hand)}枚, 場札{len(field_cards)}枚, 山札{len(yama_deck)}枚")
    
    return player_hand, cpu_hand, field_cards, yama_deck

# 画面サイズを大きく変更（グローバル変数として定義）
d = pygame.display.get_desktop_sizes()[0]  # デスクトップサイズを取得
SCREEN_WIDTH = int(d[0]*0.8)  # 画面幅をデスクトップの80%に設定（グローバル変数）
SCREEN_HEIGHT = int(d[1]*0.8)  # 画面高さをデスクトップの80%に設定（グローバル変数）
screen_width = SCREEN_WIDTH  # 互換性のための変数
screen_height = SCREEN_HEIGHT  # 互換性のための変数
screen = pygame.display.set_mode((screen_width, screen_height))  # ウィンドウを作成
pygame.display.set_caption("花札")  # ウィンドウタイトルを設定

for card in cards:  # 全カードについて
    card.load_images()  # カード画像を読み込み

# FPSの設定
FPS = 60  # フレームレートを60FPSに設定
clock = pygame.time.Clock()  # クロックオブジェクトを作成

# 背景画像の読み込み
base_dir = os.path.dirname(__file__)  # 現在のファイルのディレクトリを取得
bg_path = os.path.join(base_dir, "assets", "img", "other", "tatami.png")  # 背景画像のパスを構築
background = pygame.image.load(bg_path)  # 背景画像を読み込み
background = pygame.transform.scale(background, (screen_width, screen_height))  # 背景画像を画面サイズにスケール

#日本語フォントの取得
japanese_font=get_japanese_font(36)
small_font = get_japanese_font(24)  # 小さめのフォントを取得

# デッキ準備
deck = Deck(cards)

# 役状態をリセット（新しいゲーム開始時）
from logic import previous_player_yakus, previous_cpu_yakus
previous_player_yakus.clear()
previous_cpu_yakus.clear()
print("💫 新しいゲーム開始 - 役状態をリセット")

# コマンドライン引数をチェック
test_mode = None
if len(sys.argv) > 1:
    test_mode = sys.argv[1]
    print(f"🎯 テストモード指定: {test_mode}")

# カード配置の設定
if test_mode:
    # テスト配置
    result = setup_test_scenario(test_mode, deck)
    if result:
        player_hand, cpu_hand, field_cards, yama_deck = result
    else:
        # テスト失敗時は通常配置
        deck.shuffle()
        player_hand = deck.deal(7)
        cpu_hand = deck.deal(7)
        field_cards = deck.deal(6)
        yama_deck = deck.cards[:]
else:
    # 通常配置
    deck.shuffle()
    player_hand = deck.deal(7)
    cpu_hand = deck.deal(7)
    field_cards = deck.deal(6)
    yama_deck = deck.cards[:]

# 取り札を保存するリスト
player_captured = []
cpu_captured = []

# 縦の間隔を拡大
VERTICAL_SPACING = 150

# カードの座標設定
for i, card in enumerate(player_hand):
    card.x = 50 + i * (card.get_image().get_width() + 10)
    card.y = screen_height - 200
    card.is_face_up = True

for i, card in enumerate(cpu_hand):
    card.x = 50 + i * (card.get_image().get_width() + 10)
    card.y = 100
    card.is_face_up = False

for i, card in enumerate(field_cards):
    card.x = 80 + i * 70
    card.y = 100 + VERTICAL_SPACING
    card.is_face_up = True

# 山札の位置を設定（画面右側）
yama_x = screen_width - 400  # 画面右端から150px内側
yama_y =  100 + VERTICAL_SPACING  # 場札にそろえる
for card in yama_deck:
    card.x = yama_x
    card.y = yama_y
    card.is_face_up = False  # 山札は裏向き

# 情報表示の固定座標を計算（初期配置）
# カード画像の幅を取得（最初のカードから）
card_width = cards[0].get_image().get_width()
# 手札7枚分の右端座標を計算
info_display_x = 50 + 6 * (card_width + 10) + card_width + 20

game_state = {
    'turn': 'player',
    'selected_card': None,
    'cpu_timer': 0,
    'cpu_action_phase': 'waiting',
    'game_over': False,  # ゲーム終了フラグを追加
    'koikoi_choice': False,  # こいこい選択画面フラグ
    'pending_koikoi_choice': False,  # カットイン完了後にこいこい選択を表示するフラグ
    'koikoi_player': None,  # こいこいを選択したプレイヤー（'player' or 'cpu'）
    'current_round_score': 0,  # 現在のラウンドの得点
    'current_yakus': [],  # 現在成立している役
    'cpu_choice_display': False,  # CPUの選択メッセージ表示フラグ
    'cpu_choice_type': None,  # CPUの選択タイプ（'koikoi' または 'agari'）
    'cpu_choice_timer': 0,  # CPUメッセージ表示時間
}

# テストモード情報を表示
if test_mode:
    print(f"\n🎮 {test_mode} テストモード開始！")
    print("プレイヤー手札:")
    for card in player_hand:
        print(f"  🃏 {card.name}")
    print("場札:")
    for card in field_cards:
        print(f"  🎴 {card.name}")
    print("=" * 50)


pygame.mixer.init()  # Pygameのミキサーを初期化
pygame.mixer.music.load("assets/sound/茶屋にて.mp3")  # BGMの読み込み
pygame.mixer.music.set_volume(0.1)  # BGMの音量を設定
pygame.mixer.music.play(-1)  # BGMをループ再生

# メインループ
run = True
while run:
    screen.blit(background, (0, 0))
    
    # アニメーションの更新
    update_animations()
    
    # カットインキューの処理（前のカットインが終了した場合に次を開始）
    process_cutin_queue(SCREEN_WIDTH, SCREEN_HEIGHT, game_state)
    
    # カード描画
    for card in cpu_hand:
        # 重なり合いアニメーション中のカードをチェック
        is_in_merge_animation = False
        for merge_anim in active_merge_animations:
            if card == merge_anim.hand_card:
                is_in_merge_animation = True
                break
        
        if not is_in_merge_animation:
            card.update_and_draw(screen)
    for card in player_hand:
        # 重なり合いアニメーション中のカードをチェック
        is_in_merge_animation = False
        for merge_anim in active_merge_animations:
            if card == merge_anim.hand_card:
                is_in_merge_animation = True
                break
        
        if not is_in_merge_animation:
            card.update_and_draw(screen)
            if game_state['selected_card'] == card:
                pygame.draw.rect(screen, (255, 255, 0),
                               (card.x-2, card.y-2, card.get_image().get_width()+4, card.get_image().get_height()+4), 3)
    
    # 場札描画（特殊表示でない場合のみ）
    for card in field_cards:
        # 山札強調表示中のカードをチェック
        is_in_yama_highlight = False
        for highlight in active_yama_highlights:
            if card == highlight.matched_field_card:
                is_in_yama_highlight = True
                break
        
        # 重なり合いアニメーション中のカードをチェック
        is_in_merge_animation = False
        for merge_anim in active_merge_animations:
            if card == merge_anim.field_card:
                is_in_merge_animation = True
                break
        
        # 通常のアニメーション中のカードをチェック
        is_in_normal_animation = False
        for anim in active_animations:
            if card == anim.card:
                is_in_normal_animation = True
                break
        
        if not is_in_yama_highlight and not is_in_merge_animation and not is_in_normal_animation:
            card.update_and_draw(screen)

    # 山札の描画（一番上のカードのみ表示）
    if len(yama_deck) > 0:
        yama_deck[0].update_and_draw(screen)  # 山札の一番上のカードを描画
        
        # 山札の枚数を表示（日本語フォント使用）
        yama_count_text = japanese_font.render(f"山札: {len(yama_deck)}枚", True, (255, 255, 255))
        screen.blit(yama_count_text, (yama_x - 80, yama_y + 100))
    else:
        # 山札が空の場合
        empty_text = japanese_font.render("山札: なし", True, (255, 100, 100))
        screen.blit(empty_text, (yama_x - 80, yama_y + 100))

    # ゲーム情報の表示（日本語）- 中央上部に移動
    # turn_text = "プレイヤーのターン" if game_state['turn'] == 'player' else "CPUのターン"
    # turn_surface = small_font.render(turn_text, True, (255, 255, 255))
    # turn_rect = turn_surface.get_rect(center=(screen_width//2, 30))
    # screen.blit(turn_surface, turn_rect)

    # CPU手札枚数表示（固定位置）
    cpu_hand_text = small_font.render(f"CPU手札: {len(cpu_hand)}枚", True, (255, 255, 255))
    screen.blit(cpu_hand_text, (info_display_x, 100))
    
    # CPU取り札枚数表示（手札枚数の下）
    cpu_captured_text = small_font.render(f"CPU取り札: {len(cpu_captured)}枚", True, (255, 255, 255))
    screen.blit(cpu_captured_text, (info_display_x, 125))
    
    # CPUポイント表示
    cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
    cpu_score_text = small_font.render(f"CPUポイント: {cpu_score}文", True, (255, 255, 100))
    screen.blit(cpu_score_text, (info_display_x, 150))
    
    # CPU成立役表示（最大2つまで）
    if cpu_yakus:
        for i, yaku in enumerate(cpu_yakus[:2]):
            yaku_text = small_font.render(f"• {yaku}", True, (200, 200, 255))
            screen.blit(yaku_text, (info_display_x, 175 + i * 20))

    # プレイヤー手札枚数表示（固定位置）
    player_hand_text = small_font.render(f"プレイヤー手札: {len(player_hand)}枚", True, (255, 255, 255))
    screen.blit(player_hand_text, (info_display_x, screen_height - 200))
    
    # プレイヤー取り札枚数表示（手札枚数の下）
    player_captured_text = small_font.render(f"プレイヤー取り札: {len(player_captured)}枚", True, (255, 255, 255))
    screen.blit(player_captured_text, (info_display_x, screen_height - 175))
    
    # プレイヤーポイント表示
    player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
    player_score_text = small_font.render(f"プレイヤーポイント: {player_score}文", True, (255, 255, 100))
    screen.blit(player_score_text, (info_display_x, screen_height - 150))
    
    # プレイヤー成立役表示（最大2つまで）
    if player_yakus:
        for i, yaku in enumerate(player_yakus[:2]):
            yaku_text = small_font.render(f"• {yaku}", True, (200, 255, 200))
            screen.blit(yaku_text, (info_display_x, screen_height - 125 + i * 20))

    # 取り札の配置
    draw_sorted_captured_cards(screen, cpu_captured, 50, 10)
    draw_sorted_captured_cards(screen, player_captured, 50, screen_height - 100)

    # 特殊表示の描画
    draw_overlays(screen)  # 重ね合わせ表示を描画
    draw_yama_highlights(screen)  # 山札強調表示を描画
    draw_merge_animations(screen)  # 重なり合いアニメーション描画
    draw_normal_animations(screen)  # 通常のアニメーション描画
    draw_captured_highlights(screen)  # 取り札ハイライト表示を描画
    draw_cutin_animations(screen)  # カットインアニメーション描画

    # こいこい選択画面の描画
    koikoi_buttons = None
    if game_state['koikoi_choice']:
        koikoi_buttons = draw_koikoi_choice_screen(screen, game_state, japanese_font, small_font)

    # CPUの選択メッセージ表示
    if game_state['cpu_choice_display']:
        draw_cpu_choice_message(screen, game_state['cpu_choice_type'], japanese_font, small_font)
        game_state['cpu_choice_timer'] -= 1
        if game_state['cpu_choice_timer'] <= 0:
            game_state['cpu_choice_display'] = False
            game_state['cpu_choice_type'] = None

    # CPUターンの処理（こいこい選択中・ゲーム終了後・CPUメッセージ表示中は停止）
    if (game_state['turn'] == 'cpu' and len(cpu_hand) > 0 and 
        not is_animations_active() and not game_state['koikoi_choice'] and
        not game_state['game_over'] and not game_state['cpu_choice_display']):  # ゲーム終了後は停止
        game_state['cpu_timer'] += 1
        if game_state['cpu_timer'] > 90:
            import random
            
            if game_state['cpu_action_phase'] == 'waiting':
                # 戦略的にカードを選択
                cpu_card = choose_best_cpu_card(cpu_hand, cpu_captured, field_cards)
                game_state['selected_cpu_card'] = cpu_card
                
                game_state['cpu_action_phase'] = 'card_selected'
                game_state['cpu_timer'] = 0
                print(f"CPU: {cpu_card.name} を選択しました")
                
            elif game_state['cpu_action_phase'] == 'card_selected':
                if game_state['cpu_timer'] > 30:
                    cpu_card = game_state['selected_cpu_card']
                    
                    matched = False
                    matching_cards = [field_card for field_card in field_cards if field_card.month == cpu_card.month]
                    if matching_cards:
                        print(f"CPU Match! {cpu_card.name} と同じ月のカード {len(matching_cards)}枚: {[c.name for c in matching_cards]}")
                        cpu_hand.remove(cpu_card)
                        
                        # 同じ月のカードを全て場札から削除
                        for matching_card in matching_cards:
                            field_cards.remove(matching_card)
                        
                        # 複数枚取得のアニメーション（新しい関数を使用）
                        capture_multiple_cards_with_animation(cpu_card, matching_cards, cpu_captured, True, screen_height, screen_width, game_state)
                        matched = True
                    
                    if not matched:
                        print(f"CPU: {cpu_card.name} を場に出します")
                        cpu_hand.remove(cpu_card)
                        cpu_card.is_face_up = True
                        field_cards.append(cpu_card)
                        
                        # 場札の位置を更新して即座に場に表示
                        update_field_positions(field_cards)
                    
                    # 山札処理を次のフェーズに延期
                    game_state['cpu_action_phase'] = 'draw_yama'
                    game_state['cpu_timer'] = 0
                    
            elif game_state['cpu_action_phase'] == 'draw_yama':
                # アニメーションが完了してから山札処理を実行（少し遅延を追加）
                if not is_animations_active() and game_state['cpu_timer'] > 30:  # 0.5秒遅延
                    # 山札処理前に場札の位置を整形
                    update_field_positions(field_cards)
                    draw_from_yama_deck(yama_deck, field_cards, cpu_captured, player_captured, True, screen_width, screen_height, game_state)
                    
                    game_state['cpu_action_phase'] = 'waiting'
                    game_state['turn'] = 'player'
                    game_state['cpu_timer'] = 0

    # CPUの選択カードのハイライト表示（金色に変更）
    if game_state['turn'] == 'cpu' and game_state['cpu_action_phase'] == 'card_selected' and 'selected_cpu_card' in game_state:
        cpu_card = game_state['selected_cpu_card']
        pygame.draw.rect(screen, (255, 215, 0),  # 修正: 赤色(255, 0, 0)→金色(255, 215, 0)
                       (cpu_card.x-2, cpu_card.y-2, cpu_card.get_image().get_width()+4, cpu_card.get_image().get_height()+4), 3)
    
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            # こいこい選択の処理
            if game_state['koikoi_choice'] and koikoi_buttons:
                agari_x, agari_y, agari_w, agari_h = koikoi_buttons['agari_button']
                koikoi_x, koikoi_y, koikoi_w, koikoi_h = koikoi_buttons['koikoi_button']
                
                if (agari_x <= mx <= agari_x + agari_w and 
                    agari_y <= my <= agari_y + agari_h):
                    # 上がりを選択
                    print("🎯 プレイヤーが上がりを選択！")
                    game_state['koikoi_choice'] = False
                    game_state['game_over'] = True
                    # 結果を設定（とりあえず勝利として処理）
                    result_text = japanese_font.render("プレイヤーの勝利！", True, (0, 255, 0))
                    game_state['result_text'] = result_text
                    
                elif (koikoi_x <= mx <= koikoi_x + koikoi_w and 
                      koikoi_y <= my <= koikoi_y + koikoi_h):
                    # こいこいを選択
                    print("🔥 プレイヤーがこいこいを選択！")
                    game_state['koikoi_choice'] = False
                    # ゲーム続行
                    
            elif (game_state['turn'] == 'player' and not is_animations_active() and 
                  not game_state['koikoi_choice'] and not game_state['game_over']):
                # 手札選択処理
                for card in player_hand:
                    card_width = card.get_image().get_width()
                    card_height = card.get_image().get_height()
                    if card.x <= mx <= card.x + card_width and card.y <= my <= card.y + card_height:
                        if game_state['selected_card'] == card:
                            game_state['selected_card'] = None
                        else:
                            game_state['selected_card'] = card
                        break

                if game_state['selected_card']:
                    clicked_field_card = False
                    for card in field_cards:
                        card_width = card.get_image().get_width()
                        card_height = card.get_image().get_height()
                        if card.x <= mx <= card.x + card_width and card.y <= my <= card.y + card_height:
                            clicked_field_card = True
                            if game_state['selected_card'].month == card.month:
                                # 同じ月のカードを全て検索
                                matching_cards = [field_card for field_card in field_cards if field_card.month == game_state['selected_card'].month]
                                print(f"Match! {game_state['selected_card'].name} と同じ月のカード {len(matching_cards)}枚: {[c.name for c in matching_cards]}")
                                
                                selected_card = game_state['selected_card']
                                player_hand.remove(selected_card)
                                
                                # 同じ月のカードを全て場札から削除
                                for matching_card in matching_cards:
                                    field_cards.remove(matching_card)
                                
                                # 複数枚取得のアニメーション（新しい関数を使用）
                                capture_multiple_cards_with_animation(selected_card, matching_cards, player_captured, False, screen_height, screen_width, game_state)
                                game_state['selected_card'] = None
                                
                                # プレイヤーの山札処理を遅延
                                game_state['player_yama_pending'] = True
                                game_state['cpu_timer'] = 0
                            else:
                                print("No match!")
                                game_state['selected_card'] = None
                            break
                    
                    # マッチしない場合の処理
                    if not clicked_field_card:
                        has_match = False
                        for field_card in field_cards:
                            if game_state['selected_card'].month == field_card.month:
                                has_match = True
                                break
                        
                        if not has_match:
                            print(f"Player: マッチするカードがないため {game_state['selected_card'].name} を場に出します")
                            selected_card = game_state['selected_card']
                            player_hand.remove(selected_card)
                            selected_card.is_face_up = True
                            field_cards.append(selected_card)
                            
                            # 場札の位置を更新して即座に場に表示
                            update_field_positions(field_cards)
                            
                            game_state['selected_card'] = None
                            
                            # プレイヤーの山札処理を遅延（場に出てから実行）
                            game_state['player_yama_pending'] = True
                            game_state['player_yama_delay'] = 60  # 1秒遅延を追加
    
    # プレイヤーの遅延山札処理（こいこい選択中・ゲーム終了後は停止）
    if (game_state.get('player_yama_pending', False) and 
        not is_animations_active() and not game_state['koikoi_choice'] and
        not game_state['game_over']):
        # 遅延カウントがある場合は減少させる
        if game_state.get('player_yama_delay', 0) > 0:
            game_state['player_yama_delay'] -= 1
        else:
            # 遅延時間が終了したら山札処理を実行
            # 山札処理前に場札の位置を整形
            update_field_positions(field_cards)
            draw_from_yama_deck(yama_deck, field_cards, cpu_captured, player_captured, False, screen_width, screen_height, game_state)
            game_state['player_yama_pending'] = False
            if 'player_yama_delay' in game_state:
                del game_state['player_yama_delay']  # 遅延カウンタを削除
            game_state['turn'] = 'cpu'
            game_state['cpu_timer'] = 0
    
    # CPUが役で勝利した場合の処理
    if (game_state['game_over'] and game_state.get('winner') == 'cpu' and 
        'result_text' not in game_state):
        # CPUの役による勝利
        cpu_score = game_state.get('final_score_cpu', 0)
        cpu_yakus = game_state.get('final_yakus_cpu', [])
        
        print(f"\n=== CPU役による勝利 ===")
        print(f"CPU最終得点: {cpu_score}文")
        if cpu_yakus:
            print("CPUの成立役:")
            for yaku in cpu_yakus:
                print(f"  • {yaku}")
        
        result_text = japanese_font.render("CPUの勝利！", True, (255, 0, 0))
        game_state['result_text'] = result_text
        print("\n💻 CPUの役による勝利！ 💻")
    
    
    # ゲーム終了判定（全てのアニメーションが終了してから実行、こいこい選択中は停止）
    if (not game_state['game_over'] and 
        len(player_hand) == 0 and 
        len(cpu_hand) == 0 and 
        not is_animations_active() and
        not game_state['koikoi_choice']):  # こいこい選択中は終了判定も停止
        
        # 実際の役計算を実行
        print("=== プレイヤーの役計算 ===")
        player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
        print(f"プレイヤー合計得点: {player_score}文")
        if player_yakus:
            print("成立した役:")
            for yaku in player_yakus:
                print(f"  • {yaku}")
        else:
            print("役なし")
        
        print("\n=== CPUの役計算 ===")
        cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
        print(f"CPU合計得点: {cpu_score}文")
        if cpu_yakus:
            print("成立した役:")
            for yaku in cpu_yakus:
                print(f"  • {yaku}")
        else:
            print("役なし")
        
        print(f"\n=== 最終結果 ===")
        print(f"プレイヤー: {player_score}文")
        if player_yakus:
            print("プレイヤーの役:")
            for yaku in player_yakus:
                print(f"  • {yaku}")
        else:
            print("プレイヤー: 役なし")
            
        print(f"CPU: {cpu_score}文")
        if cpu_yakus:
            print("CPUの役:")
            for yaku in cpu_yakus:
                print(f"  • {yaku}")
        else:
            print("CPU: 役なし")

        if player_score > cpu_score:
            result_text = japanese_font.render("プレイヤーの勝利！", True, (0, 255, 0))
            print("\n🎊 プレイヤーの勝利！ 🎊")
            game_state['game_over'] = True
        elif cpu_score > player_score:
            result_text = japanese_font.render("CPUの勝利！", True, (255, 0, 0))
            print("\n💻 CPUの勝利！ 💻")
            game_state['game_over'] = True
        else:
            result_text = japanese_font.render("引き分け！", True, (255, 255, 0))
            print("\n🤝 引き分け！ 🤝")
            game_state['game_over'] = True
        
        # 結果テキストをgame_stateに保存
        game_state['result_text'] = result_text
    
    # ゲーム終了後の結果表示
    if game_state['game_over'] and 'result_text' in game_state:
        # 結果を画面中央に表示
        text_rect = game_state['result_text'].get_rect(center=(screen_width//2, screen_height//2))
        screen.blit(game_state['result_text'], text_rect)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()