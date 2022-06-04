import re
import sys


class Terms:
    def __init__(self, term_str):
        self.TERM_PATTERN = r"20\d\d_\d\d_\d\d"
        term_str = term_str.replace("/", "")
        self.check_term(term_str)

        self.current_term = term_str
        self.set_next_term()
        self.set_last_term()

    @staticmethod
    def get_int_month(month_str):
        # 月を表す2文字の文字列（"04" 等）を整数（4 等）に変換
        # get_str_month()の逆

        assert len(month_str) == 2

        if month_str[0] == "0":
            month_str = month_str.replace("0", "")

        return int(month_str)

    @staticmethod
    def get_str_month(month_int):
        # 月を表す整数（4 等）を2文字の文字列（"04" 等）に変換
        # get_int_month()の逆

        assert 0 < month_int and month_int <= 12

        if month_int < 10:  # もし一桁なら
            return "0" + str(month_int)
        else:
            return str(month_int)

    def check_term(self, term_str):
        # 期間を表した文字列termを、正規表現を使ってフォーマットチェック

        # フォーマットチェックし、一致しなかった時はプログラム終了
        matches = re.findall(self.TERM_PATTERN, term_str)
        if len(matches) != 1:
            print("期間（term）のフォーマットが不正です")
            sys.exit()

        # 月が連続しない時（2022_04_06 など）の時もプログラム終了
        before_month = term_str.split("_")[1]
        after_month = term_str.split("_")[2]
        if (
            Terms.get_int_month(after_month) - Terms.get_int_month(before_month)
            != 1
        ):
            print("期間が1カ月間ではありません")
            sys.exit()

    def set_last_term(self):
        # 一個前の期間（2022_04_05⇒2022_03_04）を取得する

        info = self.current_term.split("_")
        year = info[0]
        before_month = Terms.get_int_month(info[1])
        after_month = Terms.get_int_month(info[2])

        assert before_month < after_month

        self.last_term = f"{year}_{Terms.get_str_month(before_month-1)}_{Terms.get_str_month(after_month-1)}"

    def set_next_term(self):
        # 次の期間（2022_04_05⇒2022_05_06）を取得

        info = self.current_term.split("_")
        year = info[0]
        before_month = Terms.get_int_month(info[1])
        after_month = Terms.get_int_month(info[2])

        assert before_month < after_month

        next_before_month = before_month + 1
        next_after_month = after_month + 1

        if next_before_month == 12 and next_after_month == 13:
            next_before_month == 0
            next_after_month = 1
            year = str(int(year) + 1)

        self.next_term = f"{year}_{Terms.get_str_month(next_before_month)}_{Terms.get_str_month(next_after_month)}"


class NumberFormatter:
    # 数字(int)をカンマ区切りして(strにして）返すクラス（10000⇒"10,000"）
    @staticmethod
    def get_formatted_number(number: int):
        str_number = str(number)

        reversed_number_list = list(reversed(str_number))
        return "".join(
            reversed(
                [
                    reversed_number_list[i] + ","
                    if (i + 1) % 3 == 1
                    and (1 + 1) != len(reversed_number_list)
                    and i != 0
                    and reversed_number_list[i] != "-"
                    else reversed_number_list[i]
                    for i in range(len(reversed_number_list))
                ]
            )
        )


if __name__ == "__main__":
    print(NumberFormatter.get_formatted_number(-34500))
