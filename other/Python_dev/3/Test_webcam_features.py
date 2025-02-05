import subprocess
from datetime import datetime
import pytest
import time

def get_current_time():
    # Get the current date and time
    current_time = datetime.now()

    # Format the date and time as mm_dd_yyyy_hh_mm_ss
    formatted_time = current_time.strftime("%m_%d_%Y_%H_%M_%S")
    return formatted_time


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
    else:
        print(stdout)

# test 1.1: # search for webcam device:
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


# Test 2: Get device capabilities
def get_device_capabilities(device="/dev/video0"):
    print(f"Getting capabilities of {device}:")
    stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --all")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 3: List supported formats for a device
def list_supported_formats(device="/dev/video0"):
    print(f"Listing supported formats for {device}:")
    stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --list-formats")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 4: Capture a frame (save as image)
def capture_frame(device="/dev/video0", filename="frame", format="jpg"):
    date = get_current_time()
    print(f"Capturing a frame from {device} and saving as {filename}_{date}.{format}:")
    # stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --capture --file={filename}")
    stdout, stderr = run_v4l2_ctl(f"ffmpeg -f video4linux2 -i {device} -frames 1 /home/ubuntu/Documents/{filename}_{date}.{format}")

    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 5: video stream (save as jpg)
def video_stream(device="/dev/video0", filename="video.jpg", format="mp4"):
    date = get_current_time()
    print(f"Capturing video from {device} and saving as {filename}_{date}.{format}:")
    # stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --capture --file={filename}")
    stdout, stderr = run_v4l2_ctl(f"ffmpeg -f v4l2 -t 3 -i /dev/video0 -vcodec libx264 -acodec aac /home/ubuntu/Documents/{filename}_{date}.{format}")
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

    # List supported formats
    list_supported_formats("/dev/video0")

    # Capture a frame
    capture_frame("/dev/video0", "test_frame_1", "jpg")

    # video stream
    video_stream("/dev/video0", "test_video_1", "mp4")

    print("FINISHED")