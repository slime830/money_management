import datetime
import os
import sys

import japanize_matplotlib as jplt
import matplotlib.pyplot as plt
import pandas as pd
from utils import NumberFormatter as nf
from utils import Terms

jplt.japanize()


class MoneyCalculator:
    def __init__(self, term, config):
        # コンストラクタ

        # 現在の期間
        self.terms = Terms(term)

        # ファイル読み込み用
        self.income = None  # 今期間の収入
        self.goal = None  # 目標貯金金額
        self.last_basic_saving = None  # 前期間の収入
        self.last_additional_saving = None  # 全期間時点での、貯金金額
        self.plan_df = None  # 今期間の計画DataFrame
        self.output_df = None  # 今期間の支出DataFrame
        self.output_types = list()  # 支出項目
        self.plan_by_type = dict()  # 項目と金額の対応（計画）
        self.output_by_type = dict()  # 項目と金額の対応（支出）

        # planの詳細
        self.plan_sum = None  # 計画の金額合計
        self.plan_additional_saving = None  # 計画によって生まれる貯金金額

        # 支出の詳細
        self.output_sum = None  # 支出の合計金額
        self.additional_saving = None  # 実際の貯金金額

        # 要件
        self.PAYDAY = config.PAYDAY  # 給料日
        self.BONUS_MONTHS = config.BONUS_MONTHS  # ボーナス月（set)
        self.BASIC_SAVING_KEY = (
            config.BASIC_SAVING_KEY
        )  # 定期貯金のキー（output_types.txtより）

        self.OUTPUT_TYPES_FILEPATH = (
            config.OUTPUT_TYPES_FILEPATH
        )  # output_types.txtのパス
        self.INCOME_FILEPATH = os.path.join(
            self.terms.current_term, config.INCOME_FILENAME
        )  # 今期間のincome.txtのパス
        self.GOAL_FILEPATH = os.path.join(
            self.terms.current_term, config.GOAL_FILENAME
        )  # 今期間のgoal.txtのパス
        self.PLAN_FILEPATH = os.path.join(
            self.terms.current_term, config.PLAN_FILENAME
        )  # 今期間のplan.csvのパス
        self.REAL_OUTPUT_FILEPATH = os.path.join(
            self.terms.current_term, config.REAL_OUTPUT_FILENAME
        )  # 今期間のoutput.csvのパス

        self.RESULT_FILEPATH = os.path.join(
            self.terms.current_term, config.RESULT_FILENAME
        )  # 今期間のplan_analyze_result.txtのパス
        self.BAR_FILEPATH = os.path.join(
            self.terms.current_term, config.BAR_FILENAME
        )  # 今期間の棒グラフのパス
        self.SETTLEMENT_FILEPATH = os.path.join(
            self.terms.current_term, config.SETTLEMENT_FILENAME
        )  # 今期間のsettlement.csvのパス

        self.NEXT_INCOME_FILEPATH = os.path.join(
            self.terms.next_term, config.INCOME_FILENAME
        )  # 次期間のincome.txtのパス
        self.NEXT_GOAL_FILEPATH = os.path.join(
            self.terms.next_term, config.GOAL_FILENAME
        )  # 次期間のgoal.txtのパス
        self.NEXT_PLAN_FILEPATH = os.path.join(
            self.terms.next_term, config.PLAN_FILENAME
        )  # 次期間のplan.csvのパス
        self.NEXT_REAL_OUTPUT_FILEPATH = os.path.join(
            self.terms.next_term, config.REAL_OUTPUT_FILENAME
        )  # 次期間のreal_output.txtのパス

        self.LAST_SETTLEMENT_FILEPATH = os.path.join(
            self.terms.last_term, config.SETTLEMENT_FILENAME
        )  # 前機関のsettlement.txtのパス

        self.FONT_SIZE = config.FONT_SIZE  # グラフ用のフォントサイズ
        self.LINE_WIDTH = config.LINE_WIDTH  # グラフの幅
        self.ENCODING = config.ENCODING  # 各ファイルの読み取り・書き込みのエンコーディング

        self.read_files()  # ファイルの読み込み

    def __call__(self, settle_frag):
        # 一連の処理 実質のメイン関数

        if settle_frag:
            if not self.is_available_settlement():
                print(f"あなたはまだ{self.terms.current_term}の決算はできません")
            elif os.path.isdir(self.terms.next_term):
                print(
                    f"あなたは既に{self.terms.current_term}の決算をしています（次期間のディレクトリが既に存在します）"
                )
        self.plan_analyze()
        self.analyze_real_output()
        if settle_frag:
            self.settle()

        print("\n----------------------- プログラム終了 --------------------------\n")

    def df_to_dict_by_types(self, df, types):
        # 計画や支出のDataFrameから、項目別の合計を表すdictを生成する

        assert "type" in df.columns
        assert "price" in df.columns

        d = {
            output_type: sum(list(df.price[df.type == output_type]))
            for output_type in types
        }

        return d

    def read_files(self):
        # ファイル読み込み

        with open(self.OUTPUT_TYPES_FILEPATH, "r", encoding=self.ENCODING) as f:
            self.output_types = [t.replace("\n", "") for t in f.readlines()]

        with open(self.INCOME_FILEPATH, "r", encoding=self.ENCODING) as f:
            self.income = int(f.readline().replace("\n", ""))

        with open(self.GOAL_FILEPATH, "r", encoding=self.ENCODING) as f:
            self.goal = int(f.readline().replace("\n", ""))

        self.plan_df = pd.read_csv(self.PLAN_FILEPATH, encoding=self.ENCODING)
        self.output_df = pd.read_csv(self.REAL_OUTPUT_FILEPATH)

        self.plan_by_type = self.df_to_dict_by_types(
            self.plan_df, self.output_types
        )
        self.output_by_type = self.df_to_dict_by_types(
            self.output_df, self.output_types
        )

        # 前期間のディレクトリが存在する時
        if os.path.isdir(self.terms.last_term):
            # settlement.csvが存在する時
            if os.path.exists(self.LAST_SETTLEMENT_FILEPATH):
                with open(
                    self.LAST_SETTLEMENT_FILEPATH, "r", encoding=self.ENCODING
                ) as f:
                    self.last_basic_saving = int(
                        f.readline().replace("\n", "").split(",")[0]
                    )
                    self.last_additional_saving = int(
                        f.readline().replace("\n", "").split(",")[0]
                    )
            else:
                print(f"まず{self.terms.last_term}を決算してください")
                sys.exit()

        else:
            self.last_basic_saving = 0
            self.last_additional_saving = 0

    def plan_analyze(self):
        # 計画を分析し、標準出力&ファイル出力

        print("\n----------------------- 計画分析 --------------------------\n")

        self.plan_sum = sum(self.plan_by_type.values())

        if self.plan_sum > self.income + self.last_additional_saving:
            print("この計画では、赤字です")
            sys.exit()

        self.plan_additional_saving = self.income - self.plan_sum

        with open(self.RESULT_FILEPATH, "w", encoding=self.ENCODING) as f:
            print(
                f"あなたは{nf.get_formatted_number(self.plan_by_type.get(self.BASIC_SAVING_KEY))} 円"
                + f"({round((self.plan_by_type.get(self.BASIC_SAVING_KEY)/self.income)*100)}%) を定期貯金します"
            )
            f.write(
                f"あなたは{nf.get_formatted_number(self.plan_by_type.get(self.BASIC_SAVING_KEY))} 円"
                + f"({round((self.plan_by_type.get(self.BASIC_SAVING_KEY)/self.income)*100)}%) を定期貯金します\n"
            )

            print(
                f"あなたは今期間に {nf.get_formatted_number(self.plan_additional_saving)} 円を追加で貯金します"
            )
            f.write(
                f"あなたは今期間に {nf.get_formatted_number(self.plan_additional_saving)} 円を追加で貯金します\n"
            )

            print(
                f"あなたの累計追加貯金額は {nf.get_formatted_number(self.plan_additional_saving + self.last_additional_saving)} 円になる予定です"
            )
            f.write(
                f"あなたの累計追加貯金額は {nf.get_formatted_number(self.plan_additional_saving + self.last_additional_saving)} 円になる予定です\n"
            )

    def plot_bar_by_type(self):
        # 各タイプごとの支出をプロットする

        plt.bar(
            list(self.plan_by_type.keys()),
            list(self.plan_by_type.values()),
            label="計画",
            align="edge",
            width=-self.LINE_WIDTH,
        )
        plt.bar(
            list(self.output_by_type.keys()),
            list(self.output_by_type.values()),
            label="支出",
            align="edge",
            width=self.LINE_WIDTH,
        )

        plt.title(
            f"{self.terms.current_term}における区分ごとの支出",
            fontsize=self.FONT_SIZE,
        )
        plt.xlabel("区分", fontsize=self.FONT_SIZE)
        plt.ylabel("支出 (円)", fontsize=self.FONT_SIZE)
        plt.legend()
        plt.grid()

        plt.savefig(self.BAR_FILEPATH)

    def analyze_real_output(self):
        # 実際の支出を纏めたcsvファイルを読み込み、総支出額当を計算する。
        print("\n----------------------- 支出分析 --------------------------\n")

        self.plot_bar_by_type()

        self.output_sum = sum(list(self.output_df.price))
        self.additional_saving = self.income - self.output_sum

        print(f"あなたは今期間で既に{nf.get_formatted_number(self.output_sum)}円使いました")

        if self.income + self.last_additional_saving > self.output_sum:
            print(
                f"今月はあと{nf.get_formatted_number(self.income+self.last_additional_saving-self.output_sum)}円使えます"
            )
        else:
            print("定期貯金に手を付けてしまっています")

    def is_available_settlement(self):
        # 現在決算可能か判定する
        term_info = self.terms.current_term.split("_")
        available_year, available_month, available_date = (
            int(term_info[0]),
            Terms.get_int_month(term_info[2]),
            self.PAYDAY,
        )
        today_year, today_month, today_date = tuple(
            datetime.date.today().strftime("%Y_%m_%d").split("_")
        )
        today_year = int(today_year)
        today_month = Terms.get_int_month(today_month)
        today_date = Terms.get_int_month(today_date)

        if available_year < today_year:  # 今の年が有効年よりも大きいなら
            return True
        elif available_year > today_year:  # 今の年が有効年よりも小さいなら
            return False
        else:  # それ以外（今の年＝有効年）なら
            if available_month < today_month:  # 今の月が有効月よりも大きいなら
                return True
            elif available_month > today_month:  # 今の月が有功月よりも小さいなら
                return False
            else:  # それ以外（今の月＝有効月）なら
                if available_date <= today_date:
                    return True
                else:
                    return False

    def make_next_term_directory(self, next_goal):
        # 次期間のディレクトリを作成する

        os.makedirs(self.terms.next_term)
        with open(self.NEXT_GOAL_FILEPATH, "w", encoding=self.ENCODING) as f:
            f.write(str(next_goal))
        with open(self.NEXT_INCOME_FILEPATH, "w", encoding=self.ENCODING) as f:
            f.write("0")
        with open(self.NEXT_PLAN_FILEPATH, "w", encoding=self.ENCODING) as f:
            f.write("title,price,type")
        with open(
            self.NEXT_REAL_OUTPUT_FILEPATH, "w", encoding=self.ENCODING
        ) as f:
            f.write("date,price,note,type")

    def settle(self):
        # 決算し、決算用のファイルを出力する
        print(
            f"\n----------------------- {self.terms.current_term}の決算 --------------------------\n"
        )

        total_additional_saving = (
            self.additional_saving + self.last_additional_saving
        )

        total_basic_saving = (
            self.output_by_type.get(self.BASIC_SAVING_KEY)
            + self.last_basic_saving
        )

        with open(self.SETTLEMENT_FILEPATH, "w", encoding=self.ENCODING) as f:
            f.write(f"{total_basic_saving},{self.BASIC_SAVING_KEY}\n")
            f.write(f"{total_additional_saving},additional_saving")

        print(
            f"あなたの累積追加貯金額は {nf.get_formatted_number(total_additional_saving)} 円です"
        )

        if total_additional_saving <= self.goal:
            next_goal = self.goal - total_additional_saving
        else:
            next_goal = 0

        self.make_next_term_directory(next_goal)
