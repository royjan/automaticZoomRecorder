import time
import wave

import cv2
import mss
import numpy as np
import pyaudio
from moviepy.editor import VideoFileClip, AudioFileClip

FORMAT = pyaudio.paInt16
RATE = 44100
audio = pyaudio.PyAudio()
CHANNELS = 2
audio_record_frames = []
stop_threads = False
CHUNK = 512
FPS = 13
PATH_TO_MIDDLE = "output.avi"
AUDIO_PATH = "file.wav"
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080


def run(function, args):
    number_of_times = 0
    previous_time = 0
    while True:
        function(*args)
        number_of_times += 1
        time_now = time.time()
        print(f"{function.__name__} FPS: {1. / (time_now - previous_time)}")
        previous_time = time_now
        if stop_threads:
            break


def capture_video(sct, monitor, video_writer):
    frame = capture_from_screen(sct, monitor)
    video_writer.write(frame)


def capture_audio(stream):
    global audio_record_frames
    for _ in range(0, int(RATE / CHUNK)):
        audio_record_frames.append(record_audio(stream))


def capture_from_screen(sct, monitor):
    img = np.array(sct.grab(monitor))
    img = np.flip(img[:, :, :3], 2)  # 1
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 2
    return frame


def get_sound_card(automatic=False):
    info = audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    automatic_index = 0
    print("----------------------record device list---------------------")
    devices_names = [audio.get_device_info_by_host_api_device_index(0, i).get('name') for i in range(num_devices) if
                     audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0]
    for index, device in enumerate(devices_names):
        print(f"{index}) Input Device id {device}")
        if "stereo mix" in device.lower():
            automatic_index = index
    print("-------------------------------------------------------------")
    if automatic:
        return automatic_index
    index = int(input())
    print("recording via index " + str(index))
    return index


def create_stream_object(device_index, channels=CHANNELS):
    return audio.open(format=FORMAT, channels=channels,
                      rate=RATE, input=True, output=True, input_device_index=device_index, frames_per_buffer=CHUNK)


def record_to_array(stream):
    for i in range(0, int(RATE / CHUNK)):
        data = record_audio(stream)
        audio_record_frames.append(data)
    return audio_record_frames


def stop_record(stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()


def record_audio(stream):
    return stream.read(CHUNK, exception_on_overflow=False)


def create_wave_file(data, file_name, channels=CHANNELS):
    waveFile = wave.open(file_name, 'wb')
    waveFile.setnchannels(channels)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(data))
    waveFile.close()


def start_threads(sct, monitor, video_writer, stream, during):
    global stop_threads
    import threading
    import time
    t1 = threading.Thread(target=run, args=(capture_video, (sct, monitor, video_writer)))
    t2 = threading.Thread(target=run, args=(capture_audio, [stream]))
    t1.start()
    t2.start()
    time.sleep(int(during*60))
    stop_threads = True
    t1.join()
    t2.join()


def combine_audio_with_video():
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    video = VideoFileClip(PATH_TO_MIDDLE)
    audio_object = AudioFileClip(AUDIO_PATH)
    temp_video = video.set_audio(audio_object)
    video = CompositeVideoClip([temp_video])
    video.write_videofile("test2.mp4", codec="libx264")


def get_monitor_configuration(sct):
    monitor_number = 1
    mon = sct.monitors[monitor_number]
    monitor = {
        "top": mon["top"] + 0,  # 100px from the top
        "left": mon["left"] + 0,  # 100px from the left
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "mon": monitor_number,
    }
    return monitor


def setup_video_configuration():
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    video_writer = cv2.VideoWriter(PATH_TO_MIDDLE, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
    index = get_sound_card(automatic=True)
    return video_writer, index


def capture_screen(during=1):
    """
    :param during: how many minutes is the meeting
    """
    video_writer, device_index = setup_video_configuration()
    global stop_threads
    stream = create_stream_object(device_index)

    with mss.mss() as sct:
        monitor = get_monitor_configuration(sct)
        start_threads(sct, monitor, video_writer, stream, during)
        stop_record(stream)
        create_wave_file(audio_record_frames, AUDIO_PATH)
        video_writer.release()
        cv2.destroyAllWindows()
        combine_audio_with_video()


if __name__ == '__main__':
    capture_screen()
