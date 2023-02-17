import subprocess
import os
import random
import tkinter as tk
from tkinter import filedialog
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip


def install_required_libraries():
    try:
        import tkinter
        import pytube
        from moviepy.editor import VideoFileClip
    except ImportError:
        subprocess.check_call(
            ['python', '-m', 'pip', 'install', 'tkinter', 'pytube', 'moviepy'])


def concat_videos(video_path_1, video_path_2, output_path):
    # Load the two video clips
    clip1 = VideoFileClip(video_path_1)
    clip2 = VideoFileClip(video_path_2)

    # Add a crossfade effect between the two clips
    crossfade_duration = 1.0
    crossfade = CompositeVideoClip([
        clip1.crossfadein(crossfade_duration),
        clip2.crossfadeout(crossfade_duration)
    ], duration=clip1.duration+clip2.duration-crossfade_duration)

    # Concatenate the two clips with the crossfade effect
    final_clip = concatenate_videoclips([clip1, crossfade, clip2])

    # Add additional effects to the final clip if desired

    # Write the final clip to a file
    final_clip.write_videofile(output_path)


def concat_videos_folder(input_path):
    video_paths = get_video_files(input_path)
    videos = []
    for video_path in video_paths:
        video_clip = VideoFileClip(video_path)
        videos.append(video_clip)
    if not videos:
        return None
    final_clip = concatenate_videoclips(videos)
    output_path = f"./temp/"+get_folder_name(input_path)+".mp4"
    final_clip.write_videofile(output_path)
    return output_path


def concatenate_audio_files(input_files, output_file):
    # Create a text file with the list of input files
    input_list_path = './input_list.txt'
    with open(input_list_path, 'w') as f:
        for path in input_files:
            f.write("file '{}'\n".format(path))

    # Use ffmpeg to concatenate the input files
    cmd = 'ffmpeg -y -f concat -safe 0 -i "{}" -c copy "{}"'.format(
        input_list_path, output_file)
    subprocess.call(cmd, shell=True)

    # Delete the input list file
    os.remove(input_list_path)


def concat_audio_files(audio_files, output_file):
    # Create a list of input files for ffmpeg
    input_files = []
    for file in audio_files:
        input_files.append("-i")
        input_files.append(file)

    # Create the command for ffmpeg to concatenate the input files
    ffmpeg_command = ["ffmpeg"] + input_files + ["-filter_complex",
                                                 "concat=n={}:v=0:a=1".format(len(audio_files)), "-y", output_file]

    # Call the ffmpeg command
    subprocess.run(ffmpeg_command, check=True)


def concat_audios_folder(input_path):
    audio_paths = get_audio_files(input_path)
    if not audio_paths:
        return None
    random.shuffle(audio_paths)
    output_path = f"temp/temp.mp3"
    concat_audio_files(audio_files=audio_paths, output_file=output_path)
    return output_path


def merge_audio_into_video(video_file, audio_file, output_file):
    # Load the video and audio files
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)

    # Set the audio of the video to the audio from the audio file
    video = video.set_audio(audio)

    # Set the duration of the video to the duration of the audio file
    video = video.set_duration(video.duration)

    # Write the output file
    video.write_videofile(output_file)


def check_or_create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Created directory: " + directory)
    else:
        print("Directory already exists: " + directory)


def download_youtube_audio(url, output_dir):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    file_name = f"{yt.title}.mp3"
    file_path = os.path.join(output_dir, file_name)
    stream.download(output_path=output_dir, filename=file_name)
    return file_path


def download_audio():
    url = url_entry.get()
    error_label.config(text="Đang tải: " + url)
    download_audio_button.config(text="Đang tải")
    audio_path = download_youtube_audio(
        url=url, output_dir="./audio")
    download_audio_button.config(text="Tải nhạc")
    error_label.config(text="Đã tải: " + audio_path)
    url_entry.config(textvariable="")


def create_video_folder():
    folder_path = filedialog.askdirectory()
    audio_path = "./"+concat_audios_folder(f"./audio")
    video_path = concat_videos_folder(folder_path)
    video_button.config(text="Đang tạo")
    if not os.path.exists(audio_path) or not os.path.exists(video_path):
        error_label.config(text="Tạo không thành công")
        os.remove(audio_path)
        os.remove(video_path)
        return
    export_path = "./export/" + get_folder_name(video_path)
    merge_audio_into_video(video_file=video_path, audio_file=audio_path,
                           output_file=export_path)
    error_label.config(text="Đã tạo: " + export_path)
    video_button.config(text="Tạo video")
    open_export_folder()


def open_file_explorer(path):
    """
    Opens the file explorer for the given path.
    """
    os.startfile(path)


def open_export_folder():
    open_file_explorer("export")


def open_audio_folder():
    open_file_explorer("audio")


def get_video_files(directory):
    # get a list of all the files in the directory
    files = os.listdir(directory)

    # filter for only the video files
    video_files = []
    for file in files:
        if file.endswith(".mp4") or file.endswith(".avi") or file.endswith(".mov"):
            video_files.append(os.path.join(directory, file))

    return video_files


def get_audio_files(directory):
    audio_extensions = ('.mp3')
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(audio_extensions):
                audio_files.append(os.path.join(root, file))
    return audio_files


def get_folder_name(path):
    return os.path.basename(path)


def increase_i(i):
    i = i+1


# main
if __name__ == '__main__':
    install_required_libraries()
    # Your program code here...


check_or_create_directory("export")
check_or_create_directory("audio")
check_or_create_directory("temp")
root = tk.Tk()

frame = tk.Frame(root)
frame.grid(row=0, column=0)
frame.pack(pady=10, padx=10)
i = -1


error_label = tk.Label(frame, text="")
error_label.grid(row=increase_i(i), column=0, sticky='w')

url_label = tk.Label(frame, text="Nhập link youtube để tải nhạc:")
url_label.grid(row=increase_i(i), column=0, sticky='w')

url_entry = tk.Entry(frame)
url_entry.config(width=50)
url_entry.grid(row=increase_i(i), column=0)

download_audio_button = tk.Button(
    frame, text="Tải nhạc", command=download_audio)
download_audio_button.grid(row=increase_i(i), column=0, sticky='w')

video_button = tk.Button(frame, text="Tạo video",
                         command=create_video_folder)
video_button.grid(row=increase_i(i), column=0, sticky='w')


open_export = tk.Button(frame, text="Mở video đã tạo",
                        command=open_export_folder)
open_export.grid(row=increase_i(i), column=0, sticky='w')
open_audio = tk.Button(frame, text="Mở thư mục nhạc",
                       command=open_audio_folder)
open_audio.grid(row=increase_i(i), column=0, sticky='w')
root.mainloop()
