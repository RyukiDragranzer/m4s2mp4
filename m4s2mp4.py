import os
import sys

from moviepy import VideoFileClip, AudioFileClip

def exchange(input_path, output_path, buffer_size=256 * 1024 * 1024):
    #修复视频m4s
    #引入buffer_size为了平衡各个电脑的性能,没有一口气把所有内容全部读入
    #原始单位为字节,去掉后面两个1024即为所对应的M字节大小
    with open(input_path, 'rb') as f:
        header = f.read(32)
        new_header = header.replace(b'000000000', b'')
        with open(output_path, 'wb') as output_file:
            output_file.write(new_header)
            i = f.read(buffer_size)
            while i:
                output_file.write(i)
                i = f.read(buffer_size)


def bind(video_path, audio_path, output_path):
    video_fix_path = "".join([video_path.split(".")[0], "-1.m4s"])
    exchange(video_path, video_fix_path)
    video = VideoFileClip(video_fix_path)

    audio_fix_path = "".join([audio_path.split(".")[0], "-1.m4s"])
    exchange(audio_path, audio_fix_path)
    audio = AudioFileClip(audio_fix_path)

    video = video.with_audio(audio)
    video.write_videofile(output_path, codec = "h264_nvenc", audio_codec='aac', threads=4, preset="fast")


    os.remove(video_fix_path)
    os.remove(audio_fix_path)


def single_dir_search(dir_path, output_dir=None):
    import json
    from pathlib import Path
    output_dir_path = Path(output_dir)
    if not output_dir_path.exists():
        output_dir_path.mkdir()

    json_path = os.path.join(dir_path, "videoInfo.json")
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if output_dir is None:
        video_name = os.path.join(dir_path, data['title'] + '.mp4')
    else:
        video_name = os.path.join(output_dir, data['title'] + '.mp4')

    if os.path.exists(video_name):
        return

    files = os.listdir(dir_path)
    video_path = None
    audio_path = None
    for file in files:
        if file.endswith(".m4s"):
            if video_path is None:
                video_path = os.path.join(dir_path, file)
            else:
                size1 = os.path.getsize(video_path)
                size2 = os.path.getsize(os.path.join(dir_path, file))
                if size1 < size2:
                    audio_path = video_path
                    video_path = os.path.join(dir_path, file)
                else:
                    audio_path = os.path.join(dir_path, file)

    bind(video_path, audio_path, video_name)


def search_bat(dirs_path, output_dir):
    if dirs_path.split("\\")[-1].isdigit():
        single_dir_search(dirs_path, output_dir)
    else:
        dirs = os.listdir(dirs_path)
        for single_dir in dirs:
            new_dir = os.path.join(dirs_path, single_dir)
            if os.path.isdir(new_dir) and single_dir.isdigit():
                single_dir_search(new_dir, output_dir)


if __name__ == '__main__':
    try:
        search_bat(sys.argv[1], sys.argv[2])
    except:
        #search_bat('E:\VideoDownload\BIliBili\\30492590407','E:\VideoDownload\Output')
        pass

