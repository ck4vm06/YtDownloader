import time

from moviepy.editor import VideoFileClip, AudioFileClip
from pytubefix import Playlist, YouTube
from proglog import ProgressBarLogger
import multiprocessing
import os
import threading

class YtDownloader():
    def __init__(self, Yt_url, save_path, file_ext, information_update,progress_bar_update , download_finish):
        self.Yt_url = Yt_url
        self.save_path = save_path
        self.file_ext = file_ext.split()# (quality type pack_speed) be like (1080p mp4 fast)
        self.information_update = information_update
        self.progress_bar_update = progress_bar_update
        self.download_finish = download_finish

        self.stop_event = threading.Event()

        self.info_pack = {'counter': '', #(6/9)
                          'title': '', #song name
                          'state': '', #Downloading/Converting
                          'type': ''} #audio/video/mp3/mp4

    def start(self):
        if 'playlist' in self.Yt_url:
            video_urls = Playlist(self.Yt_url).video_urls
            self.__download_manager(video_urls)
        else:
            video_url = [self.Yt_url]
            self.__download_manager(video_url)
    def stop_set(self):
        self.stop_event.set()

    def stop(self):
        self.information_update("Download stopped!")
        self.download_finish()

    def __download_manager(self, video_urls):
        print(video_urls)
        playlist_quantity = len(video_urls)
        for count, video_url in enumerate(video_urls, start=1):
            if self.stop_event.is_set():
                self.stop()
                return
            yt = YouTube(video_url, on_progress_callback=self.register_on_progress_callback)

            self.info_pack['title'] = yt.title
            self.info_pack['counter'] = f'({count}/{playlist_quantity})'
            self.information_updater()

            if 'mp3' in self.file_ext:
                download_state = self.get_mp3(yt)
            elif 'mp4' in self.file_ext:
                download_state = self.get_mp4(yt)
            else:
                download_state = 'Error >>> extension not supported'
            if download_state:
                self.information_update(download_state)
                time.sleep(2)


        if not self.stop_event.is_set():
            self.information_update('Download Completed!')
        self.download_finish()


    def register_on_progress_callback(self, stream, chunk, remains):
        self.progress_bar_update((stream.filesize - remains) / stream.filesize * 100)
        if self.stop_event.is_set():
            raise StopException("Download stopped by user.")
    def information_updater(self):
        i = self.info_pack
        self.information_update(f'{i['counter']}{i['title']}\n{i['state']}>>>{i['type']}')


    def get_mp3(self, yt):
        try:
            if os.path.exists(f'{os.path.join(self.save_path, yt.title)}.mp3'):
                return f'{yt.title}\nalready exist'

            abr = self.file_ext[0] if self.file_ext[0] else '160kbps'
            audio_file = self.__get_audio(yt, abr)
            if audio_file == None:
                return 'Error >>> audio_file is None'
            elif audio_file.startswith('Error'):
                return audio_file

            # to mp3
            self.info_pack['state'] = 'Reading'
            self.info_pack['type'] = 'mp3'
            self.information_updater()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            out_file_name = os.path.join(self.save_path, f'{yt.title}.mp3')
            file_name, file_ext = os.path.splitext(audio_file)
            if file_ext == '.mp3':
                os.rename(audio_file, out_file_name)
            else:
                audio_clip = AudioFileClip(audio_file)
                audio_clip.write_audiofile(out_file_name,
                                           bitrate=abr.replace('bps', ''),
                                           logger=MoviepyBarLogger(self))
                os.remove(audio_file)
            return 0
        except StopException:
            print('stop test')
            self.stop()
        except Exception as e:
            return f'Error >>> {e}'

    def __get_audio(self, yt, abr):

        self.info_pack['state'] = 'Downloading'
        self.info_pack['type'] = 'audio resource'
        self.information_updater()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        try:
            #find stream
            stream = yt.streams.filter(adaptive=True, type='audio',
                                       abr=abr).order_by('abr').desc().first()
            if not stream:
                stream = yt.streams.filter(adaptive=True, type='audio',
                                           ).order_by('abr').desc().first()
            print(stream)
            audio_file = stream.download(output_path=self.save_path,
                                       filename=f'{stream.title}(ProcessingAudio).{stream.subtype}')
            return audio_file
        except StopException:
            print('stop test')
            self.stop()
        except Exception as e:
            print(e)
            return f'Error >>> {e}'


    def get_mp4(self, yt):
        try:
            if os.path.exists(f'{os.path.join(self.save_path, yt.title)}.mp4'):
                return f'{yt.title}\nalready exist'

            quality = self.file_ext[0].split('p')
            res = None if (quality[0] == '') else quality[0]+'p'
            fps = None if (quality[1] == '') else quality[1]

            abr = '160kbps'
            audio_file = self.__get_audio(yt, abr)
            if audio_file == None:
                return 'Error >>> audio_file is None'
            elif audio_file.startswith('Error'):
                return audio_file

            video_file = self.__get_video(yt, res, fps)
            if video_file == None:
                return 'Error >>> video_file is None'
            elif video_file.startswith('Error') or video_file == None:
                return video_file

            # pack_speed = self.file_ext[2] if len(self.file_ext) > 2 else None # 確認使否指定壓縮速率

            self.info_pack['state'] = 'Reading'
            self.info_pack['type'] = 'mp4'
            self.information_updater()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            out_file_name = os.path.join(self.save_path, f'{yt.title}.mp4')
            audio = AudioFileClip(audio_file)
            video = VideoFileClip(video_file)
            final_video = video.set_audio(audio)
            final_video.write_videofile(out_file_name,
                                        codec="libx264",
                                        audio_codec="aac",
                                        audio_bitrate='160k',
                                        preset='fast',
                                        logger=MoviepyBarLogger(self),
                                        threads=multiprocessing.cpu_count()
                                        )
            os.remove(audio_file)
            os.remove(video_file)
            return 0
        except StopException:
            print('stop test')
            self.stop()
        except Exception as e:
            return f'Error >>> {e}'



    def __get_video(self, yt, res, fps):
        res_list = ['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']

        self.info_pack['state'] = 'Downloading'
        self.info_pack['type'] = 'video resource'
        self.information_updater()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        print(res)
        if res not in res_list:
            res = res_list[2]
        try:
            for res_try in res_list[res_list.index(res):]:
                stream = yt.streams.filter(adaptive=True, type='video',
                                           res=res_try, fps=fps).desc().first()
                if not stream:
                    stream = yt.streams.filter(adaptive=True, type='video',
                                               res=res_try).desc().first()
                if stream:
                    print(stream)
                    video_file = stream.download(output_path=self.save_path,
                                               filename=f'{stream.title}(ProcessingVideo).{stream.subtype}')
                    break
            return video_file
        except StopException:
            print('stop test')
            self.stop()
        except Exception as e:
            print(e)
            return f'Error >>> {e}' #回傳下載時的錯誤

class MoviepyBarLogger(ProgressBarLogger):
    def __init__(self, outer_instance):
        super().__init__()
        self.outer_instance = outer_instance
    def bars_callback(self, bar, attr, value, old_value=None):
        self.outer_instance.progress_bar_update(int((value / self.bars[bar]['total']) * 100))
        if bar == 't' and value == 0:
            self.outer_instance.info_pack['state'] = 'Converting Video'
            self.outer_instance.information_updater()
        elif bar == 'chunk' and value == 0:
            self.outer_instance.info_pack['state'] = 'Converting Audio'
            self.outer_instance.information_updater()
        if self.outer_instance.stop_event.is_set():
            raise StopException("Download stopped by user.")

class StopException(Exception):
    pass
