# 貯金管理プログラム

Office （Excel）が無い ＆「Google スプレッドシートで管理するのは、インターネット上に個人情報を保存するみたいで嫌だ！」
という人向けの、貯金管理プログラムです

貯金は「定期貯金」と「追加貯金」に分けています。
追加貯金はおこづかい的なイメージで、定期貯金は人生設計上の貯金（マイホームなど）というイメージです。

ほぼ個人用です。

## 環境

- OS: Ubuntu / Windows10 (Windows Subsystem for Linux)
- 言語: Python 3.8.4

## 必要ライブラリ

- pandas == 1.1.3
- matplotlib == 3.3.2
- japanize_matplotlib == 1.1.3

## 実行方法

1. 管理する期間（以下の場合、2000 年 4 月の給与日～ 5 月の給与日前日）のディレクトリを、`YYYY_MM_MM`をコピーすることで作成
   ```bash
   cp YYYY_MM_MM 2000_04_05
   ```
2. 1 で作ったディレクトリの `income.txt` , `goal.txt` , `plan.csv` , `real_output.csv` に、それぞれ収入・目標追加貯金額・支出計画・実際の支出を記入する

   - `income.txt`

     ```
     10000000
     ```

   - `additional_goal.txt`

     ```
     100000000
     ```

   - `plan.csv`

     ```cs
     title,price,type
     定期貯金,10000000,basic saving
     家賃,10000000,rent
     キャバクラ,10000000,playing
     デート,10000000,date
     ```

     一行目("title,price,type")は必ず固定

     `title` に目的を記述し、 `price` にその金額、`type`に分類（`output_types.txt`に準拠）を記述する。

   - `real_output.csv`

     ```cs
     date,price,note,type
     20000420,10000000,定期貯金,basic saving
     20000501,10000000,家賃4月分,rent
     20000502,5000000,キャバクラ,playing
     20000503,5000000,デート,date
     ```

     `type`は`output_types`に書いてあるものに統一する

3. `main.py` を実行

- 通常時

  ```bash
  python3 main.py -t 2000_04_05
  ```

- 決算時

  ```bash
  python3 main.py -t 2000_04_05 -s
  ```

  通常時は、計画分析ファイル（`plan_analyze_result.txt`）、項目別の支出棒グラフ（`output_by_type_bar.png`）を出力する。

  決算時は通常時に加えて、決算ファイル（`settlement.csv`）を出力する

  期間中の決算は出来ない（給料日が 20 日なら、2000/05/20 までは決算出来ない）

4. 実行結果

- 標準出力

  - 通常時

    ```
    ---------------------- 計画分析 --------------------------

    あなたは10,000,000 円(10%) を定期貯金します
    あなたは今期間に 60,000,000 円を追加で貯金します
    あなたの累計追加貯金額は 60,000,000 円になる予定です

    ----------------------- 支出分析 --------------------------

    あなたは今期間で既に30,000,000円使いました
    今月はあと70,000,000円使えます

    ----------------------- プログラム終了 --------------------------
    ```

  - 決算時

    ```
    ----------------------- 計画分析 --------------------------

    あなたは10,000,000 円(10%) を定期貯金します
    あなたは今期間に 60,000,000 円を追加で貯金します
    あなたの累計追加貯金額は 60,000,000 円になる予定です

    ----------------------- 支出分析 --------------------------

    あなたは今期間で既に30,000,000円使いました
    今月はあと70,000,000円使えます

    ----------------------- 2000_04_05の決算 --------------------------

    あなたの累積追加貯金額は 70,000,000 円です

    ----------------------- プログラム終了 --------------------------
    ```

- 計画分析ファイル（`plan_analyze_result.txt`）

  ```
  あなたは10,000,000 円(10%) を定期貯金します
  あなたは今期間に 60,000,000 円を追加で貯金します
  あなたの累計追加貯金額は 60,000,000 円になる予定です
  ```

- 棒グラフ（`output_by_type_bar.png`）
  ![棒グラフ](/misc/output_by_type_bar.png)

- 決算ファイル
  ```
  10000000,basic saving
  70000000,additional saving
  ```
