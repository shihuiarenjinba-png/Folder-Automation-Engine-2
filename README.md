# Folder Automation Engine -2

一般ユーザー向けのWindowsファイル整理アプリ。ここは通常版とは別の製品用リポジトリです。

## 操作
1. 基準フォルダーをWindowsのフォルダー選択ダイアログから選びます。
2. 読み込み元と保存先を選択し、拡張子やファイル名パターンを指定します。
3. 変更しない**試運転**で対象とルールを確認します。
4. 明示的な確認後にコピーまたは移動を実行します。既存ファイルへの上書きは禁止です。
5. 監視は任意。明示確認と試運転が必要で、アプリを閉じると停止します。

技術設定を理解していなくても利用できる導線を目指しますが、**安全な取り消し／復元機能はまだ未実装**です。実データに対する操作前に確認してください。

## 状態
- Ported from source repo `shihuiarenjinba-png/folder-automation-engine`, exact SHA `853b47ce82d936a0a74a345153f90da40934527a` (2026-10-24).
- QA source branch: `codex/consumer-v2-initial-20261024`
- ここは **Windowsテスト／未署名EXEの検証段階**。MSIXやStore提出物ではありません。
- -2専用の Store ID, Identity, Publisher, PFN, versionは未照合のためHOLD。
- 旧製品のMSIX設定・Store ID・Package Identityは移植していません。
- Windows実機GUIの操作確認、1024×768と1280×720、第三者ライセンス確認が必要。
- main/releaseへの直接変更や提出・公開を禁止しています。

## 開発
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python folder_desktop_app.py --self-test
python folder_desktop_app.py
```

Windows検証用EXE: `./build-folder-desktop-validation.ps1`。
