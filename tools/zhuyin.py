# /// script
# dependencies = ["pypinyin"]
# ///
"""掃描 index.html 裡所有中文，產生注音對照表，寫回 /*ZY-START*/ ... /*ZY-END*/ 之間。

用法：uv run tools/zhuyin.py
pypinyin 用的是大陸讀音，台灣教育部讀音不同的字放在 CHAR / PHRASE 修正。
"""
import json
import pathlib
import re
from collections import Counter, defaultdict

from pypinyin import Style, pinyin

HTML = pathlib.Path(__file__).resolve().parent.parent / "index.html"
START, END = "/*ZY-START*/", "/*ZY-END*/"
CJK = re.compile(r"[一-鿿]+")

# 單字修正（台灣讀音）
CHAR = {
    "擊": "ㄐㄧˊ", "危": "ㄨㄟˊ", "誰": "ㄕㄟˊ", "期": "ㄑㄧˊ", "微": "ㄨㄟˊ",
    "息": "ㄒㄧˊ", "暫": "ㄓㄢˋ", "綜": "ㄗㄨㄥˋ",
    # 低年級課本標本調，不標變調
    "一": "ㄧ", "不": "ㄅㄨˋ",
    # 連接詞「和」課本標ㄏㄢˋ；「站著、看著」的著是輕聲
    "和": "ㄏㄢˋ", "著": "˙ㄓㄜ",
}
# 詞語修正：詞 -> 每字注音
PHRASE = {
    "著急": ["ㄓㄠˊ", "ㄐㄧˊ"],
    "什麼": ["ㄕㄣˊ", "˙ㄇㄜ"],
}


def convert(run: str) -> list[str]:
    syl = [p[0] for p in pinyin(run, style=Style.BOPOMOFO)]
    if len(syl) != len(run):  # 保險：逐字轉
        syl = [pinyin(c, style=Style.BOPOMOFO)[0][0] for c in run]
    syl = [CHAR.get(c, s) for c, s in zip(run, syl)]
    # 「看得清楚、飛得好遠」的得是輕聲；「得分」才唸ㄉㄜˊ
    syl = ["˙ㄉㄜ" if c == "得" and run[i + 1:i + 2] != "分" else s
           for i, (c, s) in enumerate(zip(run, syl))]
    for word, fix in PHRASE.items():
        for m in re.finditer(word, run):
            syl[m.start():m.end()] = fix
    # 輕聲符號統一放最前面（直排時在最上方）
    return [("˙" + s.replace("˙", "")) if "˙" in s else s for s in syl]


def main() -> None:
    src = HTML.read_text("utf-8")
    a, b = src.index(START), src.index(END)
    body = src[:a] + src[b:]
    runs = sorted(set(CJK.findall(body)))
    table: dict[str, str] = {}
    votes: dict[str, Counter] = defaultdict(Counter)
    for run in runs:
        syl = convert(run)
        table[run] = " ".join(syl)
        for c, s in zip(run, syl):
            votes[c][s] += 1
    chars = {c: v.most_common(1)[0][0] for c, v in votes.items()}
    data = json.dumps({"r": table, "c": chars}, ensure_ascii=False, separators=(",", ":"))
    HTML.write_text(src[:a] + START + f"const ZY={data};" + src[b:], "utf-8")
    print(f"{len(runs)} 段、{len(chars)} 個字")
    for c, v in sorted(votes.items()):
        if len(v) > 1:
            print("多音：", c, dict(v))


if __name__ == "__main__":
    main()
