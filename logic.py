from animation import CardAnimation, CardOverlayDisplay, YamaCardHighlight, CapturedCardHighlight, CardMergeAnimation, YakuCutInAnimation  # アニメーション関連クラスをインポート（カットインクラスを追加）

# グローバル変数（アニメーション管理）
active_animations = []  # アクティブなアニメーションのリスト
active_overlays = []  # アクティブなオーバーレイ表示のリスト
active_yama_highlights = []  # アクティブな山札ハイライトのリスト
active_captured_highlights = []  # 新規追加: アクティブな取り札ハイライトのリスト
active_merge_animations = []  # 新規追加: アクティブな重なり合いアニメーションのリスト
active_cutin_animations = []  # 新規追加: アクティブなカットインアニメーションのリスト

# 役状態管理
previous_player_yakus = []  # プレイヤーの前回の役リスト（新しい役のみカットイン表示するため）

def update_hand_positions(hand_cards, base_x, base_y, spacing=120):
    """手札の位置を更新する関数（チート機能で手札が変更された時用）
    Args:
        hand_cards: 手札カードのリスト
        base_x: 基準x座標
        base_y: 基準y座標
        spacing: カード間隔
    """
    for i, card in enumerate(hand_cards):
        card.x = base_x + i * spacing
        card.y = base_y

def create_yaku_cutin(yaku_name, screen_width, screen_height):
    """役カットインアニメーション作成関数
    Args:
        yaku_name: 役の名前
        screen_width: 画面幅
        screen_height: 画面高さ
    """
    global active_cutin_animations
    cutin = YakuCutInAnimation(yaku_name, screen_width, screen_height)
    active_cutin_animations.append(cutin)
    print(f"🎉 カットイン作成: {yaku_name} (アクティブ数: {len(active_cutin_animations)})")
    print(f"   画面サイズ: {screen_width}x{screen_height}")
    print(f"   アニメーション状態: アクティブ={cutin.is_active}, 期間={cutin.duration}フレーム")

def calculate_score(captured_cards, screen_width=800, screen_height=600):
    """花札の役計算関数（カットイン機能付き）
    Args:
        captured_cards: 取得したカードのリスト
        screen_width: 画面幅（カットイン用）
        screen_height: 画面高さ（カットイン用）
    Returns:
        tuple: (合計得点, 成立した役のリスト)
    """
    score = 0
    achieved_yakus = []  # 成立した役のリスト
    
    # カードを分類
    bright_cards = [card for card in captured_cards if card.type == "bright"]
    tane_cards = [card for card in captured_cards if card.type == "tane"]
    ribbon_cards = [card for card in captured_cards if "ribbon" in card.type or card.type == "tan"]
    plain_cards = [card for card in captured_cards if card.type == "plain"]
    
    # 光札の役判定
    if len(bright_cards) == 5:
        score += 10  # 五光
        achieved_yakus.append("五光 (10文)")
        print("【役成立】五光 - 10文")
        print("五光: 10文")
    elif len(bright_cards) == 4:
        # 雨四光か四光かを判定（雨は11月の柳の光札）
        rain_card = any(card.month == 11 and card.type == "bright" for card in bright_cards)
        if rain_card:
            score += 7  # 雨四光
            achieved_yakus.append("雨四光 (7文)")
            print("【役成立】雨四光 - 7文")
            print("雨四光: 7文")
        else:
            score += 8  # 四光
            achieved_yakus.append("四光 (8文)")
            print("【役成立】四光 - 8文")
            print("四光: 8文")
    elif len(bright_cards) == 3:
        # 雨を含まない三光
        rain_card = any(card.month == 11 and card.type == "bright" for card in bright_cards)
        if not rain_card:
            score += 5  # 三光
            achieved_yakus.append("三光 (5文)")
            print("【役成立】三光 - 5文")
            print("三光: 5文")
    
    # 種札の役判定
    # 猪鹿蝶（7月の猪、10月の鹿、6月の蝶）
    boar = any(card.month == 7 and card.name == "boar" for card in tane_cards)
    deer = any(card.month == 10 and card.name == "maple_deer" for card in tane_cards)
    butterfly = any(card.month == 6 and card.name == "peony_butterfly" for card in tane_cards)
    if boar and deer and butterfly:
        score += 5  # 猪鹿蝶
        achieved_yakus.append("猪鹿蝶 (5文)")
        print("【役成立】猪鹿蝶 - 5文")
        print("猪鹿蝶: 5文")
    
    # 花見酒（3月の桜幕と9月の菊盃）
    cherry_curtain = any(card.month == 3 and card.name == "cherry_curtain" for card in bright_cards)
    sake_cup = any(card.month == 9 and card.name == "chrysanthemum_sake_cup" for card in tane_cards)
    if cherry_curtain and sake_cup:
        score += 5  # 花見酒
        achieved_yakus.append("花見酒 (5文)")
        print("【役成立】花見酒 - 5文")
        print("花見酒: 5文")
    
    # 月見酒（8月の月と9月の菊盃）
    full_moon = any(card.month == 8 and card.name == "full_moon_pampas" for card in bright_cards)
    if full_moon and sake_cup:
        score += 5  # 月見酒
        achieved_yakus.append("月見酒 (5文)")
        print("【役成立】月見酒 - 5文")
        print("月見酒: 5文")
    
    # 短冊札の役判定
    red_ribbons = [card for card in ribbon_cards if card.type == "red_ribbon"]
    blue_ribbons = [card for card in ribbon_cards if card.type == "blue_ribbon"]
    
    # 赤短（松・梅・桜の赤短冊）
    red_ribbon_months = [card.month for card in red_ribbons]
    if 1 in red_ribbon_months and 2 in red_ribbon_months and 3 in red_ribbon_months:
        score += 5  # 赤短
        achieved_yakus.append("赤短 (5文)")
        print("【役成立】赤短 - 5文")
        print("赤短: 5文")
    
    # 青短（牡丹・菊・紅葉の青短冊）
    blue_ribbon_months = [card.month for card in blue_ribbons]
    if 6 in blue_ribbon_months and 9 in blue_ribbon_months and 10 in blue_ribbon_months:
        score += 5  # 青短
        achieved_yakus.append("青短 (5文)")
        print("【役成立】青短 - 5文")
        print("青短: 5文")
    
    # 数の役
    # 短（短冊札5枚以上）
    if len(ribbon_cards) >= 5:
        points = len(ribbon_cards) - 4  # 5枚目から1枚1文
        score += points
        achieved_yakus.append(f"短 ({points}文)")
        print(f"短: {points}文")
    
    # 種（種札5枚以上）
    if len(tane_cards) >= 5:
        points = len(tane_cards) - 4  # 5枚目から1枚1文
        score += points
        achieved_yakus.append(f"種 ({points}文)")
        print(f"種: {points}文")
    
    # カス（カス札10枚以上）
    if len(plain_cards) >= 10:
        points = len(plain_cards) - 9  # 10枚目から1枚1文
        score += points
        achieved_yakus.append(f"カス ({points}文)")
        print(f"カス: {points}文")
    
    return score, achieved_yakus

def sort_captured_cards_by_type(captured_cards):
    """取り札を属性別に分類する関数
    Args:
        captured_cards: 取得したカードのリスト
    Returns:
        tuple: (光札, 種札, 短冊札, カス札) のタプル
    """
    bright_cards = []  # 光札（20点）のリスト
    tane_cards = []  # 種札（10点）のリスト
    ribbon_cards = []  # 短冊札（5点）のリスト
    plain_cards = []  # カス札（1点）のリスト
    
    for card in captured_cards:  # 各取得カードについて
        if card.type == "bright":  # 光札の場合
            bright_cards.append(card)  # 光札リストに追加
        elif card.type == "tane":  # 種札の場合
            tane_cards.append(card)  # 種札リストに追加
        elif "ribbon" in card.type or card.type == "tan":  # 短冊札の場合
            ribbon_cards.append(card)  # 短冊札リストに追加
        elif card.type == "plain":  # カス札の場合
            plain_cards.append(card)  # カス札リストに追加
    
    return bright_cards, tane_cards, ribbon_cards, plain_cards  # 分類済みのリストを返す

def draw_sorted_captured_cards(screen, captured_cards, start_x, start_y):
    """属性別に整理して取り札を描画する関数（アニメーション中カード対応）
    Args:
        screen: 描画先の画面
        captured_cards: 取得したカードのリスト
        start_x: 描画開始のx座標
        start_y: 描画開始のy座標
    """
    # アニメーション中のカードをチェックする関数
    def is_card_in_animation(card):
        # 重なり合いアニメーション中かチェック
        for merge_anim in active_merge_animations:
            if card == merge_anim.hand_card or card == merge_anim.field_card:
                return True
        # 通常のアニメーション中かチェック
        for anim in active_animations:
            if card == anim.card:
                return True
        return False
    
    # カードを属性別に分類
    bright_cards, tane_cards, ribbon_cards, plain_cards = sort_captured_cards_by_type(captured_cards)
    
    current_x = start_x  # 現在の描画x座標
    card_spacing = 35  # カード間のスペース
    
    # Bright属性（左端）
    for i, card in enumerate(bright_cards):  # 各光札について
        if not is_card_in_animation(card):  # アニメーション中でない場合のみ座標変更
            card.x = current_x + i * card_spacing  # x座標を設定
            card.y = start_y  # y座標を設定
            card.is_face_up = True  # カードを表向きに
            card.update_and_draw(screen)  # カードを描画
    
    if bright_cards:  # 光札が存在する場合
        current_x += len(bright_cards) * card_spacing + 15  # 次の描画位置を更新
    
    # Tane属性
    for i, card in enumerate(tane_cards):  # 各種札について
        if not is_card_in_animation(card):  # アニメーション中でない場合のみ座標変更
            card.x = current_x + i * card_spacing  # x座標を設定
            card.y = start_y  # y座標を設定
            card.is_face_up = True  # カードを表向きに
            card.update_and_draw(screen)  # カードを描画
    
    if tane_cards:  # 種札が存在する場合
        current_x += len(tane_cards) * card_spacing + 15  # 次の描画位置を更新
    
    # Ribbon属性
    for i, card in enumerate(ribbon_cards):  # 各短冊札について
        if not is_card_in_animation(card):  # アニメーション中でない場合のみ座標変更
            card.x = current_x + i * card_spacing  # x座標を設定
            card.y = start_y  # y座標を設定
            card.is_face_up = True  # カードを表向きに
            card.update_and_draw(screen)  # カードを描画
    
    if ribbon_cards:  # 短冊札が存在する場合
        current_x += len(ribbon_cards) * card_spacing + 15  # 次の描画位置を更新
    
    # Plain属性（右端）
    for i, card in enumerate(plain_cards):  # 各カス札について
        if not is_card_in_animation(card):  # アニメーション中でない場合のみ座標変更
            card.x = current_x + i * card_spacing  # x座標を設定
            card.y = start_y  # y座標を設定
            card.is_face_up = True  # カードを表向きに
            card.update_and_draw(screen)  # カードを描画

def get_captured_card_position(captured_list, is_cpu=True, screen_height=800):
    """取り札エリアでの次のカード位置を計算する関数
    Args:
        captured_list: 取得済みカードのリスト
        is_cpu: CPUの取り札かどうか
        screen_height: 画面の高さ
    Returns:
        tuple: (x座標, y座標) のタプル
    """
    if is_cpu:  # CPUの取り札の場合
        base_y = 10  # 画面上部
    else:  # プレイヤーの取り札の場合
        base_y = screen_height - 100  # 画面下部
    
    # 現在の取り札数に基づいて位置を計算
    card_count = len(captured_list)  # 取得済みカード数
    return 50 + (card_count % 20) * 35, base_y  # x座標（20枚で折り返し）とy座標を返す

def capture_cards_with_animation(hand_card, field_card, captured_list, is_cpu=True, screen_height=800, screen_width=1200):
    """アニメーション付きでカードを取得する関数（カットイン対応版）"""
    global active_merge_animations, active_captured_highlights, active_cutin_animations, active_animations, previous_player_yakus  # グローバル変数を使用
    
    # 取得先の位置を計算
    end_x, end_y = get_captured_card_position(captured_list, is_cpu, screen_height)
    
    # カードを取り札リストに追加（すぐに追加してスコア計算を行う）
    captured_list.append(hand_card)
    captured_list.append(field_card)
    
    hand_card.is_face_up = True
    field_card.is_face_up = True
    
    # カード追加直後にスコア計算してカットインをチェック
    cutin_triggered = False
    if not is_cpu:  # プレイヤーの場合のみカットインを表示
        score, achieved_yakus = calculate_score(captured_list, screen_width, screen_height)
        print(f"💯 現在のスコア: {score}文, 成立役: {achieved_yakus}")
        
        # 新しく成立した役のみを特定
        new_yakus = [yaku for yaku in achieved_yakus if yaku not in previous_player_yakus]
        
        # 新しく役が成立した場合、カットインを表示
        if new_yakus:
            for yaku in new_yakus:
                print(f"🎊 新しい役成立でカットイン発生: {yaku}")
                cutin_triggered = True
                # すべてのアニメーションを停止
                active_animations.clear()
                active_merge_animations.clear()
                active_captured_highlights.clear()
                # カットインアニメーションを作成（最初の新しい役のみ）
                cutin_animation = YakuCutInAnimation(yaku, screen_width, screen_height)
                active_cutin_animations.append(cutin_animation)
                break  # 複数の新しい役がある場合は最初の1つのみ表示
        
        # プレイヤーの役状態を更新
        previous_player_yakus = achieved_yakus.copy()
    
    # カットインが発生した場合はアニメーションを作成しない
    if not cutin_triggered:
        # 新しい重なり合いアニメーションを作成（2秒間、2倍速）
        merge_anim = CardMergeAnimation(hand_card, field_card, end_x, end_y, 120)  # 2秒間のアニメーション（2倍速）
        active_merge_animations.append(merge_anim)
        
        # デバッグ出力
        print(f"重なり合いアニメーション作成: {hand_card.name} + {field_card.name}")
        print(f"アニメーション設定: 期間={merge_anim.duration}フレーム, フェーズ1={merge_anim.phase1_duration}, フェーズ2={merge_anim.phase2_duration}, フェーズ3={merge_anim.phase3_duration}")
        print(f"初期位置 -> 手札({merge_anim.hand_start_x}, {merge_anim.hand_start_y}), 場札({merge_anim.field_start_x}, {merge_anim.field_start_y})")
        print(f"目標位置 -> ({end_x}, {end_y})")
        print(f"アクティブなアニメーション数: {len(active_merge_animations)}")
        
        # 取得した2枚のカードを取り札エリアでハイライト
        captured_cards_to_highlight = [hand_card, field_card]  # 取得した2枚のカードをハイライト対象に
        
        # アニメーション完了後にハイライトを開始
        highlight = CapturedCardHighlight(captured_cards_to_highlight, 30)  # 0.5秒間ハイライト（2倍速）
        highlight.delay_frames = 105  # 重なり合いアニメーション完了後（1.75秒後、2倍速）
        highlight.delay_count = 0
        active_captured_highlights.append(highlight)  # アクティブなハイライトリストに追加
    else:
        # カットイン発生時はカードを最終位置に直接配置
        hand_card.x = end_x
        hand_card.y = end_y
        field_card.x = end_x
        field_card.y = end_y
        print(f"🎊 カットイン発生により、カードを直接配置: ({end_x}, {end_y})")

def draw_from_yama_deck(yama_deck, field_cards, cpu_captured, player_captured, is_cpu=False, screen_width=1200, screen_height=800):
    """山札からカードを引く処理関数（スライドアニメーション版）
    Args:
        yama_deck: 山札のリスト
        field_cards: 場札のリスト
        cpu_captured: CPUの取り札リスト
        player_captured: プレイヤーの取り札リスト
        is_cpu: CPUのターンかどうか
        screen_width: 画面の幅
        screen_height: 画面の高さ
    """
    global active_animations, active_yama_highlights, active_captured_highlights  # グローバル変数を使用（新しい変数を追加）
    
    if len(yama_deck) > 0:  # 山札にカードが残っている場合
        drawn_card = yama_deck.pop(0)  # 山札の先頭からカードを引く
        print(f"{'CPU' if is_cpu else 'Player'}: 山札から {drawn_card.name} を引きました")  # デバッグ出力
        
        # 山札の位置を保存（スライドアニメーション用）
        yama_x = screen_width - 400  # 山札のx座標（main.pyと同じ）
        yama_y = 100 + 150  # 山札のy座標（VERTICAL_SPACING=150）
        drawn_card.x = yama_x  # 山札位置からスタート
        drawn_card.y = yama_y
        drawn_card.is_face_up = True  # カードを表向きに
        
        # 場札に追加して目標位置を計算
        field_cards.append(drawn_card)  # 場札に追加
        target_index = len(field_cards) - 1  # 新しいカードのインデックス
        target_x = 80 + target_index * 70  # 場札エリアの目標x座標
        target_y = 100 + 150  # 場札エリアの目標y座標（VERTICAL_SPACING=150）
        
        # 山札から場札エリアへのスライドアニメーション（45フレーム、0.75秒、2倍速）
        slide_anim = CardAnimation(drawn_card, yama_x, yama_y, target_x, target_y, 45)
        active_animations.append(slide_anim)
        # 山札から場札エリアへのスライドアニメーション（45フレーム、0.75秒、2倍速）
        slide_anim = CardAnimation(drawn_card, yama_x, yama_y, target_x, target_y, 45)
        active_animations.append(slide_anim)
        
        # スライド完了後にマッチング判定を行う関数を設定
        def check_yama_match_after_slide():
            """スライド完了後のマッチング判定処理"""
            # 同じ月のカードがあるかチェック
            yama_matched = False  # 山札カードがマッチしたかのフラグ
            matched_field_card = None  # マッチした場札カード
            
            for field_card in field_cards[:]:  # 場札の各カードをチェック（リストのコピーを使用）
                # 引いたカード以外で同じ月のカードをチェック
                if (drawn_card.month == field_card.month and 
                    drawn_card != field_card):  # 引いたカード自身は除外
                    print(f"{'CPU' if is_cpu else 'Player'}: 山札の {drawn_card.name} と場の {field_card.name} が一致！")  # デバッグ出力
                    matched_field_card = field_card
                    yama_matched = True
                    break
            
            if yama_matched:  # マッチした場合
                # 強調表示を作成
                highlight = YamaCardHighlight(drawn_card, matched_field_card)  # ハイライト表示オブジェクトを作成
                active_yama_highlights.append(highlight)  # アクティブなハイライトリストに追加
                
                # 両方のカードを場札から削除
                field_cards.remove(drawn_card)  # 引いたカードを場札から削除
                field_cards.remove(matched_field_card)  # マッチしたカードを場札から削除
                
                # 取り札エリアの位置を計算
                end_x, end_y = get_captured_card_position(cpu_captured if is_cpu else player_captured, is_cpu, screen_height)
                
                # 両方のカードを取り札エリアに移動するアニメーション
                drawn_anim = CardAnimation(drawn_card, drawn_card.x, drawn_card.y, end_x, end_y, 60)  # 60フレーム（1秒、2倍速）
                drawn_anim.delay_frames = 30  # 0.5秒遅延（2倍速）
                
                field_anim = CardAnimation(matched_field_card, matched_field_card.x, matched_field_card.y, end_x + 10, end_y, 60)  # 60フレーム（2倍速）
                field_anim.delay_frames = 30  # 同時に開始（2倍速）
                
                active_animations.append(drawn_anim)  # 引いたカードのアニメーションを追加
                active_animations.append(field_anim)  # 場札のアニメーションを追加
                
                # カードを取り札リストに追加
                target_captured_list = cpu_captured if is_cpu else player_captured  # 対象の取り札リスト決定
                target_captured_list.append(drawn_card)  # 取り札に追加
                target_captured_list.append(matched_field_card)  # 取り札に追加
                
                # 取得した2枚のカードを取り札エリアでハイライト
                captured_cards_to_highlight = [drawn_card, matched_field_card]  # 取得した2枚のカードをハイライト対象に
                
                # 移動完了直後にハイライトを開始
                captured_highlight = CapturedCardHighlight(captured_cards_to_highlight, 30)  # 0.5秒間ハイライト（2倍速）
                captured_highlight.delay_frames = 60  # 修正: 移動完了と同時（1秒後、2倍速）
                captured_highlight.delay_count = 0
                active_captured_highlights.append(captured_highlight)  # アクティブなハイライトリストに追加
            else:
                # マッチしなかった場合は場札として残る
                print(f"{'CPU' if is_cpu else 'Player'}: 山札の {drawn_card.name} は場に残ります")  # デバッグ出力
            
            # 場札の位置を最終的に更新
            update_field_positions(field_cards)  # 場札の位置を更新
        
        # スライドアニメーションにコールバック関数を設定（45フレーム後に実行、2倍速）
        slide_anim.completion_callback = check_yama_match_after_slide
        
        return True  # 山札からカードを引いたことを返す
    return False  # 山札が空の場合はFalseを返す

def update_field_positions(field_cards, VERTICAL_SPACING=150):
    """場札の位置を更新する関数
    Args:
        field_cards: 場札のリスト
        VERTICAL_SPACING: 垂直間隔
    """
    for i, card in enumerate(field_cards):  # 各場札について
        card.x = 80 + i * 70  # x座標を設定（間隔70px）
        card.y = 100 + VERTICAL_SPACING  # y座標を設定（main.pyと統一）
        card.is_face_up = True  # カードを表向きに

def update_animations():
    """全てのアニメーションを更新する関数（カットインアニメーション対応）"""
    global active_animations, active_overlays, active_yama_highlights, active_captured_highlights, active_merge_animations, active_cutin_animations  # カットインアニメーション変数を追加
    
    # アニメーションの更新
    active_animations = [anim for anim in active_animations if anim.update()]  # アクティブなアニメーションのみを保持
    
    # 重ね合わせ表示の更新
    active_overlays = [overlay for overlay in active_overlays if overlay.update()]  # アクティブなオーバーレイのみを保持
    
    # 山札強調表示の更新
    active_yama_highlights = [highlight for highlight in active_yama_highlights if highlight.update()]  # アクティブなハイライトのみを保持
    
    # カットインアニメーションの更新
    active_cutin_animations = [cutin for cutin in active_cutin_animations if cutin.update()]
    
    # 新規追加: 重なり合いアニメーションの更新
    before_count = len(active_merge_animations)  # デバッグ用
    updated_merge_animations = []
    
    for i, merge_anim in enumerate(active_merge_animations):
        # アニメーションの詳細デバッグ情報
        if merge_anim.frame_count % 30 == 0:  # 0.5秒おきに出力
            current_phase = 1 if merge_anim.frame_count <= merge_anim.phase1_duration else \
                           2 if merge_anim.frame_count <= merge_anim.phase1_duration + merge_anim.phase2_duration else 3
            print(f"アニメーション{i}: フレーム{merge_anim.frame_count}/{merge_anim.duration}, フェーズ{current_phase}")
            print(f"    手札位置: ({merge_anim.hand_card.x:.1f}, {merge_anim.hand_card.y:.1f})")
            print(f"    場札位置: ({merge_anim.field_card.x:.1f}, {merge_anim.field_card.y:.1f})")
            print(f"    目標位置: ({merge_anim.end_x}, {merge_anim.end_y}), 重なり位置: ({merge_anim.merge_x}, {merge_anim.merge_y})")
            if current_phase == 1:
                print(f"    フェーズ1: 手札が場札の位置({merge_anim.merge_x}, {merge_anim.merge_y})まで移動中")
            elif current_phase == 2:
                print(f"    フェーズ2: 重なった状態で一時停止中")
            elif current_phase == 3:
                print(f"    フェーズ3: 重なって取り札エリアに移動中")
        
        if merge_anim.update():
            updated_merge_animations.append(merge_anim)
        else:
            print(f"重なり合いアニメーション完了: {merge_anim.hand_card.name} + {merge_anim.field_card.name}")
    
    active_merge_animations = updated_merge_animations
    after_count = len(active_merge_animations)  # デバッグ用
    
    # デバッグ出力（アニメーション数に変化があった場合のみ）
    if before_count != after_count:
        print(f"重なり合いアニメーション更新: {before_count} → {after_count}")
    
    # 新規追加: 取り札ハイライトの更新（遅延対応）
    updated_captured_highlights = []  # 更新後のハイライトリスト
    for highlight in active_captured_highlights:  # 各取り札ハイライトについて
        if hasattr(highlight, 'delay_frames') and hasattr(highlight, 'delay_count'):  # 遅延機能がある場合
            if highlight.delay_count < highlight.delay_frames:  # まだ遅延時間内の場合
                highlight.delay_count += 1  # 遅延カウントを増加
                updated_captured_highlights.append(highlight)  # リストに保持
            else:  # 遅延時間が終了した場合
                if highlight.update():  # 通常の更新処理
                    updated_captured_highlights.append(highlight)  # アクティブなら保持
        else:  # 遅延機能がない場合
            if highlight.update():  # 通常の更新処理
                updated_captured_highlights.append(highlight)  # アクティブなら保持
    active_captured_highlights = updated_captured_highlights  # リストを更新

def is_animations_active():
    """アニメーションが実行中かチェックする関数（カットインアニメーション対応）
    Returns:
        bool: アニメーションが実行中の場合True
    """
    return (len(active_animations) > 0 or len(active_overlays) > 0 or 
            len(active_yama_highlights) > 0 or len(active_captured_highlights) > 0 or
            len(active_merge_animations) > 0 or len(active_cutin_animations) > 0)  # カットインアニメーションも含めてチェック

def draw_overlays(screen):
    """重ね合わせ表示の描画関数
    Args:
        screen: 描画先の画面
    """
    for overlay in active_overlays:  # 各オーバーレイについて
        overlay.draw(screen)  # 画面に描画

def draw_yama_highlights(screen):
    """山札強調表示の描画関数
    Args:
        screen: 描画先の画面
    """
    for highlight in active_yama_highlights:  # 各ハイライトについて
        highlight.draw(screen)  # 画面に描画

def draw_captured_highlights(screen):
    """新規追加: 取り札ハイライト表示の描画関数
    Args:
        screen: 描画先の画面
    """
    for highlight in active_captured_highlights:  # 各取り札ハイライトについて
        # 遅延中でない場合のみ描画
        if not (hasattr(highlight, 'delay_frames') and highlight.delay_count < highlight.delay_frames):
            highlight.draw(screen)  # 画面に描画

def draw_merge_animations(screen):
    """新規追加: 重なり合いアニメーションの描画関数
    Args:
        screen: 描画先の画面
    """
    for merge_anim in active_merge_animations:  # 各重なり合いアニメーションについて
        # 遅延中でない場合のみ描画
        if merge_anim.delay_count >= merge_anim.delay_frames:
            # 場札を先に描画
            merge_anim.field_card.update_and_draw(screen)
            # 手札を上に重ねて描画
            merge_anim.hand_card.update_and_draw(screen)

def draw_normal_animations(screen):
    """新規追加: 通常のアニメーション中カードの描画関数
    Args:
        screen: 描画先の画面
    """
    for anim in active_animations:  # 各通常アニメーションについて
        # 遅延中でない場合のみ描画
        if hasattr(anim, 'delay_count') and hasattr(anim, 'delay_frames'):
            if anim.delay_count >= anim.delay_frames:
                anim.card.update_and_draw(screen)
        else:
            # 遅延機能がない場合は常に描画
            anim.card.update_and_draw(screen)

def draw_cutin_animations(screen):
    """新規追加: カットインアニメーションの描画関数
    Args:
        screen: 描画先の画面
    """
    for cutin in active_cutin_animations:  # 各カットインアニメーションについて
        if cutin.is_active:  # アクティブなカットインのみ描画
            cutin.draw(screen)  # カットインを描画