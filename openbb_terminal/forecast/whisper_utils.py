from typing import Iterator, TextIO


def str2bool(string):
    str2val = {"True": True, "False": False}
    if string in str2val:
        return str2val[string]
    raise ValueError(f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(
    seconds: float, always_include_hours: bool = False, decimal_marker: str = "."
):
    if seconds < 0:
        raise ValueError("non-negative timestamp expected")

    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )


def break_line(line: str, length: int):
    break_index = min(len(line) // 2, length)  # split evenly or at maximum length

    # work backwards from that guess to split between words
    # if break_index <= 1, we've hit the beginning of the string and can't split
    while break_index > 1:
        if line[break_index - 1] == " ":
            break  # break at space
        break_index -= 1
    if break_index > 1:
        # split the line, not including the space at break_index
        return line[: break_index - 1] + "\n" + line[break_index:]
    return line


def process_segment(segment: dict, line_length: int = 0):
    segment["text"] = segment["text"].strip()
    if line_length and len(segment["text"]) > line_length:
        # break at N characters as per Netflix guidelines
        segment["text"] = break_line(segment["text"], line_length)

    return segment


def write_vtt(transcript: Iterator[dict], file: TextIO, line_length: int = 0):
    print("WEBVTT\n", file=file)
    for segment in transcript:
        segment = process_segment(segment, line_length=line_length)

        print(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def write_srt(transcript: Iterator[dict], file: TextIO, line_length: int = 0):
    for i, segment in enumerate(transcript, start=1):
        segment = process_segment(segment, line_length=line_length)

        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def slugify(title):
    # adding a slug (-) in each of the string where there is a space
    return "".join(c if c.isalnum() else "_" for c in title).rstrip("_")
