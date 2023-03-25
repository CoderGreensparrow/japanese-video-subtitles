# japanese-video-subtitles
Transcript videos with Whisper by OpenAI, add furigana and romaji with janome and jaconv and use translators to add translations too. Using subsy for manipulating the ssa subtitle files. And it can convert video to audio for Whisper with moviepy.

As you can see, some parts of this are pretty specific.

The transcription may differ in quality depending on the model used and the quality of the audio.
Also, the furigana part doesn't work that well sometimes.

# Setup

Install the following dependencies from PyPI:
* janome
* jaconv
* translators
* subsy
* openai-whisper
* moviepy

Install ffmpeg too and make sure it's accessible globally. (By setting to it in the PATH environment variable). It's for Whisper.

# Running

## Don't have subtitles

If you have a video that you don't have ANY japanese subtitles for, just run fan_friendly_japanese_transcription_for_ssa.py and enter details as it requests (I recommend the base or medium model if you're computer's not that good).

## Have only japanese subtitles

Look for the markup_subtitle_file_ssa function in furigana_romaji_translation_for_ssa.py. Run the file through it.
