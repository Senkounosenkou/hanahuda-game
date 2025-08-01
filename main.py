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
    draw_captured_highlights,  #  取り札ハイライト描画関数
    draw_merge_animations,  #  重なり合いアニメーション描画関数
    draw_normal_animations,  #  通常のアニメーション描画関数
    draw_cutin_animations,  #  カットインアニメーション描画関数
    calculate_score,  #  役計算関数
    set_sound_effects,  #  効果音設定関数
    active_yama_highlights,  # アクティブな山札強調表示リスト
    active_merge_animations,  #  アクティブな重なり合いアニメーションリスト
    active_animations,  #  アクティブな通常のアニメーションリスト
    active_cutin_animations,  # アクティブなカットインアニメーションリスト
    cutin_queue  # カットインキュー
)

pygame.init()  # Pygameを初期化

# pyinstaller対応: アイコンファイルのパス解決
if getattr(sys, 'frozen', False):
    # pyinstallerで作成された実行ファイルの場合
    base_dir = sys._MEIPASS
else:
    # 開発環境（.pyファイル実行）の場合
    base_dir = os.path.dirname(__file__)

icon_path = os.path.join(base_dir, "assets", "img", "cards", "icon.png")
icon = pygame.image.load(icon_path) 
# アイコンを設定
pygame.display.set_icon(icon)#左上



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
                priority += 1800  # 花見酒または月見酒完成
        elif card.name == 'full_moon_pampas':  # 満月
            # 菊の杯があるかチェック
            has_sake_cup = any(c.name == 'chrysanthemum_sake_cup' for c in cpu_captured)
            if has_sake_cup:
                priority += 1800  # 月見酒完成
        
        # 3. 光札は常に高優先度
        card_type = get_card_type_by_name(card.name)
        if card_type == 'bright':
            priority += 300
        elif card.name == 'chrysanthemum_sake_cup':#菊の杯より強いものはない
            priority += 2000
        
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
    
    # 取れるカードがあるかチェック（優先度1000以上は場札とマッチするカード）
    can_capture = any(priority >= 1000 for card, priority in card_priorities)
    
    if can_capture:
        # 取れるカードがある場合：最高優先度のカードを選択
        card_priorities.sort(key=lambda x: x[1], reverse=True)
        best_card = card_priorities[0][0]
        print("🤖 CPU カード選択分析（取得可能）:")
        for card, priority in card_priorities:
            matching = [fc.name for fc in field_cards if fc.month == card.month]
            match_info = f" -> {matching}" if matching else " (マッチなし)"
            print(f"  {card.name}: 優先度{priority}{match_info}")
        print(f"🎯 CPU選択: {best_card.name} (優先度: {card_priorities[0][1]}) - 取得")
    else:
        # 取れるカードがない場合：一番安いカード（最低優先度）を捨てる
        card_priorities.sort(key=lambda x: x[1])  # 昇順ソート（低い優先度が先）
        best_card = card_priorities[0][0]
        print("🤖 CPU カード選択分析（捨て札）:")
        for card, priority in card_priorities:
            card_type = get_card_type_by_name(card.name)
            print(f"  {card.name}: 優先度{priority} ({card_type})")
        print(f"🎯 CPU選択: {best_card.name} (優先度: {card_priorities[0][1]}) - 捨て札")
    
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
        # if i >= 3:  # 最大3つまで表示
        #     break
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

def draw_victory_screen(screen, winner, player_score, cpu_score, yakus, japanese_font, small_font):
    """勝利画面を描画する関数（モーダルダイアログ形式）
    Args:
        screen: 描画対象のスクリーン
        winner: 勝者（'player' または 'cpu' または 'draw'）
        player_score: プレイヤーの得点
        cpu_score: CPUの得点
        yakus: 成立した役のリスト
        japanese_font: 日本語フォント
        small_font: 小さいフォント
    Returns:
        dict: クリック可能なボタンの情報
    """
    # 半透明の背景オーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 勝利画面の背景
    victory_width = 700
    victory_height = 500
    victory_x = (SCREEN_WIDTH - victory_width) // 2
    victory_y = (SCREEN_HEIGHT - victory_height) // 2
    
    # 勝者によって背景色を変更
    if winner == 'player':
        bg_color = (50, 100, 50)  # 緑系
        title_color = (100, 255, 100)
        title_text = "プレイヤーの勝利！"
    elif winner == 'cpu':
        bg_color = (100, 50, 50)  # 赤系
        title_color = (255, 100, 100)
        title_text = "CPUの勝利！"
    else:
        bg_color = (80, 80, 50)  # 黄系
        title_color = (255, 255, 100)
        title_text = "引き分け！"
    
    pygame.draw.rect(screen, bg_color, (victory_x, victory_y, victory_width, victory_height))
    pygame.draw.rect(screen, (255, 255, 255), (victory_x, victory_y, victory_width, victory_height), 3)
    
    # タイトル表示
    title_render = japanese_font.render(title_text, True, title_color)
    title_rect = title_render.get_rect(center=(SCREEN_WIDTH//2, victory_y + 60))
    screen.blit(title_render, title_rect)
    
    # 得点表示
    score_y = victory_y + 120
    player_score_text = small_font.render(f"プレイヤー: {player_score}文", True, (200, 255, 200))
    cpu_score_text = small_font.render(f"CPU: {cpu_score}文", True, (255, 200, 200))
    
    player_score_rect = player_score_text.get_rect(center=(SCREEN_WIDTH//2 - 100, score_y))
    cpu_score_rect = cpu_score_text.get_rect(center=(SCREEN_WIDTH//2 + 100, score_y))
    
    screen.blit(player_score_text, player_score_rect)
    screen.blit(cpu_score_text, cpu_score_rect)
    
    # 成立した役を表示
    yaku_y = victory_y + 170
    if yakus:
        yaku_title = small_font.render("成立した役:", True, (255, 255, 255))
        yaku_title_rect = yaku_title.get_rect(center=(SCREEN_WIDTH//2, yaku_y))
        screen.blit(yaku_title, yaku_title_rect)
        
        for i, yaku in enumerate(yakus[:4]):  # 最大4つまで表示
            yaku_text = small_font.render(f"• {yaku}", True, (200, 255, 200))
            yaku_rect = yaku_text.get_rect(center=(SCREEN_WIDTH//2, yaku_y + 40 + i * 25))
            screen.blit(yaku_text, yaku_rect)
    
    # 2つのボタン：もう一度遊ぶ と 終了
    button_width = 150
    button_height = 50
    button_spacing = 30
    total_width = button_width * 2 + button_spacing
    start_x = SCREEN_WIDTH//2 - total_width//2
    button_y = victory_y + victory_height - 100
    
    # もう一度遊ぶボタン
    play_again_x = start_x
    pygame.draw.rect(screen, (50, 150, 50), (play_again_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (play_again_x, button_y, button_width, button_height), 2)
    
    play_again_text = small_font.render("もう一度遊ぶ", True, (255, 255, 255))
    play_again_rect = play_again_text.get_rect(center=(play_again_x + button_width//2, button_y + button_height//2))
    screen.blit(play_again_text, play_again_rect)
    
    # 終了ボタン
    quit_x = start_x + button_width + button_spacing
    pygame.draw.rect(screen, (150, 50, 50), (quit_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (quit_x, button_y, button_width, button_height), 2)
    
    quit_text = small_font.render("終了", True, (255, 255, 255))
    quit_rect = quit_text.get_rect(center=(quit_x + button_width//2, button_y + button_height//2))
    screen.blit(quit_text, quit_rect)
    
    # 操作説明
    instruction_text = small_font.render("選択してください", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, victory_y + victory_height - 40))
    screen.blit(instruction_text, instruction_rect)
    
    return {
        'play_again_button': (play_again_x, button_y, button_width, button_height),
        'quit_button': (quit_x, button_y, button_width, button_height)
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

def draw_round_result_screen(screen, game_state, japanese_font, small_font):
    """ラウンド結果画面を描画する関数"""
    # 半透明の背景オーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 結果画面の背景
    result_width = 700
    result_height = 500
    result_x = (SCREEN_WIDTH - result_width) // 2
    result_y = (SCREEN_HEIGHT - result_height) // 2
    
    pygame.draw.rect(screen, (50, 50, 100), (result_x, result_y, result_width, result_height))
    pygame.draw.rect(screen, (255, 255, 255), (result_x, result_y, result_width, result_height), 3)
    
    # ラウンド情報
    round_text = japanese_font.render(f"第{game_state['current_round']}回戦 結果", True, (255, 255, 255))
    round_rect = round_text.get_rect(center=(SCREEN_WIDTH//2, result_y + 50))
    screen.blit(round_text, round_rect)
    
    # このラウンドの結果
    current_result = game_state['round_results'][-1] if game_state['round_results'] else {}
    player_round_score = current_result.get('player_score', 0)
    cpu_round_score = current_result.get('cpu_score', 0)
    round_winner = current_result.get('winner', '引き分け')
    
    # このラウンドの得点表示
    player_score_text = small_font.render(f"プレイヤー: {player_round_score}文", True, (200, 255, 200))
    player_score_rect = player_score_text.get_rect(center=(SCREEN_WIDTH//2 - 100, result_y + 150))
    screen.blit(player_score_text, player_score_rect)
    
    cpu_score_text = small_font.render(f"CPU: {cpu_round_score}文", True, (255, 200, 200))
    cpu_score_rect = cpu_score_text.get_rect(center=(SCREEN_WIDTH//2 + 100, result_y + 150))
    screen.blit(cpu_score_text, cpu_score_rect)
    
    # ラウンド勝者表示
    winner_text = japanese_font.render(f"勝者: {round_winner}", True, (255, 255, 0))
    winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, result_y + 200))
    screen.blit(winner_text, winner_rect)
    
    # 総合得点表示
    total_text = small_font.render("総合得点", True, (255, 255, 255))
    total_rect = total_text.get_rect(center=(SCREEN_WIDTH//2, result_y + 270))
    screen.blit(total_text, total_rect)
    
    player_total_text = small_font.render(f"プレイヤー: {game_state['player_total_score']}文", True, (200, 255, 200))
    player_total_rect = player_total_text.get_rect(center=(SCREEN_WIDTH//2 - 100, result_y + 310))
    screen.blit(player_total_text, player_total_rect)
    
    cpu_total_text = small_font.render(f"CPU: {game_state['cpu_total_score']}文", True, (255, 200, 200))
    cpu_total_rect = cpu_total_text.get_rect(center=(SCREEN_WIDTH//2 + 100, result_y + 310))
    screen.blit(cpu_total_text, cpu_total_rect)
    
    # 次のラウンドまたは最終結果のメッセージ
    if game_state['current_round'] < game_state['total_rounds']:
        next_text = small_font.render(f"次は第{game_state['current_round'] + 1}回戦です", True, (255, 255, 255))
    else:
        # 最終結果
        if game_state['player_total_score'] > game_state['cpu_total_score']:
            final_winner = "プレイヤーの総合勝利！"
            final_color = (0, 255, 0)
        elif game_state['cpu_total_score'] > game_state['player_total_score']:
            final_winner = "CPUの総合勝利！"
            final_color = (255, 0, 0)
        else:
            final_winner = "総合引き分け！"
            final_color = (255, 255, 0)
        
        next_text = japanese_font.render(final_winner, True, final_color)
    
    next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, result_y + 380))
    screen.blit(next_text, next_rect)
    
    # 操作説明
    instruction_text = small_font.render("クリックして続行", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, result_y + 450))
    screen.blit(instruction_text, instruction_rect)

def calculate_final_scores(game_state, winner, loser, winner_score, winner_yakus, loser_score, loser_yakus):
    """
    新しい得点計算ロジック（こいこい後の特殊ルール対応）
    
    Args:
        game_state: ゲーム状態
        winner: 勝者（'player' or 'cpu'）
        loser: 敗者（'player' or 'cpu'）
        winner_score: 勝者の得点
        winner_yakus: 勝者の役リスト
        loser_score: 敗者の得点
        loser_yakus: 敗者の役リスト
    
    Returns:
        tuple: (勝者最終得点, 敗者最終得点)
    """
    print(f" 得点計算: {winner}勝利 {winner_score}文 vs {loser} {loser_score}文")
    
    final_winner_score = winner_score
    final_loser_score = 0  # 敗者は必ず0点

    # こいこい宣言後の特殊ルール処理
    if game_state['koikoi_was_declared']:
        koikoi_declarer = game_state['koikoi_declarer']
        # こいこい宣言者が負けた場合、勝者の得点を2倍
        if koikoi_declarer != winner:
            print(f"🚨 こいこい２倍付: {winner_score}文 → {winner_score * 2}文")
            final_winner_score = winner_score * 2
        # どちらも役を作らなかった場合の処理（両者0点）
        if winner_score == 0 and loser_score == 0:
            print(f"🤝 こいこい後両者無得点 - 得点なし")
            final_winner_score = 0
            final_loser_score = 0

    print(f"� 最終得点: 勝者{final_winner_score}文, 敗者{final_loser_score}文")

    return final_winner_score, final_loser_score

def reset_for_next_round(game_state):
    """次のラウンドのためにゲーム状態をリセット"""
    global player_hand, cpu_hand, field_cards, yama_deck, player_captured, cpu_captured
    
    # 新しいゲームのためにデッキをリセット
    deck = Deck(cards)
    deck.shuffle()
    
    # カード配置をリセット
    player_hand = deck.deal(7)
    cpu_hand = deck.deal(7)
    field_cards = deck.deal(6)
    yama_deck = deck.cards[:]
    
    # 取り札をリセット
    player_captured = []
    cpu_captured = []
    
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

    # 山札の位置を設定
    yama_x = screen_width - 400
    yama_y = 100 + VERTICAL_SPACING
    for card in yama_deck:
        card.x = yama_x
        card.y = yama_y
        card.is_face_up = False
    
    # ゲーム状態をリセット
    # 先行プレイヤーの決定（花札の正式ルール）
    if game_state['current_round'] == 1:
        # 1回戦はランダム
        game_state['turn'] = random.choice(['player', 'cpu'])
        print(f"🎲 1回戦 - ランダム先行: {'プレイヤー' if game_state['turn'] == 'player' else 'CPU'}")
    else:
        # 2回戦以降は前回戦の勝者が先行
        if game_state['round_results']:
            last_result = game_state['round_results'][-1]
            if last_result['winner'] == 'プレイヤー':
                game_state['turn'] = 'player'
                print(f"🏆 第{game_state['current_round']}回戦 - 前回勝者（プレイヤー）が先行")
            elif last_result['winner'] == 'CPU':
                game_state['turn'] = 'cpu'
                print(f"🏆 第{game_state['current_round']}回戦 - 前回勝者（CPU）が先行")
            else:
                # 引き分けの場合は前回と同じ先行者
                # または前々回の勝者を維持（実装により異なる）
                game_state['turn'] = random.choice(['player', 'cpu'])
                print(f"🤝 第{game_state['current_round']}回戦 - 前回引き分けのためランダム先行: {'プレイヤー' if game_state['turn'] == 'player' else 'CPU'}")
        else:
            # 念のための安全処理
            game_state['turn'] = random.choice(['player', 'cpu'])
            print(f"⚠️ 第{game_state['current_round']}回戦 - 結果記録がないためランダム先行")
    game_state['selected_card'] = None
    game_state['cpu_timer'] = 0
    game_state['cpu_action_phase'] = 'waiting'
    game_state['game_over'] = False
    game_state['koikoi_choice'] = False
    game_state['pending_koikoi_choice'] = False
    game_state['koikoi_player'] = None
    game_state['koikoi_was_declared'] = False  
    game_state['koikoi_declarer'] = None  
    game_state['cpu_agari'] = False  
    game_state['current_round_score'] = 0
    game_state['current_yakus'] = []
    game_state['cpu_choice_display'] = False
    game_state['cpu_choice_type'] = None
    game_state['cpu_choice_timer'] = 0
    game_state['show_round_result'] = False
    game_state['round_result_timer'] = 0
    
    # 遅延処理フラグをリセット
    game_state['player_yama_delay'] = 0
    game_state['cpu_yama_delay'] = 0
    game_state['player_yama_pending'] = False
    if 'player_yama_delay' in game_state:
        del game_state['player_yama_delay']
    if 'cpu_yama_delay' in game_state:
        del game_state['cpu_yama_delay']
    
    # CPUの勝利関連フラグをクリア
    if 'winner' in game_state:
        del game_state['winner']
    if 'final_score_cpu' in game_state:
        del game_state['final_score_cpu']
    if 'final_yakus_cpu' in game_state:
        del game_state['final_yakus_cpu']
    if 'result_text' in game_state:
        del game_state['result_text']
    
    # 勝利画面関連フラグをクリア
    game_state['show_victory_screen'] = False
    game_state['victory_winner'] = None
    game_state['victory_player_score'] = 0
    game_state['victory_cpu_score'] = 0
    game_state['victory_yakus'] = []
    
    # 役状態をリセット
    from logic import previous_player_yakus, previous_cpu_yakus
    previous_player_yakus.clear()
    previous_cpu_yakus.clear()
    
    # アニメーション状態をリセット
    try:
        from logic import active_animations
        active_animations.clear()
    except ImportError:
        pass
    
    try:
        from logic import active_merge_animations
        active_merge_animations.clear()
    except ImportError:
        pass
    
    try:
        from logic import active_captured_highlights
        active_captured_highlights.clear()
    except ImportError:
        pass
    
    try:
        from logic import active_yama_highlights
        active_yama_highlights.clear()
    except ImportError:
        pass
    
    try:
        from logic import cutin_queue
        cutin_queue.clear()
    except ImportError:
        pass
    
    # カットインアニメーションもリセット（存在する場合）
    try:
        from logic import active_cutin_animations
        active_cutin_animations.clear()
    except ImportError:
        pass
    
    print(f"🎮 第{game_state['current_round']}回戦開始！")

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
        
    elif test_type == "種" or test_type == "tane":
        print("📝 種テスト配置を設定")
        # 種5枚: 猪、鹿、蝶、杯、鳥を プレイヤーに配布
        player_cards = ['boar', 'maple_deer', 'peony_butterfly', 'chrysanthemum_sake_cup', 'plum_bird']
        field_card_names = ['bush_clover_tan', 'maple_tan', 'peony_tan', 'chrysanthemum_tan', 'plum_tan']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'cherry_curtain']
        remaining_field = ['pine_tan']
        
    elif test_type == "短" or test_type == "tan":
        print("📝 短テスト配置を設定")
        # 短5枚: 松、梅、桜、藤、菖蒲の短冊を プレイヤーに配布
        player_cards = ['pine_tan', 'plum_tan', 'cherry_tan', 'wisteria_tan', 'iris_tan']
        field_card_names = ['pine_1', 'plum_1', 'cherry_1', 'wisteria_1', 'iris_1']
        # 残りは通常配置
        remaining_player = ['pine_crane', 'plum_bird']
        remaining_field = ['peony_tan']
        
    elif test_type == "カス" or test_type == "kasu":
        print("📝 カステスト配置を設定")
        # カス10枚: 各月のカス札を プレイヤーに配布
        player_cards = ['pine_1', 'pine_2', 'plum_1', 'plum_2', 'cherry_1', 'cherry_2', 'wisteria_1']
        field_card_names = ['wisteria_2', 'iris_1', 'iris_2']  # 残り3枚を場に配布してプレイヤーが取得
        # 残りは通常配置
        remaining_player = []
        remaining_field = ['pine_tan', 'plum_tan', 'cherry_tan']
        
    elif test_type == "山札選択" or test_type == "yama_select":
        print("📝 山札選択テスト配置を設定 - 場に松のカード2枚、プレイヤーが松のカードを引く")
        # 場札に松の短冊と松カス1を配置（2枚のみ）
        # プレイヤーが山札から松の鶴を引いて選択する
        player_cards = []  # プレイヤー手札は松以外
        field_card_names = ['pine_tan', 'pine_1']  # 松の短冊と松カス1（2枚のみ）
        # 残りは通常配置
        remaining_player = ['plum_bird', 'cherry_curtain', 'wagtail', 'iris_bridge', 'peony_butterfly', 'maple_1', 'bush_clover_1']
        remaining_field = ['plum_tan', 'cherry_tan', 'wisteria_tan', 'iris_tan']
        
        # 山札の先頭に松の鶴（光札）を配置
        target_yama_cards = ['pine_crane']  # 松の鶴（1月の光札）
        
    elif test_type == "山札選択2" or test_type == "yama_select2":
        print("📝 山札選択テスト2配置を設定（価値比較）")
        # 9月の菊を使った高価値vs低価値選択テスト
        # 場札に菊の杯（種札・高価値）と菊カス（カス札・低価値）を配置
        # 山札から菊の短冊を引く設定
        player_cards = ['chrysanthemum_bird']  # 9月のダミー種札（実際は存在しないが、手札調整用）
        field_card_names = ['chrysanthemum_sake_cup', 'chrysanthemum_1', 'chrysanthemum_2']  # 菊杯、菊カス1、菊カス2
        # 残りは通常配置
        remaining_player = ['pine_crane', 'plum_bird', 'cherry_curtain', 'wagtail', 'iris_bridge']
        remaining_field = ['pine_tan', 'plum_tan', 'cherry_tan']
        
        # 山札の先頭に菊の短冊を配置
        target_yama_cards = ['chrysanthemum_tan']  # 菊の短冊（9月の短冊札）
        
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
    
    # 山札の先頭に特定のカードを配置（テスト用）
    if 'target_yama_cards' in locals():
        print(f"📋 山札先頭カード設定: {target_yama_cards}")
        # 指定されたカードを山札から探して先頭に移動
        for card_name in reversed(target_yama_cards):  # 逆順で処理（最後のカードが最前面になる）
            target_card = find_card(card_name)
            if target_card and target_card in yama_deck:
                yama_deck.remove(target_card)
                yama_deck.insert(0, target_card)  # 先頭に挿入
                print(f"  🎯 山札先頭に配置: {target_card.name}")
    
    random.shuffle(yama_deck[1:])  # 先頭以外をシャッフル（先頭カードは固定）
    
    print(f"✅ テスト配置完了: プレイヤー{len(player_hand)}枚, CPU{len(cpu_hand)}枚, 場札{len(field_cards)}枚, 山札{len(yama_deck)}枚")
    if 'target_yama_cards' in locals():
        print(f"  🔍 山札先頭カード: {yama_deck[0].name if yama_deck else 'なし'}")
    
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

# 背景画像の読み込み - pyinstaller対応
if getattr(sys, 'frozen', False):
    # pyinstallerで作成された実行ファイルの場合
    base_dir = sys._MEIPASS
else:
    # 開発環境（.pyファイル実行）の場合
    base_dir = os.path.dirname(__file__)  # 現在のファイルのディレクトリを取得

bg_path = os.path.join(base_dir, "assets", "img", "other", "tatami.png")  # 背景画像のパスを構築
background = pygame.image.load(bg_path)  # 背景画像を読み込み
background = pygame.transform.scale(background, (screen_width, screen_height))  # 背景画像を画面サイズにスケール

#日本語フォントの取得
japanese_font=get_japanese_font(36)
small_font = get_japanese_font(24)  # ちょっと小さめ

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

# 情報表示の動的座標計算用のカード幅を取得（最初のカードから）
card_width = cards[0].get_image().get_width()

first_player = random.choice(['player', 'cpu'])  # 最初のプレイヤーをランダムに決定
print(f"🎲 最初のプレイヤー: {first_player}")

game_state = {
    # 'turn': 'player',
    'turn': first_player,   
    'selected_card': None,
    'cpu_timer': 0,
    'cpu_action_phase': 'waiting',
    'game_over': False,  # ゲーム終了フラグを追加
    'koikoi_choice': False,  # こいこい選択画面フラグ
    'pending_koikoi_choice': False,  # カットイン完了後にこいこい選択を表示するフラグ
    'koikoi_player': None,  # こいこいを選択したプレイヤー（'player' or 'cpu'）
    'koikoi_was_declared': False,  # このラウンドでこいこいが宣言されたかのフラグ
    'koikoi_declarer': None,  # こいこいを宣言したプレイヤー（'player' or 'cpu'）
    'cpu_agari': False,  # CPUが上がりを選択したフラグ
    'current_round_score': 0,  # 現在のラウンドの得点
    'current_yakus': [],  # 現在成立している役
    'cpu_choice_display': False,  # CPUの選択メッセージ表示フラグ
    'cpu_choice_type': None,  # CPUの選択タイプ（'koikoi' または 'agari'）
    'cpu_choice_timer': 0,  # CPUメッセージ表示時間
    # 3回戦制システム用の変数を追加
    'current_round': 1,  # 現在のラウンド（1〜3）
    'total_rounds': 3,  # 総ラウンド数
    'player_total_score': 0,  # プレイヤーの総得点
    'cpu_total_score': 0,  # CPUの総得点
    'round_results': [],  # 各ラウンドの結果を保存
    'match_over': False,  # 全試合終了フラグ
    'show_round_result': False,  # ラウンド結果表示フラグ
    'round_result_timer': 0,  # ラウンド結果表示時間
    # 勝利画面用の変数を追加
    'show_victory_screen': False,  # 勝利画面表示フラグ
    'victory_winner': None,  # 勝者（'player', 'cpu', 'draw'）
    'victory_player_score': 0,  # 勝利画面用プレイヤー得点
    'victory_cpu_score': 0,  # 勝利画面用CPU得点
    'victory_yakus': [],  # 勝利画面用成立役
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

# 効果音再生関数
def play_sound_effect(sound):
    """効果音を再生する関数"""
    if sound:
        try:
            sound.play()
        except pygame.error:
            pass  # 音が再生できない場合は無視

# 効果音の読み込み
card_capture_sound = None
yaku_complete_sound = None

try:
    # カード取得時の効果音
    card_capture_sound = pygame.mixer.Sound("assets/sound/card_capture.mp3")
    card_capture_sound.set_volume(5.0)
    print("✅ カード取得効果音を読み込みました")
except:
    print("⚠️ カード取得効果音ファイルが見つかりません - 効果音なしで実行")

try:
    # 役成立時の効果音
    yaku_complete_sound = pygame.mixer.Sound("assets/sound/yaku_complete.mp3")
    yaku_complete_sound.set_volume(0.3)
    print("✅ 役成立効果音を読み込みました")
except:
    print("⚠️ 役成立効果音ファイルが見つかりません - 効果音なしで実行")

# logic.pyに効果音を設定
set_sound_effects(card_capture_sound, yaku_complete_sound)

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

    # プレイヤー選択ハイライトの描画
    from logic import is_player_selecting, draw_player_selection_highlights
    if is_player_selecting():
        draw_player_selection_highlights(screen)

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

    # ゲーム情報の表示（日本語）- 右上角に移動
    # ラウンド情報を表示
    round_info_text = f"第{game_state['current_round']}回戦 / {game_state['total_rounds']}回戦"
    round_surface = small_font.render(round_info_text, True, (255, 255, 255))
    screen.blit(round_surface, (screen_width - round_surface.get_width() - 10, 10))
    
    # 総合得点を表示
    total_score_text = f"総合得点 - プレイヤー: {game_state['player_total_score']}文, CPU: {game_state['cpu_total_score']}文"
    total_surface = small_font.render(total_score_text, True, (255, 255, 0))
    screen.blit(total_surface, (screen_width - total_surface.get_width() - 10, 35))

    # 情報表示の固定座標（取り札との重なりを避けた位置）
    info_display_x = 600  # 固定位置（十分右側に配置）

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
    
    # CPU成立役表示（最大2つまでにするならコメントアウトを外す）
    if cpu_yakus:
        # for i, yaku in enumerate(cpu_yakus[:2]):
        for i, yaku in enumerate(cpu_yakus):
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

    # ラウンド結果画面の描画
    if game_state['show_round_result']:
        draw_round_result_screen(screen, game_state, japanese_font, small_font)
        game_state['round_result_timer'] += 1

    # 勝利画面の描画
    victory_buttons = None
    if game_state['show_victory_screen']:
        victory_buttons = draw_victory_screen(screen, game_state['victory_winner'], 
                                           game_state['victory_player_score'], game_state['victory_cpu_score'], 
                                           game_state['victory_yakus'], japanese_font, small_font)

    # こいこい選択画面の描画
    koikoi_buttons = None
    if game_state['koikoi_choice']:
        koikoi_buttons = draw_koikoi_choice_screen(screen, game_state, japanese_font, small_font)

    # CPUの選択メッセージ表示
    if game_state['cpu_choice_display']:
        draw_cpu_choice_message(screen, game_state['cpu_choice_type'], japanese_font, small_font)

    # CPUターンの条件詳細チェック（デバッグ用）
    if game_state['turn'] == 'cpu':
        cpu_conditions = []
        if is_animations_active():
            cpu_conditions.append("アニメーション実行中")
        if game_state['koikoi_choice']:
            cpu_conditions.append("こいこい選択中")
        if game_state['game_over']:
            cpu_conditions.append("ゲーム終了")
        if game_state['cpu_choice_display']:
            cpu_conditions.append("CPU選択表示中")
        
        # if cpu_conditions:
        #     print(f"⚠️ CPUターン処理ブロック中: {', '.join(cpu_conditions)}")
        # else:
        #     print(f"✅ CPUターン処理条件クリア: フェーズ={game_state['cpu_action_phase']}")

    # CPUターンの処理（こいこい選択中・ゲーム終了後・CPUメッセージ表示中・プレイヤー選択中は停止）
    from logic import is_turn_blocked
    if (game_state['turn'] == 'cpu' and 
        not is_animations_active() and not game_state['koikoi_choice'] and
        not game_state['game_over'] and not game_state['cpu_choice_display'] and
        not is_turn_blocked()):  # プレイヤー選択中はCPUターンをブロック
        
        # CPUのフェーズに基づいて処理を継続（手札チェックは後で行う）
        game_state['cpu_timer'] += 1
        
        # デバッグ: CPUの状態を詳細出力
        # if game_state['cpu_timer'] % 60 == 0:  # 1秒ごとに出力
        #     print(f"🤖 CPU状態: フェーズ={game_state['cpu_action_phase']}, タイマー={game_state['cpu_timer']}, 手札={len(cpu_hand)}枚, アニメーション={is_animations_active()}")
        #     print(f"   詳細: koikoi_choice={game_state['koikoi_choice']}, game_over={game_state['game_over']}, cpu_choice_display={game_state['cpu_choice_display']}")
        #     print(f"   山札={len(yama_deck)}枚, プレイヤー手札={len(player_hand)}枚")
        
        if game_state['cpu_timer'] > 90:
            import random
            
            if game_state['cpu_action_phase'] == 'waiting':
                # waiting フェーズでのみ手札をチェック
                if len(cpu_hand) == 0:
                    print("🎴 CPU手札が空 - プレイヤーターンに切り替え")
                    game_state['turn'] = 'player'
                    game_state['cpu_timer'] = 0
                    game_state['cpu_action_phase'] = 'waiting'
                else:
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

                        if len(matching_cards) == 2:
                            # 2枚ならtype優先で高い方のみ取得
                            def card_value(card):
                                type_order = {'bright': 4, 'animal': 3, 'ribbon': 2, 'plain': 1}
                                return type_order.get(get_card_type_by_name(card.name), 0)
                            chosen_card = max(matching_cards, key=card_value)
                            field_cards.remove(chosen_card)
                            capture_cards_with_animation(cpu_card, chosen_card, cpu_captured, True, screen_height, screen_width, game_state, cpu_hand, player_captured, field_cards, len(yama_deck))
                        else:
                            # 1枚または3枚以上は従来通り全て取得
                            for matching_card in matching_cards:
                                field_cards.remove(matching_card)
                            capture_multiple_cards_with_animation(cpu_card, matching_cards, cpu_captured, True, screen_height, screen_width, game_state, cpu_hand, player_captured, field_cards, len(yama_deck))
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
                # デバッグ: draw_yamaフェーズの詳細状態
                if game_state['cpu_timer'] % 30 == 0:  # 0.5秒ごとに出力
                    print(f"🎴 draw_yamaフェーズ: タイマー={game_state['cpu_timer']}, アニメーション={is_animations_active()}, 山札={len(yama_deck)}枚")
                
                # アニメーションが完了してから山札処理を実行（少し遅延を追加）
                if not is_animations_active() and game_state['cpu_timer'] > 30:  # 0.5秒遅延
                    # 山札処理前に場札の位置を整形
                    update_field_positions(field_cards)
                    yama_drawn = draw_from_yama_deck(yama_deck, field_cards, cpu_captured, player_captured, True, screen_width, screen_height, game_state, cpu_hand, field_cards, len(yama_deck))
                    
                    # 山札が空でもターンを正常に終了
                    if not yama_drawn:
                        print("🎴 山札が空です - CPUターン終了")
                    
                    # 手札と山札が両方とも空になったらゲーム終了
                    if len(yama_deck) == 0 and len(cpu_hand) == 0 and len(player_hand) == 0:
                        print("🏁 全カードを使い切りました - ラウンド終了")
                        # 遅延処理フラグをすべてクリア
                        game_state['player_yama_pending'] = False
                        if 'player_yama_delay' in game_state:
                            del game_state['player_yama_delay']
                        if 'cpu_yama_delay' in game_state:
                            del game_state['cpu_yama_delay']
                        # 得点計算と結果保存は即座に行うが、ダイアログ表示は遅延
                        player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
                        cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
                        round_winner = "プレイヤー" if player_score > cpu_score else ("CPU" if cpu_score > player_score else "引き分け")
                        round_result = {
                            'round': game_state['current_round'],
                            'player_score': player_score,
                            'cpu_score': cpu_score,
                            'player_yakus': player_yakus,
                            'cpu_yakus': cpu_yakus,
                            'winner': round_winner
                        }
                        game_state['round_results'].append(round_result)
                        game_state['player_total_score'] += player_score
                        game_state['cpu_total_score'] += cpu_score
                        # ダイアログ表示はpendingフラグで遅延
                        # 【修正】即座にpending_round_resultを設定せず、統一判定に委ねる
                        print("⏳ 全アニメーション・カットイン完了まで結果ダイアログを延期")
                        # game_state['pending_round_result'] = True  # コメントアウト
                        game_state['round_result_timer'] = 0
                        game_state['game_over'] = True
                    else:
                        print(f"🔄 CPUターン正常終了 - プレイヤーターンに切り替え")
                        print(f"   最終状態: CPU手札={len(cpu_hand)}枚, プレイヤー手札={len(player_hand)}枚, 山札={len(yama_deck)}枚")
                        game_state['cpu_action_phase'] = 'waiting'
                        game_state['turn'] = 'player'
                        game_state['cpu_timer'] = 0

    # CPUの選択カードのハイライト表示（金色に変更）
    if game_state['turn'] == 'cpu' and game_state['cpu_action_phase'] == 'card_selected' and 'selected_cpu_card' in game_state:
        cpu_card = game_state['selected_cpu_card']
        pygame.draw.rect(screen, (255, 215, 0),  # 修正: 赤色(255, 0, 0)→金色(255, 215, 0)
                       (cpu_card.x-2, cpu_card.y-2, cpu_card.get_image().get_width()+4, cpu_card.get_image().get_height()+4), 3)
    
    # イベント処理
    # pending_round_resultがTrueなら、アニメーション終了後にラウンド結果ダイアログを表示
    if game_state.get('pending_round_result', False) and not is_animations_active():
        if len(player_hand) == 0 and len(cpu_hand) == 0:
            game_state['show_round_result'] = True
            game_state['pending_round_result'] = False
            print("🎬 アニメーション完了後にラウンド結果ダイアログ表示")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # CPU選択メッセージのクリック処理
            if game_state['cpu_choice_display']:
                print("🖱️ CPU選択メッセージをクリックで消去")
                game_state['cpu_choice_display'] = False
                game_state['cpu_choice_type'] = None
                continue  # 他のダイアログ消去処理はスキップ
            
            # プレイヤーの手動選択処理
            from logic import is_player_selecting, handle_player_card_selection
            if is_player_selecting():
                if handle_player_card_selection(event.pos):
                    print("✅ プレイヤーカード選択完了")
                continue  # 他の処理はスキップ
            
            mx, my = event.pos
            # 勝利画面のクリック処理
            if game_state['show_victory_screen'] and victory_buttons:
                # もう一度遊ぶボタン
                if 'play_again_button' in victory_buttons:
                    play_again_x, play_again_y, play_again_w, play_again_h = victory_buttons['play_again_button']
                    if (play_again_x <= mx <= play_again_x + play_again_w and 
                        play_again_y <= my <= play_again_y + play_again_h):
                        print("🔄 もう一度遊ぶ")
                        # ゲーム状態を完全リセット
                        print("💫 新しいゲーム開始 - 完全初期化")
                        
                        # 基本ゲーム状態のリセット
                        game_state['current_round'] = 1
                        game_state['player_total_score'] = 0
                        game_state['cpu_total_score'] = 0
                        game_state['round_results'] = []
                        game_state['match_over'] = False
                        game_state['show_victory_screen'] = False
                        game_state['victory_winner'] = None
                        game_state['victory_player_score'] = 0
                        game_state['victory_cpu_score'] = 0
                        game_state['victory_yakus'] = []
                        
                        # すべてのゲーム状態フラグをリセット
                        game_state['game_over'] = False
                        game_state['koikoi_choice'] = False
                        game_state['pending_koikoi_choice'] = False
                        game_state['koikoi_player'] = None
                        game_state['current_round_score'] = 0
                        game_state['current_yakus'] = []
                        game_state['cpu_choice_display'] = False
                        game_state['cpu_choice_type'] = None
                        game_state['cpu_choice_timer'] = 0
                        game_state['show_round_result'] = False
                        game_state['round_result_timer'] = 0
                        game_state['selected_card'] = None
                        game_state['cpu_timer'] = 0
                        game_state['cpu_action_phase'] = 'waiting'
                        game_state['player_yama_pending'] = False
                        
                        # 遅延処理や一時的なフラグをクリア
                        for key in list(game_state.keys()):
                            if key in ['player_yama_delay', 'cpu_yama_delay', 'winner', 
                                     'final_score_cpu', 'final_yakus_cpu', 'result_text',
                                     'pending_cpu_choice', 'cpu_choice', 'cpu_score', 'cpu_yakus']:
                                del game_state[key]
                        
                        # カードとアニメーションの完全リセット（先行プレイヤーも自動決定）
                        reset_for_next_round(game_state)
                
                # 終了ボタン
                if 'quit_button' in victory_buttons:
                    quit_x, quit_y, quit_w, quit_h = victory_buttons['quit_button']
                    if (quit_x <= mx <= quit_x + quit_w and 
                        quit_y <= my <= quit_y + quit_h):
                        print("🎮 ゲーム終了")
                        run = False
                    
            # こいこい選択の処理
            elif game_state['koikoi_choice'] and koikoi_buttons:
                agari_x, agari_y, agari_w, agari_h = koikoi_buttons['agari_button']
                koikoi_x, koikoi_y, koikoi_w, koikoi_h = koikoi_buttons['koikoi_button']
                
                if (agari_x <= mx <= agari_x + agari_w and 
                    agari_y <= my <= agari_y + agari_h):
                    # 上がりを選択 - ラウンド終了処理
                    print("🎯 プレイヤーが上がりを選択！")
                    game_state['koikoi_choice'] = False
                    
                    # 遅延処理フラグをすべてクリア
                    game_state['player_yama_pending'] = False
                    if 'player_yama_delay' in game_state:
                        del game_state['player_yama_delay']
                    if 'cpu_yama_delay' in game_state:
                        del game_state['cpu_yama_delay']
                    
                    # 現在の得点を取得
                    player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
                    cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
                    
                    # 新しい得点計算ロジックを適用
                    if player_score > cpu_score:
                        # プレイヤーの勝利
                        final_player_score, final_cpu_score = calculate_final_scores(
                            game_state, 'player', 'cpu', player_score, player_yakus, cpu_score, cpu_yakus
                        )
                        round_winner = "プレイヤー"
                    elif cpu_score > player_score:
                        # CPUの勝利
                        final_player_score, final_cpu_score = calculate_final_scores(
                            game_state, 'cpu', 'player', cpu_score, cpu_yakus, player_score, player_yakus
                        )
                        round_winner = "CPU"
                    else:
                        # 引き分け
                        final_player_score, final_cpu_score = player_score, cpu_score
                        round_winner = "引き分け"
                    
                    # ラウンド結果を記録
                    round_result = {
                        'round': game_state['current_round'],
                        'player_score': final_player_score,
                        'cpu_score': final_cpu_score,
                        'player_yakus': player_yakus,
                        'cpu_yakus': cpu_yakus,
                        'winner': round_winner
                    }
                    game_state['round_results'].append(round_result)
                    
                    # 総得点に加算
                    game_state['player_total_score'] += final_player_score
                    game_state['cpu_total_score'] += final_cpu_score
                    
                    # ラウンド結果画面を表示
                    game_state['show_round_result'] = True
                    game_state['round_result_timer'] = 0
                    game_state['game_over'] = True
                    
                elif (koikoi_x <= mx <= koikoi_x + koikoi_w and 
                      koikoi_y <= my <= koikoi_y + koikoi_h):
                    # こいこいを選択
                    print("🔥 プレイヤーがこいこいを選択！")
                    game_state['koikoi_choice'] = False
                    game_state['koikoi_was_declared'] = True  # こいこい宣言フラグ
                    game_state['koikoi_declarer'] = 'player'  # 宣言者を記録
                    # ゲーム続行
                    
            # ラウンド結果画面のクリック処理
            elif game_state['show_round_result']:
                # ラウンド結果画面（勝者問わず）をクリックで閉じる
                if game_state['current_round'] < game_state['total_rounds']:
                    game_state['current_round'] += 1
                    game_state['show_round_result'] = False
                    reset_for_next_round(game_state)
                else:
                    game_state['match_over'] = True
                    game_state['show_round_result'] = False
                    # 最終結果を設定
                    if game_state['player_total_score'] > game_state['cpu_total_score']:
                        game_state['victory_winner'] = 'player'
                        print("\n🎊 プレイヤーの総合勝利！ 🎊")
                    elif game_state['cpu_total_score'] > game_state['player_total_score']:
                        game_state['victory_winner'] = 'cpu'
                        print("\n💻 CPUの総合勝利！ 💻")
                    else:
                        game_state['victory_winner'] = 'draw'
                        print("\n🤝 総合引き分け！ 🤝")
                    
                    # 勝利画面用の情報を保存
                    game_state['victory_player_score'] = game_state['player_total_score']
                    game_state['victory_cpu_score'] = game_state['cpu_total_score']
                    game_state['victory_yakus'] = game_state.get('current_yakus', [])
                    game_state['show_victory_screen'] = True
                    
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

                                if len(matching_cards) == 2:
                                    # 2枚ならどちらかをクリックで選択
                                    for matching_card in matching_cards:
                                        card_width = matching_card.get_image().get_width()
                                        card_height = matching_card.get_image().get_height()
                                        if matching_card.x <= mx <= matching_card.x + card_width and matching_card.y <= my <= matching_card.y + card_height:
                                            field_cards.remove(matching_card)
                                            capture_cards_with_animation(selected_card, matching_card, player_captured, False, screen_height, screen_width, game_state, cpu_hand, player_captured, field_cards, len(yama_deck))
                                            break
                                    # どちらも選ばれていなければ何もしない
                                else:
                                    # 1枚または3枚以上は従来通り全て取得
                                    for matching_card in matching_cards:
                                        field_cards.remove(matching_card)
                                    capture_multiple_cards_with_animation(selected_card, matching_cards, player_captured, False, screen_height, screen_width, game_state, cpu_hand, player_captured, field_cards, len(yama_deck))
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
            else:
                # プレイヤーの操作がブロックされている理由をデバッグ
                if game_state['turn'] == 'player':
                    blocked_reasons = []
                    if is_animations_active():
                        blocked_reasons.append("アニメーション実行中")
                    if game_state['koikoi_choice']:
                        blocked_reasons.append("こいこい選択中")
                    if game_state['game_over']:
                        blocked_reasons.append("ゲーム終了")
                    if blocked_reasons:
                        print(f"🚫 プレイヤー操作ブロック中: {', '.join(blocked_reasons)}")
                elif game_state['turn'] == 'cpu':
                    # CPUターンが続いている理由をデバッグ
                    blocked_reasons = []
                    if len(cpu_hand) == 0:
                        blocked_reasons.append(f"CPU手札空（{len(cpu_hand)}枚）")
                    if is_animations_active():
                        blocked_reasons.append("アニメーション実行中")
                    if game_state['koikoi_choice']:
                        blocked_reasons.append("こいこい選択中")
                    if game_state['game_over']:
                        blocked_reasons.append("ゲーム終了")
                    if game_state['cpu_choice_display']:
                        blocked_reasons.append("CPU選択表示中")
                    
                    if blocked_reasons:
                        print(f"⏳ CPUのターン中（ブロック理由: {', '.join(blocked_reasons)}）")
                    else:
                        print(f"⏳ CPUのターン中（フェーズ: {game_state['cpu_action_phase']}, タイマー: {game_state['cpu_timer']}）")
                else:
                    print(f"❓ 不明な状態: turn={game_state['turn']}")
    
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
            yama_drawn = draw_from_yama_deck(yama_deck, field_cards, cpu_captured, player_captured, False, screen_width, screen_height, game_state, cpu_hand, field_cards, len(yama_deck))
            
            # 山札が空でもターンを正常に終了
            if not yama_drawn:
                print("🎴 山札が空です - プレイヤーターン終了")
            
            game_state['player_yama_pending'] = False
            if 'player_yama_delay' in game_state:
                del game_state['player_yama_delay']  # 遅延カウンタを削除
            
            # 【修正】プレイヤーの山札処理完了後、CPUターンに切り替え
            game_state['turn'] = 'cpu'
            game_state['cpu_timer'] = 0
            game_state['cpu_action_phase'] = 'waiting'
            print("🔄 プレイヤー山札処理完了 - CPUターンに切り替え")
            print(f"   状態: プレイヤー手札={len(player_hand)}枚, CPU手札={len(cpu_hand)}枚, 山札={len(yama_deck)}枚")
            
            # 手札と山札が両方とも空になったらゲーム終了
            if len(yama_deck) == 0 and len(cpu_hand) == 0 and len(player_hand) == 0:
                print("🏁 全カードを使い切りました - ラウンド終了")
                
                # 遅延処理フラグをすべてクリア
                game_state['player_yama_pending'] = False
                if 'player_yama_delay' in game_state:
                    del game_state['player_yama_delay']
                if 'cpu_yama_delay' in game_state:
                    del game_state['cpu_yama_delay']
                
                # 現在の得点を取得
                player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
                cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
                
                # ラウンド結果を記録
                round_winner = "プレイヤー" if player_score > cpu_score else ("CPU" if cpu_score > player_score else "引き分け")
                
                round_result = {
                    'round': game_state['current_round'],
                    'player_score': player_score,
                    'cpu_score': cpu_score,
                    'player_yakus': player_yakus,
                    'cpu_yakus': cpu_yakus,
                    'winner': round_winner
                }
                game_state['round_results'].append(round_result)
                
                # 総得点に加算
                game_state['player_total_score'] += player_score
                game_state['cpu_total_score'] += cpu_score
                
                # ラウンド結果画面を表示
                # 【修正】即座にshow_round_resultを設定せず、統一判定に委ねる
                print("⏳ 全アニメーション・カットイン完了まで結果ダイアログを延期")
                # game_state['show_round_result'] = True  # コメントアウト
                game_state['round_result_timer'] = 0
                game_state['game_over'] = True
            else:
                print(f"🔄 プレイヤー山札処理完了 - CPUターンに切り替え")
                print(f"   状態: プレイヤー手札={len(player_hand)}枚, CPU手札={len(cpu_hand)}枚, 山札={len(yama_deck)}枚")
                game_state['turn'] = 'cpu'
                game_state['cpu_timer'] = 0
    
    # CPUが役で勝利した場合の処理（3回戦制対応）
    if (game_state['game_over'] and game_state.get('winner') == 'cpu' and 
        'result_text' not in game_state and not game_state['show_round_result']):
        # CPUの役による勝利 - ラウンド終了処理
        cpu_score = game_state.get('final_score_cpu', 0)
        cpu_yakus = game_state.get('final_yakus_cpu', [])
        player_score, player_yakus = calculate_score(player_captured, screen_width, screen_height)
        
        print(f"\n=== CPU役による勝利 ===")
        print(f"CPU最終得点: {cpu_score}文")
        if cpu_yakus:
            print("CPUの成立役:")
            for yaku in cpu_yakus:
                print(f"  • {yaku}")
        
        # ラウンド結果を記録
        round_winner = "CPU"  # CPUが役で勝利
        
        # 正しい得点計算を実行
        if cpu_score > player_score:
            # calculate_final_scoresの返り値は (player_score, cpu_score) の順なので、値を入れ替える
            tmp_player_score, tmp_cpu_score = calculate_final_scores(
                game_state, 'cpu', 'player', cpu_score, cpu_yakus, player_score, player_yakus
            )
            final_player_score = tmp_cpu_score
            final_cpu_score = tmp_player_score      #意味不明。CPUが勝ったのに逆になるから無理やりこうした
        elif player_score > cpu_score:
            final_player_score, final_cpu_score = calculate_final_scores(
                game_state, 'player', 'cpu', player_score, player_yakus, cpu_score, cpu_yakus
            )
            round_winner = "プレイヤー"  # プレイヤーの勝利
        else:
            final_player_score, final_cpu_score = calculate_final_scores(
                game_state, 'cpu', 'player', cpu_score, cpu_yakus, player_score, player_yakus
            )
            round_winner = "引き分け"
        
        round_result = {
            'round': game_state['current_round'],
            'player_score': final_player_score,
            'cpu_score': final_cpu_score,
            'player_yakus': player_yakus,
            'cpu_yakus': cpu_yakus,
            'winner': round_winner
        }
        game_state['round_results'].append(round_result)
        
        # 総得点に加算
        print(f"📊 CPU役勝利 総得点更新: P{game_state['player_total_score']}+{final_player_score} C{game_state['cpu_total_score']}+{final_cpu_score}")
        game_state['player_total_score'] += final_player_score
        game_state['cpu_total_score'] += final_cpu_score
        
        print(f"\n=== 第{game_state['current_round']}回戦結果（CPU役勝利） ===")
        print(f"プレイヤー: {player_score}文")
        print(f"CPU: {cpu_score}文")
        print(f"勝者: {round_winner}")
        print(f"総合得点 - プレイヤー: {game_state['player_total_score']}文, CPU: {game_state['cpu_total_score']}文")
        
        # ラウンド結果画面を表示
        game_state['show_round_result'] = True
        game_state['round_result_timer'] = 0
        # game_stateのwinnerフラグをクリア
        if 'winner' in game_state:
            del game_state['winner']
        if 'final_score_cpu' in game_state:
            del game_state['final_score_cpu']
        if 'final_yakus_cpu' in game_state:
            del game_state['final_yakus_cpu']
        
        print("\n💻 CPUの役による勝利！ 💻")
    
    
    # 手札が0枚になった瞬間はpending_round_resultフラグを立てるだけ
    # 【修正】全ての処理が完了してからダイアログを表示するように条件を厳格化
    if (not game_state['game_over'] and 
        ((len(player_hand) == 0 and len(cpu_hand) == 0) or game_state.get('cpu_agari', False)) and
        not game_state.get('pending_round_result', False) and
        not game_state['koikoi_choice'] and
        not game_state.get('player_yama_pending', False) and  # プレイヤー山札処理完了まで待機
        not is_animations_active() and                        # 全アニメーション完了まで待機
        not active_cutin_animations and                       # カットインアニメーション完了まで待機
        len(cutin_queue) == 0):                              # カットインキュー空まで待機
        game_state['pending_round_result'] = True
        print("🏁 全処理完了 - ラウンド結果ダイアログ準備完了")

    # pending_round_resultがTrueかつ全ての処理が終わったらラウンド終了処理
    if (game_state.get('pending_round_result', False)
        and not is_animations_active()
        and not game_state['game_over']
        and not game_state['koikoi_choice']
        and not game_state.get('player_yama_pending', False)  # 追加：プレイヤー山札処理完了確認
        and len(active_cutin_animations) == 0                 # 追加：カットイン完了確認
        and len(cutin_queue) == 0):                          # 追加：カットインキュー空確認
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
        # ...existing code...
        game_state['pending_round_result'] = False
        cpu_score, cpu_yakus = calculate_score(cpu_captured, screen_width, screen_height)
        print(f"CPU合計得点: {cpu_score}文")
        if cpu_yakus:
            print("成立した役:")
            for yaku in cpu_yakus:
                print(f"  • {yaku}")
        else:
            print("役なし")
        
        # CPU上がりの場合のみ得点を加算
        if game_state.get('cpu_agari', False):
            print("🤖 CPU上がり検出→得点計算開始")
            # CPU上がりの場合の得点計算
            if cpu_score > player_score:
                # CPUの勝利
                final_player_score, final_cpu_score = calculate_final_scores(
                    game_state, 'cpu', 'player', cpu_score, cpu_yakus, player_score, player_yakus
                )
                round_winner = "CPU"
            elif player_score > cpu_score:
                # プレイヤーの勝利
                final_player_score, final_cpu_score = calculate_final_scores(
                    game_state, 'player', 'cpu', player_score, player_yakus, cpu_score, cpu_yakus
                )
                round_winner = "プレイヤー"
            else:
                # 引き分け
                final_player_score, final_cpu_score = calculate_final_scores(
                    game_state, 'player', 'cpu', player_score, player_yakus, cpu_score, cpu_yakus
                )
                round_winner = "引き分け"
            
            # 総得点に加算
            print(f"📊 総得点更新: P{game_state['player_total_score']}+{final_player_score} C{game_state['cpu_total_score']}+{final_cpu_score}")
            game_state['player_total_score'] += final_player_score
            game_state['cpu_total_score'] += final_cpu_score
            
            print(f"🏆 第{game_state['current_round']}回戦: {round_winner}勝利")
            print(f"📈 新総合得点: P{game_state['player_total_score']} - C{game_state['cpu_total_score']}")
            
            # デバッグ: 最重要情報のみ表示
            print(f"*** 得点加算確認 ***")
            print(f"CPU得点: {cpu_score} → 最終{final_cpu_score}")
            print(f"プレイヤー得点: {player_score} → 最終{final_player_score}")
            print(f"総合得点: CPU={game_state['cpu_total_score']}, プレイヤー={game_state['player_total_score']}")
            print(f"*** ここまで ***")
            
            print(f"\n=== 第{game_state['current_round']}回戦結果 ===")
            print(f"プレイヤー: {final_player_score}文（元得点: {player_score}文）")
            print(f"CPU: {final_cpu_score}文（元得点: {cpu_score}文）")
            print(f"勝者: {round_winner}")
            print(f"総合得点 - プレイヤー: {game_state['player_total_score']}文, CPU: {game_state['cpu_total_score']}文")
        else:
            # カード終了による自動終了の場合は得点加算なし
            print("\n🎴 全てのカードが場に出ました")
            print("💭 誰も「上がり」を選択しなかったため、このラウンドは得点なしです")
            final_player_score = 0
            final_cpu_score = 0
            round_winner = "得点なし"
            
            print(f"\n=== 第{game_state['current_round']}回戦結果 ===")
            print(f"プレイヤー: 0文（役得点: {player_score}文だが加算されず）")
            print(f"CPU: 0文（役得点: {cpu_score}文だが加算されず）")
            print(f"勝者: {round_winner}")
            print(f"総合得点 - プレイヤー: {game_state['player_total_score']}文, CPU: {game_state['cpu_total_score']}文")
        
        # ラウンド結果を保存
        round_result = {
            'round': game_state['current_round'],
            'player_score': final_player_score,
            'cpu_score': final_cpu_score,
            'player_yakus': player_yakus,
            'cpu_yakus': cpu_yakus,
            'winner': round_winner
        }
        game_state['round_results'].append(round_result)
        
        # ラウンド結果画面を表示
        game_state['show_round_result'] = True
        game_state['round_result_timer'] = 0
        game_state['game_over'] = True  # 一時的にゲームを停止

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()