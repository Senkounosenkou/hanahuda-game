import pygame  # Pygameライブラリをインポート
import math  # 数学関数をインポート（より滑らかなイージング用）
import os  # ファイル操作用
import sys  # pyinstaller対応のパス解決用

class CardMergeAnimation:
    """2枚のカードが重なり合いながら移動するアニメーションクラス（修正版）"""
    def __init__(self, hand_card, field_card, end_x, end_y, duration=120):
        """重なり合いアニメーションの初期化
        Args:
            hand_card: 手札カード
            field_card: 場札カード
            end_x: 最終                    # 画面サイズに応じた適切なサイズを計算（画面幅の20%程度を目安）
                    target_width = int(self.screen_width * 0.2)
                    scale_factor = target_width / original_width
                    scaled_width = int(original_width * scale_factor)
                    scaled_height = int(original_height * scale_factor)
            end_y: 最終到達y座標
            duration: アニメーション時間（フレーム数、デフォルト120=2秒、2倍速）
        """
        self.hand_card = hand_card  # 手札カード
        self.field_card = field_card  # 場札カード
        self.end_x = end_x  # 最終到達x座標
        self.end_y = end_y  # 最終到達y座標
        self.duration = duration  # アニメーション時間
        self.frame_count = 0  # 現在のフレーム数
        self.is_active = True  # アニメーションがアクティブかどうか
        self.delay_frames = 0  # 遅延時間
        self.delay_count = 0  # 遅延カウント
        
        # 初期位置を保存
        self.hand_start_x = hand_card.x
        self.hand_start_y = hand_card.y
        self.field_start_x = field_card.x
        self.field_start_y = field_card.y
        
        # 中間地点（場札の位置で重なる）
        self.merge_x = field_card.x
        self.merge_y = field_card.y
        
        # 3段階のアニメーション時間配分（2倍速）
        self.phase1_duration = 40  # フェーズ1: 手札が場札に移動（約0.65秒）
        self.phase2_duration = 20  # フェーズ2: 重なった状態で停止（約0.35秒）
        self.phase3_duration = 60  # フェーズ3: 重なって取り札エリアに移動（1秒）
        
    def update(self):
        """重なり合いアニメーションの更新処理（完全修正版）"""
        if not self.is_active:
            return False
            
        # 遅延処理
        if self.delay_count < self.delay_frames:
            self.delay_count += 1
            return True
            
        self.frame_count += 1
        
        # 現在のフェーズを判定
        if self.frame_count <= self.phase1_duration:
            # フェーズ1: 手札が場札の位置に向かって移動
            progress = self.frame_count / self.phase1_duration
            eased_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            
            # デバッグ用：フェーズ1の実際の計算を出力
            if self.frame_count % 30 == 0:
                print(f"    フェーズ1計算: progress={progress:.2f}, eased={eased_progress:.2f}")
                print(f"    手札移動: ({self.hand_start_x}, {self.hand_start_y}) → ({self.merge_x}, {self.merge_y})")
            
            # 手札を場札の位置まで移動
            self.hand_card.x = self.hand_start_x + (self.merge_x - self.hand_start_x) * eased_progress
            self.hand_card.y = self.hand_start_y + (self.merge_y - self.hand_start_y) * eased_progress
            # 場札は元の位置のまま動かない
            self.field_card.x = self.field_start_x
            self.field_card.y = self.field_start_y
            
        elif self.frame_count <= self.phase1_duration + self.phase2_duration:
            # フェーズ2: 重なった状態で一時停止
            # 手札を場札の少し上と右にずらして配置（絵柄が見える程度）
            self.hand_card.x = self.merge_x + 12  # 12px右にずらす
            self.hand_card.y = self.merge_y - 8   # 8px上にずらす
            # 場札は元の位置のまま
            self.field_card.x = self.field_start_x
            self.field_card.y = self.field_start_y
            
        elif self.frame_count <= self.phase1_duration + self.phase2_duration + self.phase3_duration:
            # フェーズ3: 重なった状態で最終位置に移動
            phase3_elapsed = self.frame_count - (self.phase1_duration + self.phase2_duration)
            progress = phase3_elapsed / self.phase3_duration
            eased_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            
            # 手札の移動（重なった位置から最終位置へ）
            start_x = self.merge_x + 12
            start_y = self.merge_y - 8
            self.hand_card.x = start_x + (self.end_x - start_x) * eased_progress
            self.hand_card.y = start_y + (self.end_y - start_y) * eased_progress
            
            # 場札の移動（元の位置から最終位置へ）
            self.field_card.x = self.field_start_x + ((self.end_x + 8) - self.field_start_x) * eased_progress
            self.field_card.y = self.field_start_y + (self.end_y - self.field_start_y) * eased_progress
            
        else:
            # アニメーション完了
            self.hand_card.x = self.end_x
            self.hand_card.y = self.end_y
            self.field_card.x = self.end_x + 8  # 少しずらして配置
            self.field_card.y = self.end_y
            self.is_active = False
            return False
            
        return True

class CardAnimation:
    """カードのアニメーション管理クラス（改良版）"""
    def __init__(self, card, start_x, start_y, end_x, end_y, duration=60):  # 修正: 60フレーム（1秒、2倍速）
        """アニメーション初期化
        Args:
            card: アニメーション対象のカード
            start_x: 開始x座標
            start_y: 開始y座標
            end_x: 終了x座標
            end_y: 終了y座標
            duration: アニメーション時間（フレーム数、デフォルト60=1秒、2倍速）
        """
        self.card = card  # アニメーションするカードオブジェクト
        self.start_x = start_x  # アニメーション開始のx座標
        self.start_y = start_y  # アニメーション開始のy座標
        self.end_x = end_x  # アニメーション終了のx座標
        self.end_y = end_y  # アニメーション終了のy座標
        self.duration = duration  # アニメーションの長さ（フレーム数）
        self.frame_count = 0  # 現在のフレーム数
        self.is_active = True  # アニメーションが実行中かどうか
        self.delay_frames = 0  # 遅延時間（フレーム数）
        self.delay_count = 0  # 現在の遅延カウント
        self.completion_callback = None  # 完了時に実行するコールバック関数
        
    def update(self):
        """アニメーションの更新処理（改良版）"""
        if not self.is_active:  # アニメーションが非アクティブの場合
            return False  # 処理を終了
        
        # 遅延処理
        if self.delay_count < self.delay_frames:  # まだ遅延時間内の場合
            self.delay_count += 1  # 遅延カウントを増加
            return True  # アニメーションは継続中
            
        self.frame_count += 1  # フレームカウントを増加
        progress = self.frame_count / self.duration  # アニメーション進行度を計算（0.0-1.0）
        
        if progress >= 1.0:  # アニメーションが完了した場合
            self.card.x = self.end_x  # カードを最終位置に配置
            self.card.y = self.end_y  # カードを最終位置に配置
            self.is_active = False  # アニメーションを非アクティブに
            
            # コールバック関数があれば実行
            if self.completion_callback:
                self.completion_callback()
            
            return False  # アニメーション完了を返す
        
        # 修正: より滑らかなイージング関数（サイン波ベース）
        eased_progress = 0.5 - 0.5 * math.cos(progress * math.pi)  # サイン波による滑らかなイージング
        
        # 現在の位置を計算（小数点精度を保持）
        self.card.x = self.start_x + (self.end_x - self.start_x) * eased_progress  # x座標を補間
        self.card.y = self.start_y + (self.end_y - self.start_y) * eased_progress  # y座標を補間
        
        return True  # アニメーション継続中を返す

class CardOverlayDisplay:
    """カードオーバーレイ表示クラス（取得カードの表示用）"""
    def __init__(self, hand_card, field_card, display_duration=60):  # 修正: 90→60フレーム（1秒）
        """オーバーレイ表示の初期化
        Args:
            hand_card: 手札カード
            field_card: 場札カード
            display_duration: 表示時間（フレーム数、短縮）
        """
        self.hand_card = hand_card  # 手札のカード
        self.field_card = field_card  # 場札のカード
        self.display_duration = display_duration  # 表示時間
        self.frame_count = 0  # 現在のフレーム数
        self.is_active = True  # 表示がアクティブかどうか
        
        # 手札カードを場札カードの位置に少しずらして配置
        self.original_hand_x = hand_card.x  # 手札の元のx座標を保存
        self.original_hand_y = hand_card.y  # 手札の元のy座標を保存
        self.hand_card.x = field_card.x + 10  # 手札を場札位置の少し右にずらす
        self.hand_card.y = field_card.y - 5  # 手札を場札位置の少し上にずらす
        self.hand_card.is_face_up = True  # 手札を表向きに設定
        
    def update(self):
        """オーバーレイ表示の更新処理"""
        if not self.is_active:  # 表示が非アクティブの場合
            return False  # 処理を終了
            
        self.frame_count += 1  # フレームカウントを増加
        if self.frame_count >= self.display_duration:  # 表示時間が終了した場合
            self.is_active = False  # 表示を非アクティブに
            return False  # 表示終了を返す
        return True  # 表示継続中を返す
    
    def draw(self, screen):
        """オーバーレイ表示の描画処理（金色枠なし）"""
        if self.is_active:  # 表示がアクティブの場合
            # 場札を先に描画
            self.field_card.update_and_draw(screen)  # 場札カードを描画
            # 手札を上に重ねて描画
            self.hand_card.update_and_draw(screen)  # 手札カードを重ねて描画
            
            # 金色の枠は削除（重ね合わせ表示のみ）

class YamaCardHighlight:
    """山札カードハイライト表示クラス"""
    def __init__(self, drawn_card, matched_field_card, display_duration=30):  # 修正: 30フレーム（0.5秒、2倍速）
        """山札ハイライト表示の初期化
        Args:
            drawn_card: 引いた山札カード
            matched_field_card: マッチした場札カード
            display_duration: 表示時間（フレーム数、2倍速）
        """
        self.drawn_card = drawn_card  # 山札から引いたカード
        self.matched_field_card = matched_field_card  # マッチした場札カード
        self.display_duration = display_duration  # 表示時間
        self.frame_count = 0  # 現在のフレーム数
        self.is_active = True  # 表示がアクティブかどうか
        
    def update(self):
        """ハイライト表示の更新処理"""
        if not self.is_active:  # 表示が非アクティブの場合
            return False  # 処理を終了
            
        self.frame_count += 1  # フレームカウントを増加
        if self.frame_count >= self.display_duration:  # 表示時間が終了した場合
            self.is_active = False  # 表示を非アクティブに
            return False  # 表示終了を返す
        return True  # 表示継続中を返す
    
    def draw(self, screen):
        """ハイライト表示の描画処理（金色枠なし）"""
        if self.is_active:  # 表示がアクティブの場合
            # まず通常のカードを描画
            self.drawn_card.update_and_draw(screen)  # 引いた山札カードを描画
            self.matched_field_card.update_and_draw(screen)  # マッチした場札カードを描画
            
            # 金色の枠は削除（カード表示のみ）

class CapturedCardHighlight:
    """取り札エリアの同じ月のカードをハイライト表示するクラス"""
    def __init__(self, cards_to_highlight, display_duration=15):  # 0.25秒間光らせる（2倍速）
        """取り札ハイライト表示の初期化
        Args:
            cards_to_highlight: ハイライトするカードのリスト
            display_duration: 表示時間（フレーム数、デフォルト15=0.25秒、2倍速）
        """
        self.cards_to_highlight = cards_to_highlight  # ハイライトするカードのリスト
        self.display_duration = display_duration  # 表示時間
        self.frame_count = 0  # 現在のフレーム数
        self.is_active = True  # 表示がアクティブかどうか
        self.delay_frames = 0  # 遅延時間
        self.delay_count = 0  # 遅延カウント
        
    def update(self):
        """ハイライト表示の更新処理（遅延対応）"""
        if not self.is_active:  # 表示が非アクティブの場合
            return False  # 処理を終了
        
        # 遅延処理
        if self.delay_count < self.delay_frames:  # まだ遅延時間内の場合
            self.delay_count += 1  # 遅延カウントを増加
            return True  # 表示継続中（ただし描画はしない）
            
        self.frame_count += 1  # フレームカウントを増加
        if self.frame_count >= self.display_duration:  # 表示時間が終了した場合
            self.is_active = False  # 表示を非アクティブに
            return False  # 表示終了を返す
        return True  # 表示継続中を返す
    
    def draw(self, screen):
        """取り札ハイライト表示の描画処理（パルス効果付き）"""
        if self.is_active and self.delay_count >= self.delay_frames:  # 表示がアクティブかつ遅延完了の場合
            # パルス効果（ゆっくりとした光り方）
            pulse_factor = 0.3 + 0.7 * math.sin(self.frame_count * 0.2)  # ゆっくりとしたパルス効果（0.3-1.0の範囲）
            frame_thickness = int(2 + 4 * pulse_factor)  # 線の太さを2-6pxで変動
            
            # 各ハイライト対象カードに枠を描画
            for card in self.cards_to_highlight:  # ハイライト対象の各カードについて
                if hasattr(card, 'x') and hasattr(card, 'y'):  # カードに座標があることを確認
                    # 金色の光る枠を描画
                    pygame.draw.rect(screen, (255, 215, 0),  # 金色の枠
                                   (card.x-4, card.y-4,  # カードの位置から少し外側
                                    card.get_image().get_width()+8,  # 幅を少し大きく
                                    card.get_image().get_height()+8), 4)  # 枠の太さ


class YakuCutInAnimation:
    """役ができた時のカットインアニメーションクラス"""
    def __init__(self, yaku_name, screen_width, screen_height, duration=90):
        """カットインアニメーションの初期化
        Args:
            yaku_name: 役の名前（例："五光", "猪鹿蝶"など）
            screen_width: 画面幅
            screen_height: 画面高さ
            duration: アニメーション時間（フレーム数、デフォルト90=1.5秒、2倍速）
        """
        self.yaku_name = yaku_name
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.duration = duration
        self.frame_count = 0
        self.is_active = True
        
        # カットイン画像の読み込み（後で追加される画像に対応）
        self.cutin_image = None
        self.load_cutin_image()
        
        # デバッグ出力
        print(f"🎬 YakuCutInAnimation初期化: {yaku_name}")
        print(f"   画像読み込み結果: {'成功' if self.cutin_image else 'テキストモード'}")
        
        # アニメーション段階（2倍速）
        self.phase1_duration = 15  # スライドイン（0.25秒）
        self.phase2_duration = 60  # 表示停止（1秒）
        self.phase3_duration = 15  # スライドアウト（0.25秒）
        
        # アニメーション位置計算
        if self.cutin_image:
            self.image_width = self.cutin_image.get_width()
            self.image_height = self.cutin_image.get_height()
        else:
            # テキストモードの場合のデフォルトサイズ
            self.image_width = 400
            self.image_height = 100
            
        self.start_x = -self.image_width  # 画面左外から開始
        self.end_x = (screen_width - self.image_width) // 2  # 画面中央
        self.exit_x = screen_width  # 画面右外へ退場
        self.y = (screen_height - self.image_height) // 2  # 垂直中央
        
        # 現在位置
        self.current_x = self.start_x
        
        print(f"   カットイン画像サイズ: {self.image_width} x {self.image_height}")
        print(f"   アニメーション位置: start={self.start_x}, center={self.end_x}, exit={self.exit_x}, y={self.y}")
        
    def load_cutin_image(self):
        """カットイン画像の読み込み"""
        try:
            # 役名から点数部分を除去（例："三光 (5文)" → "三光"）
            clean_yaku_name = self.yaku_name.split(' ')[0]  # スペースの前の部分を取得
            
            # 特定の役名を画像ファイル名にマッピング
            name_mapping = {
                "種": "タネ",
                "短": "タン", 
                "カス": "カス" 
            }
            
            # マッピングがある場合は変換
            if clean_yaku_name in name_mapping:
                file_yaku_name = name_mapping[clean_yaku_name]
                print(f"   役名マッピング: {clean_yaku_name} → {file_yaku_name}")
            else:
                file_yaku_name = clean_yaku_name
            
            # 役名に応じた画像ファイルを探索（cutinフォルダ内） - pyinstaller対応
            if getattr(sys, 'frozen', False):
                # pyinstallerで作成された実行ファイルの場合
                base_dir = sys._MEIPASS
            else:
                # 開発環境（.pyファイル実行）の場合
                base_dir = os.path.dirname(__file__)
            
            image_path = os.path.join(base_dir, "assets", "img", "cutin", f"{file_yaku_name}_cutin.png")
            
            print(f"   カットイン画像パス: {image_path}")
            print(f"   元の役名: {self.yaku_name} → クリーン役名: {clean_yaku_name}")
            
            if os.path.exists(image_path):
                original_image = pygame.image.load(image_path)
                # 元の画像サイズを取得
                original_width = original_image.get_width()
                original_height = original_image.get_height()
                # 画面サイズに応じた適切なサイズを計算（画面幅の50%程度を目安）
                target_width = int(self.screen_width * 0.5)
                scale_factor = target_width / original_width
                scaled_width = int(original_width * scale_factor)
                scaled_height = int(original_height * scale_factor)
                
                self.cutin_image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
                print(f"   カットイン画像読み込み成功: {image_path}")
                print(f"   元のサイズ: {original_width}x{original_height} → スケール後: {scaled_width}x{scaled_height} (倍率: {scale_factor:.2f})")
            else:
                # 画像が見つからない場合はデフォルト画像を探索 - pyinstaller対応
                if getattr(sys, 'frozen', False):
                    # pyinstallerで作成された実行ファイルの場合
                    base_dir = sys._MEIPASS
                else:
                    # 開発環境（.pyファイル実行）の場合
                    base_dir = os.path.dirname(__file__)
                    
                default_path = os.path.join(base_dir, "assets", "img", "cutin", "default_cutin.png")
                if os.path.exists(default_path):
                    original_image = pygame.image.load(default_path)
                    # 元の画像サイズを取得
                    original_width = original_image.get_width()
                    original_height = original_image.get_height()
                    
                    # 画面サイズに応じた適切なサイズを計算（画面幅の30%程度を目安）
                    target_width = int(self.screen_width * 0.3)
                    scale_factor = target_width / original_width
                    scaled_width = int(original_width * scale_factor)
                    scaled_height = int(original_height * scale_factor)
                    
                    self.cutin_image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
                    print(f"   デフォルトカットイン画像読み込み成功: {default_path}")
                    print(f"   元のサイズ: {original_width}x{original_height} → スケール後: {scaled_width}x{scaled_height} (倍率: {scale_factor:.2f})")
                else:
                    print(f"   カットイン画像が見つかりません: {image_path}")
                    self.cutin_image = None
        except Exception as e:
            print(f"   カットイン画像読み込みエラー: {e}")
            self.cutin_image = None
    
    def update(self):
        """カットインアニメーションの更新処理"""
        if not self.is_active:
            return False
            
        self.frame_count += 1
        
        if self.frame_count <= self.phase1_duration:
            # フェーズ1: スライドイン
            progress = self.frame_count / self.phase1_duration
            # イージングアウト効果
            eased_progress = 1 - math.pow(1 - progress, 3)
            self.current_x = self.start_x + (self.end_x - self.start_x) * eased_progress
            
        elif self.frame_count <= self.phase1_duration + self.phase2_duration:
            # フェーズ2: 表示停止
            self.current_x = self.end_x
            
        elif self.frame_count <= self.duration:
            # フェーズ3: スライドアウト
            phase3_progress = (self.frame_count - self.phase1_duration - self.phase2_duration) / self.phase3_duration
            # イージングイン効果
            eased_progress = math.pow(phase3_progress, 3)
            self.current_x = self.end_x + (self.exit_x - self.end_x) * eased_progress
            
        else:
            # アニメーション終了
            self.is_active = False
            return False
            
        return True
    
    def draw(self, screen):
        """カットインの描画"""
        if not self.is_active:
            return
            
        if self.cutin_image:
            # カットイン画像がある場合
            screen.blit(self.cutin_image, (int(self.current_x), self.y))
        else:
            # 画像がない場合はテキストベースのカットインを表示
            # 背景矩形（濃い赤色のグラデーション）
            bg_rect = pygame.Rect(int(self.current_x), self.y, self.image_width, self.image_height)
            bg_surface = pygame.Surface((self.image_width, self.image_height))
            bg_surface.set_alpha(220)
            
            # グラデーション効果（簡易版）
            for i in range(self.image_height):
                alpha = int(220 * (1 - i / self.image_height * 0.3))
                color = (min(255, 100 + i), 20, 20)  # 赤系グラデーション
                pygame.draw.line(bg_surface, color, (0, i), (self.image_width, i))
            
            screen.blit(bg_surface, (int(self.current_x), self.y))
            
            # 二重枠線（金色と白）
            pygame.draw.rect(screen, (255, 215, 0), bg_rect, 8)  # 外側金色
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 3)  # 内側白色
            
            # テキスト表示（日本語フォント必要）
            try:
                # 日本語フォントの取得（main.pyのget_japanese_font相当）
                font_paths = [
                    "C:/Windows/Fonts/msgothic.ttc",
                    "C:/Windows/Fonts/meiryo.ttc",
                    "C:/windows/Fonts/msmincho.ttc",
                    "C:/windows/Fonts/yugothic.ttc"
                ]
                
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = pygame.font.Font(path, 56)  # フォントサイズを大きく
                        break
                
                if font is None:
                    font = pygame.font.Font(None, 56)
                
                # 役名テキスト（影付き）
                # 影
                shadow_surface = font.render(self.yaku_name, True, (0, 0, 0))
                shadow_rect = shadow_surface.get_rect(center=(int(self.current_x) + self.image_width//2 + 3, self.y + self.image_height//2 - 15 + 3))
                screen.blit(shadow_surface, shadow_rect)
                # 本体
                text_surface = font.render(self.yaku_name, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(int(self.current_x) + self.image_width//2, self.y + self.image_height//2 - 15))
                screen.blit(text_surface, text_rect)
                
                # 「役成立！」テキスト（小さめフォント）
                small_font = pygame.font.Font(font.get_fontname() if hasattr(font, 'get_fontname') else None, 32)
                if small_font is None:
                    small_font = pygame.font.Font(None, 32)
                    
                # 影
                yaku_shadow = small_font.render("役成立！", True, (0, 0, 0))
                yaku_shadow_rect = yaku_shadow.get_rect(center=(int(self.current_x) + self.image_width//2 + 2, self.y + self.image_height//2 + 35 + 2))
                screen.blit(yaku_shadow, yaku_shadow_rect)
                # 本体
                yaku_text = small_font.render("役成立！", True, (255, 215, 0))
                yaku_rect = yaku_text.get_rect(center=(int(self.current_x) + self.image_width//2, self.y + self.image_height//2 + 35))
                screen.blit(yaku_text, yaku_rect)
                
            except Exception as e:
                # フォント読み込みに失敗した場合のフォールバック
                font = pygame.font.Font(None, 48)
                text_surface = font.render(f"{self.yaku_name} YAKU!", True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(int(self.current_x) + self.image_width//2, self.y + self.image_height//2))
                screen.blit(text_surface, text_rect)