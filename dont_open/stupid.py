from pydub import AudioSegment
from pydub.playback import play

def on_win(play):
    if play:
        audio = AudioSegment.from_file("example.mp3")
        play(audio)