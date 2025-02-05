import subprocess
from datetime import datetime
import os
import pytest
import time


def get_current_time():
    # Get the current date and time
    current_time = datetime.now()

    # Format the date and time as mm_dd_yyyy_hh_mm_ss
    formatted_time = current_time.strftime("%m_%d_%Y_%H_%M_%S")
    return formatted_time


def results_path():
    base_path = "/home/ubuntu/Documents/"
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m_%d_%Y__%H_%M_%S")
    if not os.path.exists(base_path + "/test_results_" + formatted_time):
        os.mkdir(base_path + "/test_results_" + formatted_time)  # Creates only the last directory in the path
    return base_path + "/test_results_" + formatted_time


RESULT_FOLDER = results_path()


# Function to execute v4l2-ctl commands and return output
def run_v4l2_ctl(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.stdout.decode('utf-8'), e.stderr.decode('utf-8')


# Test 1: List all devices
def list_devices():
    print("Listing available video devices:")
    stdout, stderr = run_v4l2_ctl("v4l2-ctl --list-devices")
    if stderr:
        print("Error:", stderr)
        assert 0
    else:
        print(stdout)
        assert "/dev/video0" in stdout


# test 2: # search for webcam device:
def search_for_builtin_webcam_device():
    print("search for computer builtin webcam device:")
    flag = 0
    stdout, stderr = run_v4l2_ctl("v4l2-ctl --list-devices")
    if stderr:
        print("Error:", stderr)
    else:
        for line in stdout.split('\n'):
            if "/dev/video0" in line:
                print("webcam device 'video0' is found under /dev")
                flag = 1
    assert flag


# Test 3: Get device capabilities
def get_device_capabilities(device="/dev/video0"):
    print(f"Getting capabilities of {device}:")
    stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --all")
    if stderr:
        print("Error:", stderr)
        print("Test Failed")
    else:
        print(stdout)
        out = stdout.split('\n')
        for line in out:
            if "Width/Height" in line:
                assert "1280/720" in line


# Test 4: list webcam supported resolutions
def list_supported_device_resolutions(device="/dev/video0"):
    print("list webcam supported resolutions:")
    stdout, stderr = run_v4l2_ctl(f"ffmpeg -f v4l2 -list_formats all -i {device}")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)



# Test 5: Get device specs
def get_device_specs(device="/dev/video0"):
    params = [["Width/Height", "1280/720"], ["Size Image", "1843200"], ["brightness", "min=0", "max=255"],
              ["contrast", "min=0", "max=255"], ["saturation", "min=0", "max=100"]]
    for param in params:
        stdout, stderr = run_v4l2_ctl(f'v4l2-ctl --device={device} --all | grep -iE "{param[0]}"')
        if stderr:
            print("Error:", stderr)
            print("Test Failed")
            assert 0
        elif stdout:
            for i in range(1, len(param)):
                assert param[i] in stdout
        else:
            assert 0
    assert 1


# Test 6: List supported formats for a device
def list_supported_formats(device="/dev/video0"):
    print(f"Listing supported formats for {device}:")
    stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --list-formats")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 7: Capture a frame (save as image)
def capture_frame(device="/dev/video0", filename="frame", ext="jpg"):
    date = get_current_time()
    print(f"Capturing a frame from {device} and saving as {filename}_{date}.{ext}:")
    # stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --capture --file={filename}")
    stdout, stderr = run_v4l2_ctl(
        f"ffmpeg -f video4linux2 -i {device} -frames 1 {RESULT_FOLDER}/{filename}_{date}.{ext}")

    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 8: video stream (save as jpg)
def video_stream(device="/dev/video0", filename="video", ext="mp4"):
    date = get_current_time()
    print(f"Capturing video from {device} and saving as {filename}_{date}.{ext}:")
    stdout, stderr = run_v4l2_ctl(
        f"ffmpeg -f v4l2 -t 3 -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
        f"{filename}_{date}.{ext}")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 9: Capture a frame with different format (save as image)
def capture_frame_diff_formats(device="/dev/video0", filename="diff_format_frame"):
    supported_format = ["jpg", "png", "bmp", "rgb"]
    for ext in supported_format:
        date = get_current_time()
        print(f"Capturing a frame from {device} and saving as {filename}_{date}.{ext}:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f video4linux2 -i {device} -frames 1 {RESULT_FOLDER}/{filename}_{date}.{ext}")

        if stderr:
            print("Error:", stderr)
        else:
            print(stdout)


# Test 10: video stream with different format (save as jpg)
def video_stream_diff_formats(device="/dev/video0", filename="video"):
    supported_format = ["avi", "mp4", "raw"]
    for ext in supported_format:
        date = get_current_time()
        print(f"Capturing video from {device} and saving as {filename}_{date}.{ext}:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f v4l2 -t 3 -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
            f"{filename}_{date}.{ext}")
        if stderr:
            print("Error:", stderr)
        else:
            print(stdout)


# Test 11:
def video_frame_rate(device="/dev/video0", filename="video", ext="mp4"):
    fps_list = ["1", "2", "3", "5", "10", "20", "30", "40", "50", "100"]
    for fps in fps_list:
        date = get_current_time()
        print(f"Capturing 3 seconds video from {device} and saving as {filename}__{fps}_fps__{date}.{ext} with {fps}:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -framerate {fps} -f v4l2 -t 3 -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
            f"{filename}__{fps}_fps__{date}.{ext}")
        if stderr:
            print("Error:", stderr)
        else:
            print(stdout)


# Test 12:
def capture_image_with_different_resolution(device="/dev/video0", filename="image_12"):
    # supported resolutions were found using 'v4l2-ctl --list-formats-ext' command
    # List of supported resolutions from v4l2-ctl output
    supported_resolutions = ["1280x720", "32x180", "320x240", "352x288", "424x240",
                             "640x360", "640x480", "848x480", "960x540"]
    for res in supported_resolutions:
        date = get_current_time()
        print(f"Capturing 3 seconds video from {device} and saving as {filename}__{res}_res__{date}.jpg with {res}:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f video4linux2 -video_size {res} -i {device} -frames 1 {RESULT_FOLDER}/"
            f"{filename}__{res}_res__{date}.jpg")
        if stderr:
            print("Error:", stderr)
        else:
            print(stdout)


# Example usage:
if __name__ == "__main__":
    # List devices
    list_devices()

    # search for webcam device:
    search_for_builtin_webcam_device()

    # Get capabilities of the first device (adjust if needed)
    get_device_capabilities("/dev/video0")

    # List supported webcam resolutions
    list_supported_device_resolutions("/dev/video0")

    # List supported formats
    list_supported_formats("/dev/video0")

    # Capture a frame
    capture_frame("/dev/video0", "test_frame_7", "jpg")

    # video stream
    video_stream("/dev/video0", "test_video_8", "mp4")

    capture_frame_diff_formats(device="/dev/video0", filename="frame_9")

    video_stream_diff_formats(device="/dev/video0", filename="video_10")

    video_frame_rate(device="/dev/video0", filename="video_11")

    capture_image_with_different_resolution(device="/dev/video0", filename="image_12")

    print("FINISHED")