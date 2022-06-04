import argparse

from MoneyCalculator import MoneyCalculator


class Config:
    def __init__(self):

        # 詳しくはMoneyCalculator側で説明

        # 要件系
        self.PAYDAY = 20  # 給料日 書き換える
        self.BASIC_SAVING_KEY = "basic saving"
        self.RENT_KEY = "rent"
        self.OUTPUT_TYPES_FILEPATH = "output_types.txt"

        # 入力ファイル名
        self.INCOME_FILENAME = "income.txt"
        self.GOAL_FILENAME = "additional_goal.txt"
        self.PLAN_FILENAME = "plan.csv"
        self.REAL_OUTPUT_FILENAME = "real_output.csv"

        # 出力ファイル名
        self.RESULT_FILENAME = "plan_analyze_result.txt"
        self.BAR_FILENAME = "output_by_type_bar.png"
        self.SETTLEMENT_FILENAME = "settlement.csv"

        # その他設定
        self.FONT_SIZE = 12
        self.LINE_WIDTH = 0.4
        self.ENCODING = "utf-8"


def main(args):
    config = Config()
    money_calculator = MoneyCalculator(args.term, config)
    money_calculator(args.settlement)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--term",
        help="計算する期間（ディレクトリ名） yyyy_mm_mm形式 必須項目",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--settlement",
        help="決算 settlement.csvを出力し、次期間のディレクトリを作成する。",
        action="store_true",
    )
    main(parser.parse_args())
