import time

from janome.tokenizer import Tokenizer
from jaconv import kata2hira, kata2alphabet, alphabet2kana
import translators as ts
import subsy

def get_furigana_romaji(line: str):
    t = Tokenizer()
    furigana = {}
    romaji = []
    for token in t.tokenize(line):
        original = token.node.node_label()
        if token.extra:
            katakana = token.extra[4]
        else:
            katakana = alphabet2kana(original)
        # FURIGANA
        """original = hira2kata(original)  # Since original and katakana will be looked at, I have to make sure these both use katakana (kinda like making everything the same case)
        i_original = 0
        current_kanji_part = ""  # can contain multiple kanji
        for char in katakana:
            if original[i_original] != char:
                current_kanji"""
        if original != kata2hira(katakana):
            furigana.update({original: kata2hira(katakana)})
        # ROMAJI
        romaji.append(kata2alphabet(katakana))
    return furigana, romaji

def markup_subtitle_for_ssa(subtitle: str, do_furigana=True, do_romaji=False, do_translation=False, base_size=50, font="Noto Sans JP", *, translate_service="google"):
    subtitle_lines = subtitle.replace("\\N", "\n").replace("\\n", "\n").split("\n")
    furigana, romaji = get_furigana_romaji("　".join(subtitle_lines))
    parts = {
        "start": "{\\fn" + font + "}",
        "translation_start": "\\N{\\fs" + str(base_size // 1.5) + "}",
        "translation_newline": "\\n",
        "translation_end": "\\N",
        "romaji_start": "\\N{\\fs" + str(base_size // 1.5) + "}",
        "romaji_end": "\\N",
        "furigana_start": "\\N{\\fs" + str(base_size // 2) + "}",
        "furigana_end": "\\N{\\fs" + str(base_size) + "}"
    }
    # NEW SUBTITLE
    new_subtitle = parts["start"]
    if do_translation:
        new_subtitle += parts["translation_start"]
        for i, line in enumerate(subtitle_lines):
            if line != "":
                try:
                    new_subtitle += ts.translate_text(line, translate_service, "ja", "en")
                except Exception as e:
                    print("ERROR:", e)
                    new_subtitle += ""
            else:
                new_subtitle += ""
            if i + 1 != len(subtitle_lines):
                new_subtitle += parts["translation_newline"]
        new_subtitle += parts["translation_end"]
    if do_romaji:
        new_subtitle += parts["romaji_start"]
        new_subtitle += " ".join(romaji)
        new_subtitle = new_subtitle.replace(" 　 ", "  ").replace("   ", "  ")
        new_subtitle += parts["romaji_end"]
    if do_furigana:
        for line in subtitle_lines:
            new_subtitle += parts["furigana_start"]
            # find the parts given by the get_furigana_romaji function (positions of part -> hiragana)
            furigana_parts = []
            for kanji, hiragana in furigana.items():
                start_index = 0
                index = 0
                while index != -1:
                    index = line.find(kanji, start_index)
                    start_index = index + 1
                    if index != -1:
                        furigana_parts.append([index, index + len(kanji), hiragana])
            # sort them by index
            furigana_parts = sorted(furigana_parts)
            # if there is any, make the furigana line
            if furigana_parts:
                furigana_line = ""
                for i in range(len(furigana_parts) + 1):
                    prev = furigana_parts[i-1] if i-1 > -1 else [0, 0, ""]
                    current = furigana_parts[i] if i < len(furigana_parts) else [len(line), len(line), ""]
                    # find the "middle distance"
                    middle_distance = ((current[1] + current[0]) / 2) - ((prev[1] + prev[0]) / 2)
                    # adjust, so it's correct for number of spaces / 2 (would be too long to explain here maybe)
                    end_to_end_distance = middle_distance - len(prev[2]) / 4 - len(current[2]) / 4
                    # append the calculated number of full width spaces * 2 and the current furigana
                    furigana_line += "　" * int(end_to_end_distance * 2) + current[2]
                    # TODO: Support some not full width characters, eg. space, exclamation mark etc.
                new_subtitle += furigana_line
            new_subtitle += parts["furigana_end"]
            new_subtitle += line
    else:
        new_subtitle += new_subtitle
    new_subtitle = new_subtitle.replace("\\N\\N", "\\N")\
                               .replace("\\n\\n", "\\n")\
                               .replace("{\\fn" + font + "}\\N", "{\\fn" + font + "}", 1)
    return new_subtitle

def markup_subtitle_file_ssa(file, output_file=None, furigana=True, romaji=False, translation=False, base_font_size=20, font="Noto Sans JP", translate_service="google"):
    subtitles = subsy.load(file)
    new_subtitles = subsy.Subtitles()
    for i, subtitle in enumerate(subtitles):
        new_subtitle = subsy.Subtitle(None, subtitle.start, subtitle.duration, new_subtitles)
        new_subtitle.text = markup_subtitle_for_ssa(subtitle.plain, furigana, romaji, translation, base_font_size, font, translate_service=translate_service)
        new_subtitles.subtitles.append(new_subtitle)
        print("\r", (i / (len(subtitles) - 1)) * 100, "% DONE", sep="", end="")
    if output_file:
        new_subtitles.save(output_file)
    else:
        new_subtitles.save(file + "_markup_" + str(time.time()) + file[file.rfind("."):])
    print("DONE!")

def main():
    markup_subtitle_file_ssa("tore 1.ssa", None, False, True, True, translate_service="bing")
if __name__ == '__main__':
    main()