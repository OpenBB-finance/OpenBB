"""Utilize OpenAI Whisper to transcribe and summarize text"""
__docformat__ = "numpy"

import logging
from typing import Union, Optional, List
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

import warnings
import os
import whisper
from transformers import pipeline


from openbb_terminal.forecast.whisper_utils import (
    slugify,
    str2bool,
    write_srt,
    write_vtt,
)
import yt_dlp

# from .utils import slugify, str2bool, write_srt, write_vtt
import tempfile

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


def get_audio(urls):
    temp_dir = tempfile.gettempdir()

    ydl = yt_dlp.YoutubeDL(
        {
            "quiet": True,
            "verbose": True,
            "format": "bestaudio",
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"),
            "external_downloader_args": ["-loglevel", "panic"],
            "postprocessors": [
                {
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                    "key": "FFmpegExtractAudio",
                }
            ],
        }
    )

    paths = {}

    for url in urls:
        result = ydl.extract_info(url, download=True)
        print(f"Downloaded video \"{result['title']}\". Generating subtitles...")
        paths[result["title"]] = os.path.join(temp_dir, f"{result['id']}.mp3")

    return paths


@log_start_end(log=logger)
def transcribe_and_summarize(
    video: str = "",
    model_name: str = "small",
    subtitles_format: str = "vtt",
    export: str = "",
    verbose: bool = False,
    task: str = "transcribe",
    language: str = None,
    breaklines: int = 0,
    output_dir: str = "/Users/martinbufi/OpenBBTerminal/openbb_terminal/forecast/whisper_output",
):

    # Use the pipeline to summarize the text
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    console.print("Transcribing and summarizing...")
    print(f"video: {video}")
    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection."
        )
    os.makedirs(output_dir, exist_ok=True)

    model = whisper.load_model(model_name)
    audios = get_audio([video])

    for title, audio_path in audios.items():
        warnings.filterwarnings("ignore")

        decode_options = {"task": task, "language": language}
        result = whisper.transcribe(
            model=model,
            audio=audio_path,
            verbose=verbose,
            **decode_options,
        )
        warnings.filterwarnings("default")

        all_text = ""
        for segment in result["segments"]:
            all_text += segment["text"]

        original_text_length = len(all_text)

        summary = summarizer(all_text)

        summary_text = summary[0]["summary_text"]
        summary_text_length = len(summary_text)
        percent_reduction = round(
            (1 - (summary_text_length / original_text_length)) * 100, 2
        )

        print(f"Summary (reduction {percent_reduction})")
        print(summary_text)

        if subtitles_format == "vtt":
            vtt_path = os.path.join(output_dir, f"{slugify(title)}.vtt")
            with open(vtt_path, "w", encoding="utf-8") as vtt:
                write_vtt(result["segments"], file=vtt, line_length=breaklines)

            print("Saved VTT to", os.path.abspath(vtt_path))
        else:
            srt_path = os.path.join(output_dir, f"{slugify(title)}.srt")
            with open(srt_path, "w", encoding="utf-8") as srt:
                write_srt(result["segments"], file=srt, line_length=breaklines)

            print("Saved SRT to", os.path.abspath(srt_path))
