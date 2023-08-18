import ffmpeg

def convert_mp4(input_path, output_path, bitrate='1000k', resolution='640x360'):
    (
        ffmpeg.input(input_path)
        .output(output_path, vf='scale=' + resolution, bitrate=bitrate)
        .run()
    )

# Usage example
input_file = 'input.mp4'
output_file = 'output.mp4'
convert_mp4(input_file, output_file, bitrate='500k', resolution='640x360')