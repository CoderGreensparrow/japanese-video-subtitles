import whisper
from whisper.tokenizer import TO_LANGUAGE_CODE
import moviepy.editor as mpy
import subsy

def get_lines(audio_file, whisper_model, language=None) -> [[float, float, float, str], ...]:
    """
    Get lines with whisper.
    :param audio_file: The audio file to transcribe.
    :param whisper_model: The whisper model to use. Use whisper.available_models() to get the available models.
    :return: [[no_speech_prob, start, end, text], ...]
    """
    assert whisper_model in whisper.available_models()
    print("loading model...", end="")
    model = whisper.load_model(whisper_model)
    print("done.\ntranscribing...")
    result = model.transcribe(audio_file, verbose=True, language=language)
    print("returning...")
    return [[i["no_speech_prob"], i["start"], i["end"], i["text"]] for i in result["segments"]]

def check_if_video_or_audio(file):
    """
    Check a file's type.
    :param file: The file.
    :return: "video", "audio" or "unknown"
    """
    extension = file[file.rfind("."):]
    if extension in (".mp3", ".ogg", ".wav", ".3gp", ".aac", ".flac", ".m4a"):
        return "audio"
    elif extension in (".mp4", ".webm", ".mkv", ".flv", ".vob", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".m4p", ".mpg", ".mp2", ".m4v", ".3gp"):
        return "video"
    else:
        return "unknown"

def convert_video_to_audio(video_file):
    """
    Convert video to audio file.
    From mp4, mov or mkv to mp3.
    :param video_file: File.
    :return: New file
    """
    if check_if_video_or_audio(video_file) == "video":
        clip = mpy.VideoFileClip(video_file)
        new_file = video_file[:video_file.rfind(".")] + ".mp3"
        clip.audio.write_audiofile(new_file)
        return new_file
    else:
        raise ValueError("Not a video file (or unknown video file), will not convert to audio")

def create_subtitles_for_file(file, whisper_model="small", language=None):
    print("CHECKING TYPE...", end="")
    type = check_if_video_or_audio(file)
    if type == "unknown": raise ValueError("Unknown file type.")
    elif type == "video":
        print("TYPE IS VIDEO, CONVERTING...")
        file = convert_video_to_audio(file)
    print("GETTING TRANSCRIPTION...")
    result = get_lines(file, whisper_model, language=language)
    print("CREATING SUBTITLES...")
    new_subtitles = subsy.Subtitles()
    for i, line in enumerate(result):
        new_subtitle = subsy.Subtitle([line[3]], line[1]*1000, (line[2] - line[1])*1000, new_subtitles, i)
        print("new_subtitle: ", line[3], line[1], line[2] - line[1], new_subtitles, i, sep=", ")
        new_subtitles.subtitles.append(new_subtitle)
    new_subtitles_file = file[:file.rfind(".")] + ".ssa"
    print("SAVING...", end="")
    saving_done = False
    while not saving_done:
        try:
            new_subtitles.save(new_subtitles_file, "utf-8")
            saving_done = True
        except Exception as e:
            print("CAUGHT EXCEPTION!")
            print("MESSAGE:", e)
            input("PRESS ENTER TO RETRY SAVING...")
    print("DONE!\nDONE!")
    return new_subtitles_file

def basic_main():
    create_subtitles_for_file("【MV】いいわけバニー【ホロライブ-兎田ぺこら】.mp4", "large")

import tkinter
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
from tkinter import ttk
import multiprocessing
import time

class TkinterApp:
    def __init__(self):
        self.root = tkinter.Tk()
        self.rfrm = ttk.Frame(self.root)
        self.rfrm.grid(row=0, column=0)

        self.video_file_setup()
        self.model_select_setup()
        self.language_select_setup()
        self.generate_setup()

        self.root.mainloop()

    def video_file_setup(self):
        video_file_frm = ttk.Frame(self.rfrm)
        video_file_frm.grid(row=0, column=0)
        video_file_label = ttk.Label(video_file_frm, text="Select a video file:")
        video_file_label.grid(row=0, column=0)
        self.video_file = tkinter.StringVar(self.rfrm, "<Enter or click button>")
        video_file_entry = ttk.Entry(video_file_frm, textvariable=self.video_file)
        video_file_entry.grid(row=0, column=1)
        video_file_button = ttk.Button(video_file_frm, text="Select video file", command=self.video_file_chooser, takefocus=True)
        video_file_button.grid(row=0, column=2)

    def video_file_chooser(self):
        self.video_file.set(askopenfilename())

    def model_select_setup(self):
        model_select_frm = ttk.Frame(self.rfrm)
        model_select_frm.grid(row=1, column=0)
        model_select_label = ttk.Label(model_select_frm, text="Select a model:")
        model_select_label.grid(row=0, column=0)
        self.model_select = tkinter.StringVar(model_select_frm, "<Select>")
        model_select_combobox = ttk.Combobox(model_select_frm, values=whisper.available_models(),
                                             textvariable=self.model_select)
        model_select_combobox.grid(row=0, column=1)
        model_select_button = ttk.Button(model_select_frm, text="Select", command=self.model_select_language_select_state)
        model_select_button.grid(row=0, column=2)

    def model_select_language_select_state(self):
        if self.model_select.get().endswith(".en"):
            self.language_select_combobox.config(state="disabled")
            self.language_select.set("english")
        else:
            self.language_select_combobox.config(state="normal")

    def language_select_setup(self):
        language_select_frm = ttk.Frame(self.rfrm)
        language_select_frm.grid(row=2, column=0)
        language_select_label = ttk.Label(language_select_frm, text="Select language:")
        language_select_label.grid(row=0, column=0)
        self.language_select = tkinter.StringVar(language_select_frm, "auto-detect")
        self.language_select_combobox = ttk.Combobox(language_select_frm, values=["auto-detect", *TO_LANGUAGE_CODE.keys()],
                                                     textvariable=self.language_select)
        self.language_select_combobox.grid(row=0, column=1)

    def generate_setup(self):
        generate_frm = ttk.Frame(self.rfrm)
        generate_frm.grid(row=4, column=0)
        generate_button = ttk.Button(generate_frm, text="Generate subtitles", command=self.generate_subtitles)
        generate_button.grid(row=0, column=0)
        self.generate_progressbar_value = tkinter.DoubleVar(generate_frm, 0)
        self.generate_progressbar = ttk.Progressbar(generate_frm, variable=self.generate_progressbar_value)
        self.generate_progressbar.grid(row=1, column=0)

    def generate_subtitles(self):
        def generation_done():
            if not main_p.is_alive():
                self.generate_progressbar.stop()
                self.generate_progressbar_value.set(100)
                self.generate_progressbar.config(mode="determinate")
                showinfo("Transcription done", "The transcription is done. Thank you for using this software.\n"
                                               "And many thanks to OpenAI for making the usage of Whisper free.")
                self.generate_progressbar_value.set(0)
            else:
                self.root.after(25, generation_done)
        main_p = multiprocessing.Process(target=create_subtitles_for_file,
                                         args=(self.video_file.get(), self.model_select.get(),
                                               None if self.language_select.get() == "auto-detect" else TO_LANGUAGE_CODE[self.language_select.get()]))
        """create_subtitles_for_file(self.video_file.get(), self.model_select.get(),
                                  None if self.language_select.get() == "auto-detect" else TO_LANGUAGE_CODE[
                                      self.language_select.get()])"""
        main_p.start()
        self.generate_progressbar.config(mode="indeterminate")
        self.generate_progressbar.start(25)
        generation_done()

def main():
    TkinterApp()
if __name__=="__main__":
    main()