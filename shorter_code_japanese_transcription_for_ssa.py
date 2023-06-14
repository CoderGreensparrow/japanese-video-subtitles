from whisper import available_models
from transcript_video_for_ssa import create_subtitles_for_file
from furigana_romaji_translation_for_ssa import markup_subtitle_file_ssa

file = input("Filename: ")
print("Models:", *[str(i) for i in available_models()], sep="\n")
model = ""
while model not in available_models():
    model = input("Please choose a model: ")
new_subtitles = create_subtitles_for_file(file, model, "japanese")
markup_subtitle_file_ssa(new_subtitles, None, True, True, True, translate_service="bing")