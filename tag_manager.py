from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def get_tags(file_path):
    try:
        return EasyID3(file_path)
    except Exception:
        return {}

def save_tags(file_path, title, artist, cover_path=None):
    audio = MP3(file_path, ID3=ID3)
    try:
        audio.add_tags()
    except:
        pass
    audio["title"] = title
    audio["artist"] = artist
    audio.save()

    if cover_path:
        with open(cover_path, "rb") as img:
            audio.tags.add(APIC(mime="image/jpeg", type=3, desc=u"Cover", data=img.read()))
        audio.save()
