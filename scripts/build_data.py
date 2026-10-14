#!/usr/bin/env python3
"""Generate web/data/<lang>.json from a language folder's markdown.

Markdown is the human source of truth (readable, diffable). The web UI reads
JSON. Run this after editing a language folder's markdown:

    python3 scripts/build_data.py zh-tw

Writes web/data/<lang>.json (vocab + grammar patterns). For Chinese folders,
Zhuyin (Bopomofo) is derived from the pinyin, so it never has to be typed by
hand and stays correct as the list grows.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# Pinyin -> Zhuyin (Bopomofo)
# --------------------------------------------------------------------------- #
VOWEL_TONE = {
    "ā": ("a", 1), "á": ("a", 2), "ǎ": ("a", 3), "à": ("a", 4),
    "ē": ("e", 1), "é": ("e", 2), "ě": ("e", 3), "è": ("e", 4),
    "ī": ("i", 1), "í": ("i", 2), "ǐ": ("i", 3), "ì": ("i", 4),
    "ō": ("o", 1), "ó": ("o", 2), "ǒ": ("o", 3), "ò": ("o", 4),
    "ū": ("u", 1), "ú": ("u", 2), "ǔ": ("u", 3), "ù": ("u", 4),
    "ǖ": ("ü", 1), "ǘ": ("ü", 2), "ǚ": ("ü", 3), "ǜ": ("ü", 4),
    "ü": ("ü", 0),
}
TONE_MARK = {1: "", 2: "ˊ", 3: "ˇ", 4: "ˋ"}

INITIALS = ["zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l",
            "g", "k", "h", "j", "q", "x", "r", "z", "c", "s"]
INITIAL_MAP = {
    "b": "ㄅ", "p": "ㄆ", "m": "ㄇ", "f": "ㄈ", "d": "ㄉ", "t": "ㄊ",
    "n": "ㄋ", "l": "ㄌ", "g": "ㄍ", "k": "ㄎ", "h": "ㄏ", "j": "ㄐ",
    "q": "ㄑ", "x": "ㄒ", "zh": "ㄓ", "ch": "ㄔ", "sh": "ㄕ", "r": "ㄖ",
    "z": "ㄗ", "c": "ㄘ", "s": "ㄙ", "": "",
}
FINALS = {
    "a": "ㄚ", "o": "ㄛ", "e": "ㄜ", "ai": "ㄞ", "ei": "ㄟ", "ao": "ㄠ",
    "ou": "ㄡ", "an": "ㄢ", "en": "ㄣ", "ang": "ㄤ", "eng": "ㄥ", "er": "ㄦ",
    "i": "ㄧ", "ia": "ㄧㄚ", "ie": "ㄧㄝ", "iao": "ㄧㄠ", "iu": "ㄧㄡ",
    "ian": "ㄧㄢ", "in": "ㄧㄣ", "iang": "ㄧㄤ", "ing": "ㄧㄥ", "iong": "ㄩㄥ",
    "u": "ㄨ", "ua": "ㄨㄚ", "uo": "ㄨㄛ", "uai": "ㄨㄞ", "ui": "ㄨㄟ",
    "uan": "ㄨㄢ", "un": "ㄨㄣ", "uang": "ㄨㄤ", "ong": "ㄨㄥ",
    "ü": "ㄩ", "üe": "ㄩㄝ", "üan": "ㄩㄢ", "ün": "ㄩㄣ",
    "": "",
}
Y_FORMS = {
    "yi": "i", "ya": "ia", "ye": "ie", "yao": "iao", "you": "iu",
    "yan": "ian", "yin": "in", "yang": "iang", "ying": "ing", "yong": "iong",
    "yu": "ü", "yue": "üe", "yuan": "üan", "yun": "ün",
}
W_FORMS = {
    "wu": "u", "wa": "ua", "wo": "uo", "wai": "uai", "wei": "ui",
    "wan": "uan", "wen": "un", "wang": "uang", "weng": "ong",
}
# Base syllables (no tone) used to segment multi-syllable pinyin.
SYLLABLES = set("""
a o e ai ei ao ou an en ang eng er
ba bo bai bei bao ban ben bang beng bi bie biao bian bin bing bu
pa po pai pei pao pou pan pen pang peng pi pie piao pian pin ping pu
ma mo me mai mei mao mou man men mang meng mi mie miao miu mian min ming mu
fa fo fei fou fan fen fang feng fu
da de dai dei dao dou dan den dang deng di die diao diu dian ding dong du duo dui duan dun
ta te tai tao tou tan tang teng ti tie tiao tian ting tong tu tuo tui tuan tun
na ne nai nei nao nou nan nen nang neng ni nie niao niu nian nin niang ning nong nu nuo nuan nü nüe
la lo le lai lei lao lou lan lang leng li lia lie liao liu lian lin liang ling long lu luo luan lun lü lüe
ga ge gai gei gao gou gan gen gang geng gong gu gua guo guai gui guan gun guang
ka ke kai kei kao kou kan ken kang keng kong ku kua kuo kuai kui kuan kun kuang
ha he hai hei hao hou han hen hang heng hong hu hua huo huai hui huan hun huang
ji jia jie jiao jiu jian jin jiang jing jiong ju jue juan jun
qi qia qie qiao qiu qian qin qiang qing qiong qu que quan qun
xi xia xie xiao xiu xian xin xiang xing xiong xu xue xuan xun
zha zhe zhi zhai zhei zhao zhou zhan zhen zhang zheng zhong zhu zhua zhuo zhuai zhui zhuan zhun zhuang
cha che chi chai chao chou chan chen chang cheng chong chu chua chuo chuai chui chuan chun chuang
sha she shi shai shei shao shou shan shen shang sheng shu shua shuo shuai shui shuan shun shuang
re ri rao rou ran ren rang reng rong ru rua ruo rui ruan run
za ze zi zai zei zao zou zan zen zang zeng zong zu zuo zui zuan zun
ca ce ci cai cao cou can cen cang ceng cong cu cuo cui cuan cun
sa se si sai sao sou san sen sang seng song su suo sui suan sun
ya ye yao you yan yin yang ying yong yi
wa wo wai wei wan wen wang weng wu
yu yue yuan yun
""".split())


def split_syllables(base: str):
    """Greedy longest-match segmentation of unmarked pinyin into syllables."""
    out, i, n = [], 0, len(base)
    while i < n:
        for L in range(min(6, n - i), 0, -1):
            if base[i:i + L] in SYLLABLES:
                out.append(base[i:i + L])
                i += L
                break
        else:
            out.append(base[i])
            i += 1
    return out


def zhuyin_syllable(syl: str, tone: int) -> str:
    if syl in Y_FORMS:
        ini, fin = "", Y_FORMS[syl]
    elif syl in W_FORMS:
        ini, fin = "", W_FORMS[syl]
    else:
        ini = next((c for c in INITIALS if syl.startswith(c)), "")
        rest = syl[len(ini):]
        if ini in ("zh", "ch", "sh", "r", "z", "c", "s") and rest == "i":
            fin = ""
        elif ini in ("j", "q", "x") and rest.startswith("u"):
            fin = "ü" + rest[1:]
        else:
            fin = rest
    if fin not in FINALS:
        return "?" + syl
    z = INITIAL_MAP.get(ini, "") + FINALS[fin]
    if tone == 5 or tone == 0:
        return "˙" + z
    return z + TONE_MARK.get(tone, "")


def syllable_parts(py: str):
    """Split tone-marked pinyin into syllables; returns [{py, zh, tone}].

    tone: 1-4, or 5 for neutral. Positions align 1:1 with the base string, so
    the original pinyin can be sliced back out.
    """
    if not py:
        return []
    tone_at, chars, orig = {}, [], []
    for ch in py:
        if ch == " ":
            continue
        if ch in VOWEL_TONE:
            b, t = VOWEL_TONE[ch]
            tone_at[len(chars)] = t
            chars.append(b)
        else:
            chars.append(ch)
        orig.append(ch)
    base = "".join(chars)
    parts, idx = [], 0
    for syl in split_syllables(base):
        start, end = idx, idx + len(syl)
        idx = end
        tone = next((tone_at[i] for i in range(start, end) if i in tone_at), 5)
        parts.append({
            "py": "".join(orig[start:end]),
            "zh": zhuyin_syllable(syl, tone),
            "tone": tone,
        })
    return parts


def pinyin_to_zhuyin(py: str) -> str:
    """Convert a tone-marked pinyin word (maybe several syllables) to Zhuyin."""
    return " ".join(p["zh"] for p in syllable_parts(py))


# --------------------------------------------------------------------------- #
# Markdown parsing
# --------------------------------------------------------------------------- #
def parse_vocab(md: str):
    rows = []
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        pinyin = cells[2]
        parts = syllable_parts(pinyin)
        rows.append({
            "rank": int(cells[0]),
            "word": cells[1],
            "pinyin": pinyin,
            "zhuyin": " ".join(p["zh"] for p in parts),
            "pinyinParts": [{"text": p["py"], "tone": p["tone"]} for p in parts],
            "zhuyinParts": [{"text": p["zh"], "tone": p["tone"]} for p in parts],
            "meaning": cells[3],
            "example": cells[4],
        })
    return rows


def parse_patterns(md: str):
    patterns = []
    blocks = re.split(r"^###\s+", md, flags=re.M)[1:]
    for block in blocks:
        lines = block.splitlines()
        header = lines[0].strip()
        m = re.match(r"(\d+)\.\s+(.*)", header)
        num = int(m.group(1)) if m else len(patterns) + 1
        name = m.group(2).strip() if m else header
        does = structure = ""
        examples, in_examples = [], False
        for ln in lines[1:]:
            if "**Examples:**" in ln:
                in_examples = True
                continue
            if "**Status:**" in ln:
                in_examples = False
                continue
            d = re.search(r"\*\*Does:\*\*\s*(.+)", ln)
            if d:
                does = d.group(1).strip()
                continue
            st = re.search(r"\*\*Structure:\*\*\s*(.+)", ln)
            if st:
                structure = st.group(1).strip()
                continue
            if in_examples and re.match(r"^\s+-\s+", ln):
                examples.append(re.sub(r"^\s+-\s+", "", ln).strip())
        patterns.append({"n": num, "name": name, "does": does,
                         "structure": structure, "examples": examples})
    return patterns


def parse_zhuyin(md: str):
    """Parse '### <group>' sections; each may have a symbol table and/or bullets."""
    groups = []
    cur = None
    for line in md.splitlines():
        h = re.match(r"^###\s+(.*)", line.strip())
        if h:
            cur = {"name": h.group(1).strip(), "symbols": [], "bullets": []}
            groups.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 2 and "---" not in cells[0] and cells[0] not in ("Symbol",):
                cur["symbols"].append({"symbol": cells[0], "pinyin": cells[1],
                                       "note": cells[2] if len(cells) > 2 else ""})
        elif s.startswith("- "):
            cur["bullets"].append(s[2:].replace("**", "").strip())
    return [g for g in groups if g["symbols"] or g["bullets"]]


def build(lang: str):
    folder = ROOT / lang
    if not folder.is_dir():
        sys.exit(f"no such language folder: {lang}")

    vocab = parse_vocab((folder / "vocab-frequency.md").read_text(encoding="utf-8"))
    patterns = parse_patterns((folder / "grammar-patterns.md").read_text(encoding="utf-8"))
    readme = (folder / "README.md").read_text(encoding="utf-8")
    title = readme.splitlines()[0].lstrip("# ").strip()

    zh = folder / "zhuyin.md"
    data = {
        "language": lang,
        "title": title,
        "vocab": vocab,
        "patterns": patterns,
        "zhuyin": parse_zhuyin(zh.read_text(encoding="utf-8")) if zh.exists() else [],
    }

    bad = [v["word"] for v in vocab if "?" in v["zhuyin"]]
    if bad:
        print(f"WARNING: could not convert {len(bad)}: {bad}", file=sys.stderr)

    out_dir = ROOT / "web" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    avail = sorted(p.stem for p in out_dir.glob("*.json") if p.stem != "index")
    (out_dir / "index.json").write_text(json.dumps({"languages": avail}, indent=1), encoding="utf-8")

    print(f"wrote web/data/{lang}.json: {len(vocab)} words, {len(patterns)} patterns, "
          f"{len(data['zhuyin'])} zhuyin groups")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "zh-tw")
