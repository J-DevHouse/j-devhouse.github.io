# App Store Screenshots Generator

## 使い方

### 1. スクリーンショットを配置

`raw/` フォルダに以下の名前でスクリーンショットを配置してください：

| ファイル名 | 画面 | 推奨順序 |
|-----------|------|---------|
| `01_calendar.png` | カレンダー画面 | 1 |
| `02_scan.png` | レシートスキャン（カメラ）画面 | 2 |
| `03_input.png` | 入力画面 | 3 |
| `04_statistics.png` | 統計画面 | 4 |
| `05_widget.png` | ウィジェット画面 | 5 |
| `06_scanlist.png` | スキャン一覧画面 | 6 |
| `07_category.png` | カテゴリー選択画面 | （任意） |
| `08_settings.png` | 設定画面 | （任意） |

- .jpg / .jpeg も使用可能
- 全部揃っていなくてもOK（あるファイルだけ処理します）
- App Store では最大10枚まで登録可能

### 2. スクリプトを実行

```bash
cd AppStore_Screenshots
python3 generate.py
```

### 3. 出力を確認

`exports/` フォルダに3サイズ分のスクリーンショットが生成されます：

```
exports/
├── 6.9/    ← iPhone 16 Pro Max (1320×2868) ※必須
├── 6.5/    ← iPhone 15 Plus 等 (1284×2778)
└── 5.5/    ← iPhone 8 Plus 等 (1242×2208)
```

### 4. App Store Connect にアップロード

App Store Connect → アプリ → バージョン → スクリーンショット に各サイズの画像をドラッグ＆ドロップ。

## カスタマイズ

`generate.py` 内の `SCREENSHOTS` リストで以下を変更できます：

- `headline` - メインキャプション
- `sub` - サブキャプション
- `bg` - 背景グラデーション色 (上, 下)
- `text_color` - テキスト色

## テキストメタデータ

App Store に入力するテキスト情報は `AppStore_Metadata_JP.md` を参照してください。
