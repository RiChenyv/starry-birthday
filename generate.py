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


def default_letter(name):
    return (
        "见字如面。",
        "有些祝福适合当面说，有些更适合写下来，交给一小片安静的星光保管。今晚，想把这段话送给你。",
        "新的一岁，不急着成为多厉害的人。愿你在每一个普通的日子里，都能照顾好自己：累了就停一停，开心就大声笑，遇见喜欢的风景，记得多看一会儿。",
        "如果偶尔觉得世界有些嘈杂，就抬头看看星星。今晚它们为你亮着；往后也会有很多个这样的夜晚，安静地陪你走一段路。",
        "作为你的朋友，很开心能在你的宇宙里留下一个小小的坐标。愿你自由、明亮，也永远拥有被朋友认真惦记的底气。",
        f"生日快乐，{name}。",
    )


def read_letter(name):
    print(f"\n默认信件预览\n\n{name}：\n")
    print("\n\n".join(default_letter(name)))
    print("\n[1] 保留默认正文（直接回车）  [2] 自定义正文")
    while True:
        try:
            choice = input("请选择：").strip()
        except EOFError:
            return None
        if choice in ("", "1"):
            return None
        if choice == "2":
            break
        print("请输入 1 或 2。")

    print("请逐行输入正文，每行一段。单独输入 /结束 并回车完成。")
    lines = []
    while True:
        line = input().strip()
        if line == "/结束":
            if lines:
                return lines
            print("请至少输入一段正文。")
        elif line:
            lines.append(line)


def generate(name, birthday, letter=None):
    month_day = f"{birthday.month:02d}.{birthday.day:02d}"
    year = f"{birthday.year:04d}"
    paragraphs = [f"<p>{escape(text)}</p>" for text in (default_letter(name) if letter is None else letter)]
    if letter is None:
        paragraphs[-1] = paragraphs[-1].replace("<p>", '<p class="letter-last">', 1)
    values = {
        "NAME": escape(name),
        # Escape '<' so a name cannot close the surrounding script element.
        "NAME_JSON": json.dumps(name, ensure_ascii=True).replace("<", r"\u003c"),
        "LETTER_BODY": "\n          ".join(paragraphs),
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
        letter = read_letter(name) if args.name is None else None
    except (EOFError, KeyboardInterrupt):
        parser.exit(1, "\n已取消生成。\n")

    try:
        markup = generate(name, birthday, letter)
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
