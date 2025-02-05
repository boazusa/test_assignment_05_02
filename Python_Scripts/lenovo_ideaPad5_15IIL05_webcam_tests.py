import subprocess
from datetime import datetime
import os
import pytest
import time


def get_current_time():
    # Get the current date and time
    current_time = datetime.now()

    # Format the date and time as mm_dd_yyyy_hh_mm_ss
    formatted_time = current_time.strftime("%m_%d_%Y__%H_%M_%S")
    return formatted_time


def results_path():
    base_path = "/home/ubuntu/Documents/"
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m_%d_%Y__%H_%M_%S")
    if not os.path.exists(base_path + "/test_results_" + formatted_time):
        os.mkdir(base_path + "/test_results_" + formatted_time)  # Creates only the last directory in the path
    return base_path + "/test_results_" + formatted_time


RESULT_FOLDER = results_path()

print(f"Results are saved to {RESULT_FOLDER}")

# Function to execute v4l2-ctl commands and return output
def run_v4l2_ctl(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.stdout.decode('utf-8'), e.stderr.decode('utf-8')


# Test 1: Sanity, List all devices
def list_devices():
    print("Listing available video devices:")
    stdout, stderr = run_v4l2_ctl("v4l2-ctl --list-devices")
    if stderr:
        print("Error:", stderr)
        assert 0
    else:
        print(stdout)
        assert "/dev/video0" in stdout


# test 2: Sanity, search for webcam device:
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


# Test 3: Sanity, Get device capabilities
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
            if "brightness" in line:
                assert "min=0" in line
                assert "max=255" in line


# Test 4: Sanity, list webcam supported resolutions
def list_supported_device_resolutions(device="/dev/video0"):
    print("list webcam supported resolutions:")
    stdout, stderr = run_v4l2_ctl(f"ffmpeg -f v4l2 -list_formats all -i {device}")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)



# Test 5: Sanity, Get device specs
def get_device_specs(device="/dev/video0"):
    params = [["brightness", "min=0", "max=255"], ["contrast", "min=0", "max=255"], ["saturation", "min=0", "max=100"]]
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


# Test 6: Sanity, List supported formats for a device
def list_supported_formats(device="/dev/video0"):
    print(f"Listing supported formats for {device}:")
    stdout, stderr = run_v4l2_ctl(f"v4l2-ctl --device={device} --list-formats")
    if stderr:
        print("Error:", stderr)
    else:
        print(stdout)


# Test 7: Sanity, Capture a frame (save as image)
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


# Test 8: Sanity, video stream (save as mp4)
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


# Test 9: Functional, Capture a frame with different format supported formats shall be created and viewable
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


# Test 10: Functional, video stream recording with different supported formats shall be created and played
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


# Test 11: Performance, test video recording for different fps (supported and unsupported)
def video_frame_rate(device="/dev/video0", filename="video", ext="mp4"):
    fps_list = ["1", "2", "3", "5", "10", "20", "30", "40", "50", "100"]
    for fps in fps_list:
        date = get_current_time()
        print(f"Capturing 3 seconds video from {device} and saving as {filename}__{fps}_fps__{date}.{ext} "
              f"with {fps} fps settings:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -framerate {fps} -f v4l2 -t 3 -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
            f"{filename}__{fps}_fps__{date}.{ext}")
        stdout_fps_info, stderr_fps_info = run_v4l2_ctl(f'ffmpeg -i {RESULT_FOLDER}/{filename}__{fps}_fps__{date}.{ext}'
                                                        f' 2>&1 | grep "Stream #"')
        include = "fps"
        stdout_fps_info_list = stdout_fps_info.split(',')
        print("Test 11:", "\n".join(s for s in stdout_fps_info_list if include.lower() in s.lower()))

        # if stderr:
        #     print("Error:", stderr)
        # else:
        #     print(stdout)


# Test 12: Performance, Image capturing shall be created with every supported resolution.
def capture_image_with_different_resolution(device="/dev/video0", filename="image_12"):
    # supported resolutions were found using 'v4l2-ctl --list-formats-ext' command
    # List of supported resolutions from v4l2-ctl output
    supported_resolutions = ["1280x720", "320x180", "320x240", "352x288", "424x240",
                             "640x360", "640x480", "848x480", "960x540"]
    for res in supported_resolutions:
        date = get_current_time()
        print(f"Capturing image from {device} and saving as {filename}__{res}_res__{date}.jpg with {res} resolution:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f video4linux2 -video_size {res} -i {device} -frames 1 {RESULT_FOLDER}/"
            f"{filename}__{res}_res__{date}.jpg")
        resolution_test = r""" 2>&1 | grep "Stream #0" | sed -n 's/.*, \([0-9]\+x[0-9]\+\).*/\1/p'"""
        resolution_info, err = run_v4l2_ctl(
            f"ffmpeg -i {RESULT_FOLDER}/{filename}__{res}_res__{date}.jpg" + resolution_test)

        if device == "/dev/video0":
            assert resolution_info.strip() == res,(f"Resolution info received {resolution_info.strip()}"
                                                    f" != resolution set {res}")
        else:
            if resolution_info.strip() != res:
                print(
                    f"{device} captured resolution was set to {res}, but images created with {resolution_info.strip()}")


# Test 13: Performance, Negative, Video recording shall be created with every supported resolution.
def video_resolution(device="/dev/video0", filename="video_13", ext="mp4"):
    # List of supported resolutions from v4l2-ctl output
    supported_resolutions = ["1280x720", "320x180", "320x240", "352x288", "424x240",
                             "640x360", "640x480", "848x480", "960x540"]
    for res in supported_resolutions:
        date = get_current_time()
        print(f"Capturing 3 seconds video from {device} and saving as {filename}__{res}_res__{date}.{ext}"
              f" with {res} resolution:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f v4l2 -t 3 -video_size {res} -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
            f"{filename}__{res}_res__{date}.{ext}")
        resolution_test = r""" 2>&1 | grep "Stream #0" | sed -n 's/.*, \([0-9]\+x[0-9]\+\).*/\1/p'"""
        resolution_info, err = run_v4l2_ctl(
            f"ffmpeg -i {RESULT_FOLDER}/{filename}__{res}_res__{date}.{ext}" + resolution_test)

        if device == "/dev/video0":
            assert resolution_info.strip() == res,(f"Resolution info received {resolution_info.strip()}"
                                                f" != resolution set {res}")
        else:
            if resolution_info.strip() != res:
                print(f"{device} captured resolution was set to {res}, but images created with {resolution_info.strip()}")


# Test 14: Negative, Image capturing shall be created with supported resolution only.
# image resolution shall be created with the nearest supported resolution available
def capture_image_with_different_unsupported_resolution(device="/dev/video0", filename="image_14"):
    # List of random unsupported resolutions (not in v4l2-ctl output list)
    supported_resolutions = ["1200x720", "321x180", "20x240", "352x28", "42x240",
                             "640x1360", "64x480", "848x48", "1960x540"]
    for res in supported_resolutions:
        date = get_current_time()
        print(f"Capturing image from {device} and saving as {filename}__{res}_res__{date}.jpg with {res} resolution:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f video4linux2 -video_size {res} -i {device} -frames 1 {RESULT_FOLDER}/"
            f"{filename}__{res}_res__{date}.jpg")
        resolution_test = r""" 2>&1 | grep "Stream #0" | sed -n 's/.*, \([0-9]\+x[0-9]\+\).*/\1/p'"""
        resolution_info, err = run_v4l2_ctl(
            f"ffmpeg -i {RESULT_FOLDER}/{filename}__{res}_res__{date}.jpg" + resolution_test)

        assert resolution_info.strip() != res,(f"Resolution info received {resolution_info.strip()}"
                                               f" != resolution set {res}")


# Test 15: Negative, Video recording shall be created with supported resolution only.
# Video resolution shall be created with the nearest supported resolution available
def video_unsupported_resolution(device="/dev/video0", filename="video_15", ext="mp4"):
    # List of random unsupported resolutions (not in v4l2-ctl output list)
    supported_resolutions = ["1200x720", "321x180", "20x240", "352x28", "42x240",
                             "640x1360", "64x480", "848x48", "1960x540"]
    for res in supported_resolutions:
        date = get_current_time()
        print(f"Capturing 3 seconds video from {device} and saving as {filename}__{res}_res__{date}.{ext}"
              f" with {res} unsupported resolution:")
        stdout, stderr = run_v4l2_ctl(
            f"ffmpeg -f v4l2 -t 3 -video_size {res} -i {device} -vcodec libx264 -acodec aac {RESULT_FOLDER}/"
            f"{filename}__{res}_res__{date}.{ext}")
        resolution_test = r""" 2>&1 | grep "Stream #0" | sed -n 's/.*, \([0-9]\+x[0-9]\+\).*/\1/p'"""
        resolution_info, err = run_v4l2_ctl(
            f"ffmpeg -i {RESULT_FOLDER}/{filename}__{res}_res__{date}.{ext}" + resolution_test)

        assert resolution_info.strip() != res,(f"Resolution info received {resolution_info.strip()}"
                                                f" == unsupported resolution set {res}")



# Example usage:
if __name__ == "__main__":
    print(f"Test start Time: {get_current_time()}")
    start_time = time.time()

    # List devices
    list_devices()

    dev_1 = "/dev/video0"
    dev_2 = "/dev/video2"
    devices = [dev_1, dev_2]

    # search for webcam device:
    search_for_builtin_webcam_device()

    for dev in devices:
        # Get capabilities of the first device (adjust if needed)
        get_device_capabilities(dev)

        # List supported webcam resolutions
        list_supported_device_resolutions(dev)

        # List supported formats
        list_supported_formats(dev)

        # Capture a frame
        capture_frame(dev, "test_frame_7", "jpg")

        # video stream
        video_stream(dev, "test_video_8", "mp4")

        capture_frame_diff_formats(device=dev, filename="frame_9")

        video_stream_diff_formats(device=dev, filename="video_10")

        video_frame_rate(device=dev, filename="video", ext="mp4")
        video_frame_rate(device=dev, filename="video", ext="avi")

        capture_image_with_different_resolution(device=dev, filename="image_12")

        video_resolution(device=dev, filename="video_13")

        capture_image_with_different_unsupported_resolution(device=dev, filename="image_14")

        video_unsupported_resolution(device=dev, filename="video_14")

    print(f"Test end Time: {get_current_time()}")
    print("Test Execution duration: --- %s seconds ---" % (time.time() - start_time))
    print("--- %s seconds ---" % (time.time() - start_time))

