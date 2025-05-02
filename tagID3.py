import requests
from pytubefix import Playlist, YouTube
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class Id3():
    def __init__(sefl, file_dir, yt):
        sefl.file_dir = file_dir
        sefl.yt = yt
    def setMp3(self):

        # 縮圖圖片網址（可換成你要的）
        title = self.yt.title
        author = self.yt.author
        image_url = self.yt.thumbnail_url

        # 下載圖片
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("圖片下載失敗")

        image_data = response.content

        # 修改基本標籤
        audio_easy = EasyID3(self.file_dir)
        audio_easy["title"] = title
        audio_easy["artist"] = author
        audio_easy.save()

        # 加入封面圖（從 image_data）
        audio = MP3(self.file_dir, ID3=ID3)

        # 如果沒有 ID3 標籤就新增
        try:
            audio.add_tags()
        except error:
            pass

        # 刪除原封面圖
        audio.tags.delall("APIC")

        # 嘗試根據檔案副檔名推測 MIME 類型
        # 如果你知道格式是 PNG 可改成 'image/png'
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=image_data
            )
        )

        # 儲存變更
        audio.save()

