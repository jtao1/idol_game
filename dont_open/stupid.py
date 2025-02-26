from pydub import AudioSegment
from pydub.playback import play

def on_win():
    audio = AudioSegment.from_file("example.mp3")
    play(audio)