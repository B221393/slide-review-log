# スライド指摘メモ / Slide Review Log

スライドの指摘を受けた日・版・ページと一緒に記録し，次の改訂で未対応の指摘を一覧にするCLIです．

打ち合わせのたびに発表資料の版が変わり，前回の修正指示が会議メモに埋もれることから作りました．同じ資料には同じ `--deck` を使います．ページ番号は指摘を受けた版での位置です．

## 実行例

Python 3.10以上が必要です．次は架空の資料を使った例です．

```sh
python -m pip install .
slide-review-log add --deck demo --version v1 --slide 4 --date 2026-01-10 "Add units to the vertical axis"
# Added #1
slide-review-log list --deck demo
# #1 2026-01-10 v1 p4 [open] Add units to the vertical axis
slide-review-log resolve 1 --version v2
# Resolved #1 in v2
slide-review-log list --deck demo --all
# #1 2026-01-10 v1 p4 [resolved in v2] Add units to the vertical axis
```

作業フォルダに `slide-review.sqlite3` を作ります．保存場所を変更する場合は，サブコマンドの前に `--db PATH` を付けます．このCLIが扱うのは手入力した指摘です．ページの自動対応付けや複数端末への同期には対応していません．

## テスト

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```
