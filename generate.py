"""Generate an offline birthday page from template.html."""

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "dist" / "星河生日礼物.html"
MONTHS = (
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
)
TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")


def generate(name, birthday):
    month_day = f"{birthday.month:02d}.{birthday.day:02d}"
    year = f"{birthday.year:04d}"
    values = {
        "NAME": escape(name),
        # Escape '<' so a name cannot close the surrounding script element.
        "NAME_JSON": json.dumps(name, ensure_ascii=True).replace("<", r"\u003c"),
        "DATE_ISO": birthday.isoformat(),
        "DATE_SHORT": month_day,
        "DATE_DOTTED": f"{year}.{month_day}",
        "DATE_SLASH": f"{birthday.month:02d} / {birthday.day:02d} / {year}",
        "DATE_ENGLISH": f"{MONTHS[birthday.month - 1]} {birthday.day}",
        "DATE_CHINESE": f"{birthday.year} 年 {birthday.month} 月 {birthday.day} 日",
        "YEAR": year,
    }
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    return TOKEN.sub(lambda match: values[match[1]], template)


def main():
    parser = argparse.ArgumentParser(description="生成可离线打开的星河生日礼物。")
    parser.add_argument("name", nargs="?", help="收件人姓名")
    parser.add_argument("date", nargs="?", help="庆祝日期，格式为 YYYY-MM-DD")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                        help="输出路径，默认 dist/星河生日礼物.html")
    args = parser.parse_args()

    if (args.name is None) != (args.date is None):
        parser.error("请同时提供姓名和日期，或直接运行脚本按提示输入。")
    try:
        name = (input("收件人姓名：") if args.name is None else args.name).strip()
        date_text = (input("庆祝日期（YYYY-MM-DD）：") if args.date is None else args.date).strip()
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\n已取消生成。\n")

    if not name or any(ord(character) < 32 for character in name):
        parser.error("姓名须为非空的单行文本。")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date_text):
            raise ValueError
        birthday = date.fromisoformat(date_text)
    except ValueError:
        parser.error("请输入有效日期，格式为 YYYY-MM-DD，例如 2027-08-19。")

    try:
        markup = generate(name, birthday)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(markup)
    except FileExistsError:
        parser.exit(1, "输出位置已存在，请用 --output 指定其他文件路径。\n")
    except OSError as error:
        parser.exit(1, f"生成失败：{error}\n")
    print(f"已生成 {args.output.resolve()}")


if __name__ == "__main__":
    main()
