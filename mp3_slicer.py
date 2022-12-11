import os
from mutagen import mp3
from mutagen import id3
import argparse
import pydub
from pydub import AudioSegment
import ffmpeg

frame_names = []
parsed_frames = {}

# CLI Interface
parser = argparse.ArgumentParser(
    description='This is a small program to cut MP3 audio using the difference between two timestamps.')
parser.add_argument('src_path', metavar='src_path', type=str, help='Enter source path of MP3 file that '
                                                                   'will be sliced.')
parser.add_argument('--dst_path', action='store', help='choose destination file path for newly created'
                                                       'file')
# parser.add_argument('--filename', help='user created name of the sliced MP3 file')
args = parser.parse_args()

# check file to confirm it exists
def file_check():
    """May need input validation to ensure only string/filepaths are entered"""
    while True:
        file_to_parse = input(str("Source file: "))
        if os.path.exists(file_to_parse):
            filename = os.path.basename(file_to_parse)
            print(f'File name is: {filename}')
            return [file_to_parse, filename]
        else:
            print("File does not exist. Please select correct file.")

# parse ID3 tags of file
def parse_id3_tags():
    try:
        confirm_file = file_check()
        parsed_mp3 = id3.ID3(confirm_file[0])
        audio = AudioSegment.from_mp3(confirm_file[0])
        audio_duration = AudioSegment.from_file(confirm_file[0])
        audio_len = audio_duration.duration_seconds
        audio_in_secs = audio_len/60

        # find all the tags that exist in the file
        for tag in parsed_mp3:
            if tag != 'APIC:cover':
                print(tag + " - " + str(parsed_mp3[tag]))
                parsed_frames.update({tag: str(parsed_mp3[tag])})
        return [audio, confirm_file[1], audio_in_secs]
    except Exception:
        print("No ID3 tags exist for this file.")


def slice_audio():
    """Needs a while loop to allow users to enter integers if they choose wrong value type
    NEED TO PERFORM A VALIDATION TO PREVENT USERS FROM ENTERING NONSENSICAL NUMBERS
    CHECK THE ACTUAL LEN/DURATION OF THE FILE
    ENSURE THAT ENDING MINUTE IS LARGER THAN THE START MINUTE"""
    parsed_tags = parse_id3_tags()
    while True:
        try:
            start_min = int(input("Provide start minute: "))
            start_sec = int(input("Provide start second: "))
            end_min = int(input("Provide ending minute: "))
            end_sec = int(input("Provide ending second: "))

            if len(str(start_min)) > 2 or len(str(start_sec)) > 2 or len(str(end_min)) > 2 or len(str(end_sec)) > 2:
                print(f'The song is {parsed_tags[2]} minutes long. The values cannot exceed 2 integers.'
                      f'Please adjust values accordingly.')
                continue

            # conversion in millisecs
            start_time = start_min * 60 * 1000 + start_sec * 1000
            end_time = end_min * 60 * 1000 + end_sec * 1000

            if end_time < start_time:
                print(f'The song is {parsed_tags[2]} minutes long.')
                print("The total start time of the song cannot be greater than the total end time. Please adjust the values accordingly.")
                continue

            slice_audio = parsed_tags[0][start_time:end_time]
            filename = parsed_tags[1]
            slice_audio.export(f'Sliced_{filename}', format='mp3')
            print("Slicing process has completed. Please check your new file.")
            return [slice_audio, filename]
        except ValueError:
            print("Input must be an integer. Please use an integer and try again.")


def export_to_filepath(dest_filepath):
    mp3_audio = slice_audio()
    filepath = dest_filepath
    if os.path.exists(dest_filepath):
        mp3_audio[0].export(os.path.join(dest_filepath, mp3_audio[1]))
    else:
        os.makedirs(filepath)
        mp3_audio[0].export(os.path.join(filepath, str(mp3_audio[1])))

############################################################
"""START OF COMMAND LINE CODE"""
if args.dst_path:
    export_to_filepath(args.dst_path)
else:
    slice_audio()
