import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import ytdl
from pytubefix import Playlist, YouTube

bg = '#1a1a1a'
fg = 'white'
itbg = '#404040'
Yt_URL = 'unknown'
save_path = 'unknown'
file_ext = 'unknown' # mp3 mp4
download_type = 'unknown' # 'list' or 'solo'

def progress_bar_update(progress: int):
    progress_bar['value'] = progress
def information_update(info: str):
    information.config(text=info)
    app.update_idletasks()

def url_check():
    url = url_en.get()
    global download_type
    global Yt_URL
    if 'playlist' in url:
        try:
            playlist = Playlist(url)
            information_update(f'[{playlist.title}] is a playlist')
            Yt_URL = url
            download_type = 'list'
            return True
        except Exception as e:
            information_update(f'URL error:{e}')
            return False
    else:
        try:
            yt = YouTube(url)
            information_update(f'[{yt.title}] is a video')
            Yt_URL = url
            download_type = 'solo'
            return True
        except Exception as e:
            information_update(f'URL error:{e}')
            return False
def path_check():
    path = path_en.get()
    if not os.path.exists(path):
        information_update("Folder not found")
        return False
    else:
        global save_path
        save_path = path
        return True
def ext_check():
    ext = combo_box.get().lower().split()
    global file_ext
    if ext[1] == 'mp3':
        file_ext = combo_box.get().lower()
        return True
    elif ext[1] == 'mp4':
        file_ext = combo_box.get().lower()
        return True
    else:
        information_update('Choose mp3 or mp4')
        return False

def set_url():
    url_en.delete(0, tk.END)
    url_en.insert(0, app.clipboard_get())

def set_path():
    path_en.delete(0, tk.END)
    path_en.insert(0, filedialog.askdirectory())

def ui_state(is_running: bool):
    states = {
        'idle_ui': 'normal' if is_running else 'disabled',
        'runing_ui': 'normal' if not is_running else 'disabled'
    }
    url_en.config(state=states['idle_ui'])
    url_btn.config(state=states['idle_ui'])
    path_en.config(state=states['idle_ui'])
    path_btn.config(state=states['idle_ui'])
    stop_btn.config(state=states['runing_ui'])
    combo_box.config(state=states['idle_ui'])
    down_btn.config(state=states['idle_ui'])
    url_check_btn.config(state=states['idle_ui'])

def download():
    url_state = url_check()
    pathl_state = path_check()
    extl_state = ext_check()
    if url_state & pathl_state & extl_state:
        ui_state(False)
        global downloader
        downloader = ytdl.YtDownloader(Yt_URL, save_path, file_ext, information_update, progress_bar_update, download_finish)
        download_thread = threading.Thread(target=downloader.start)
        download_thread.start()
def download_finish():
    ui_state(True)
    app.update_idletasks()

def stop_download():
    global downloader
    if downloader:
        downloader.stop_set()
        del downloader
def resource_path(relative_path):
    # PyInstaller创建临时文件夹并将文件放在其中
    try:
        # 在打包的环境中
        base_path = sys._MEIPASS
    except Exception:
        # 在开发环境中
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = tk.Tk()
    app.geometry('480x300')
    app.resizable(width=False, height=True)
    app.config(background=bg)
    app.attributes('-alpha', 0.87)
    app.title('YtDownload')
    icon_path = resource_path('icon.ico')
    app.iconbitmap(icon_path)
    # 網址
    url_en_lb = tk.Label(app, text='Youtube URL', bg=bg, fg='white')
    url_en_lb.grid(column=0, row=0, padx=10, pady=5)

    url_en = tk.Entry(bg=itbg, fg='white' ,font='微軟正黑體 10')
    url_en.grid(column=1, row=0, padx=10, pady=5, columnspan=2, sticky="ew")

    url_btn = tk.Button(app, bg=itbg, fg='white', text='paste' ,font='微軟正黑體 10', command=set_url)
    url_btn.grid(column=3, row=0, padx=10, pady=5)

    # 路徑
    path_en_lb = tk.Label(app, text='Save Path', bg=bg, fg='white')
    path_en_lb.grid(column=0, row=1, padx=10, pady=5)

    path_en = tk.Entry(bg=itbg, fg='white' ,font='微軟正黑體 10')
    path_en.grid(column=1, row=1, padx=10, pady=5, columnspan=2, sticky="ew")

    path_btn = tk.Button(app, bg=itbg, fg='white', text='...' ,font=10 , command=set_path)
    path_btn.grid(column=3, row=1, padx=10, pady=5)


    # 選項
    stop_btn = tk.Button(app, bg=itbg, fg='white', text='X', font='微軟正黑體 10', command=stop_download, state='disabled')
    stop_btn.grid(column=0, row=2, padx=10, pady=5)

    options = ["Default mp3", "4320p mp4", '2160p mp4', '1440p mp4', '1080p mp4', '720p mp4', '480p mp4', '360p mp4',
               '240p mp4', '144p mp4']
    combo_box = ttk.Combobox(app, font='微軟正黑體 10', values=options)
    combo_box.grid(column=1, row=2, padx=10, pady=5)

    down_btn = tk.Button(app, bg=itbg, fg='white', text='Download' ,font='微軟正黑體 10', command=download)
    down_btn.grid(column=2, row=2, padx=10, pady=5)

    url_check_btn = tk.Button(app, bg=itbg, fg='white', text='check', font='微軟正黑體 10', command=url_check)
    url_check_btn.grid(column=3, row=2, padx=10, pady=5)

    #資訊欄
    group = tk.LabelFrame(app, text='information', bg=bg, fg='white', padx=10, pady=5)
    group.grid(column=0, row=3, padx=10, pady=5, columnspan=4, sticky="nsew")

    progress_bar = ttk.Progressbar(group, mode='determinate')
    progress_bar.pack(side='top', fill='x', expand=True, padx=10, pady=10)

    information = (tk.Label(group, text='', bg=bg, fg='white', wraplength=380))
    information.pack(side='top', fill='both', expand=True, padx=10, pady=10)


    # process = (tk.Label(group, text='0/0', bg=bg, fg='white'))
    # process.pack(side='right')
    app.mainloop()