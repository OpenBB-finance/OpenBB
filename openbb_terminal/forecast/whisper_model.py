"""Utilize OpenAI Whisper to transcribe and summarize text"""
__docformat__ = "numpy"

import logging
import os
import tempfile
import warnings

from huggingface_hub import scan_cache_dir
from tqdm import tqdm
from transformers import BartTokenizer, BartForConditionalGeneration, pipeline
import whisper
import yt_dlp

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.forecast.whisper_utils import slugify, write_srt, write_vtt

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


def get_audio(urls):
    temp_dir = tempfile.gettempdir()

    ydl = yt_dlp.YoutubeDL(
        {
            "quiet": True,
            "verbose": False,
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
    model_name: str = "base",
    subtitles_format: str = "vtt",
    verbose: bool = False,
    task: str = "transcribe",
    language: str = None,
    breaklines: int = 0,
    output_dir: str = "",
):
    if video == "":
        console.print("[red]Please provide a video URL. [/red]")
        return
    else:
        # check to make sure the video is a valid URL with a .com
        if not ((video.startswith("https") or "youtube" in video) and ".com" in video):
            console.print("[red]Please provide a valid video URL. [/red]")
            return

    os.makedirs(output_dir, exist_ok=True)

    console.print(
        "[yellow][DISCLAIMER]: This is a beta feature that uses standard NLP models. More recent"
        " models such as GPT will be added in future releases. [/yellow]"
    )
    console.print("")
    console.print("[green]Downloading and Loading NLP Pipelines from cache...[/green]")
    console.print("")

    hf_cache_info = scan_cache_dir()

    # Check if required models are already in cache
    model_cached = False

    # check for bart-large-cnn model
    for cached_repo in hf_cache_info.repos:
        if cached_repo.repo_id == "facebook/bart-large-cnn":
            summarizer = BartForConditionalGeneration.from_pretrained(
                "facebook/bart-large-cnn"
            )
            summary_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
            console.print("[green]facebook/bart-large-cnn found in cache.[/green]")
            model_cached = True
            break

    # download bart-large-cnn model if not in cache
    if not model_cached:
        console.print(
            "[yellow]facebook/bart-large-cnn not found in cache. Download model (1.64G)? (y/n)[/yellow]"
        )
        response = input()
        if response.lower() != "y":
            console.print("[red]Cancelling download and exiting command.[/red]")
            return
        summarizer = BartForConditionalGeneration.from_pretrained(
            "facebook/bart-large-cnn"
        )
        summary_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        console.print(
            "[green]facebook/bart-large-cnn downloaded and saved to cache for future use.[/green]"
        )

    # check for distilbert model
    model_cached = False

    for cached_repo in hf_cache_info.repos:
        if cached_repo.repo_id == "distilbert-base-uncased-finetuned-sst-2-english":
            classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
            )
            console.print(
                "[green]distilbert-base-uncased-finetuned-sst-2-english found in cache.[/green]"
            )
            model_cached = True
            break

    # download distilbert model if not in cache
    if not model_cached:
        console.print(
            "[yellow]distilbert-base-uncased-finetuned-sst-2-english not found"
            " in cache. Download model (275mb)? (y/n)[/yellow]"
        )
        response = input()
        if response.lower() != "y":
            console.print("[red]Cancelling download and exiting command.[/red]")
            return
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
        console.print(
            "[green]distilbert-base-uncased-finetuned-sst-2-english downloaded and"
            " saved to cache for future use.[/green]"
        )

    console.print("All NLP Pipelines loaded.")
    console.print("")

    console.print("Transcribing and summarizing...")
    print(f"video: {video}")
    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection."
        )

    model = whisper.load_model(model_name)

    try:
        audios = get_audio([video])
    except Exception as e:
        console.print(f"[red]Error downloading audio: {e}[/red]")
        console.print(
            "This command requires the command-line tool ffmpeg to be installed on your system,"
            " which is available from most package managers using the following commands:\n"
        )
        console.print(
            "[yellow]On Ubuntu or Debian: sudo apt update && sudo apt install ffmpeg[/yellow]\n"
        )
        console.print("[yellow]On Arch Linux: sudo pacman -S ffmpeg[/yellow]\n")
        console.print(
            "[yellow]On MacOS using Homebrew (https://brew.sh/): brew install ffmpeg[/yellow]\n"
        )
        console.print(
            "[yellow]On Windows using Chocolatey (https://chocolatey.org/): choco install ffmpeg[/yellow]\n"
        )
        console.print(
            "[yellow]On Windows using Scoop (https://scoop.sh/): scoop install ffmpeg[/yellow]\n"
        )
        return

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

        # original text length
        original_text_length = len(all_text)

        # split the text into chunks
        chunk_size = 1024
        chunks = [
            all_text[i : i + chunk_size] for i in range(0, len(all_text), chunk_size)
        ]

        # process each chunk and concatenate the summaries
        summary_text = ""

        # tqdm is used to show a progress bar
        for chunk in tqdm(chunks):
            # encode the chunk using the tokenizer
            inputs = summary_tokenizer(
                chunk, return_tensors="pt", truncation=True, max_length=1024
            )

            # generate a summary using the model
            summary_ids = summarizer.generate(
                inputs["input_ids"], num_beams=4, max_length=100, early_stopping=True
            )
            summary = summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            # concatenate the summaries and add a new line character
            summary_text += summary + "\n"

        # initialize sentiment scores
        # sentiment analysis
        sentiment_size = 512
        positive_score = 0.0
        negative_score = 0.0
        total_length = 0
        for i in range(0, len(summary_text), sentiment_size):
            # process each chunk and compute sentiment analysis
            chunk = summary_text[i : i + sentiment_size]
            chunk_sentiment = classifier(chunk)[0]
            chunk_sentiment_label = chunk_sentiment["label"]
            chunk_sentiment_score = round(chunk_sentiment["score"], 4)
            if chunk_sentiment_label == "POSITIVE":
                positive_score += chunk_sentiment_score * len(chunk)
            elif chunk_sentiment_label == "NEGATIVE":
                negative_score += chunk_sentiment_score * len(chunk)
            total_length += len(chunk)

        # calculate overall sentiment score
        if total_length > 0:
            positive_percent = positive_score / total_length * 100
            negative_percent = negative_score / total_length * 100
            if positive_percent > 70:
                overall_sentiment_label = "POSITIVE"
                overall_sentiment_score = positive_percent
            elif negative_percent > 70:
                overall_sentiment_label = "NEGATIVE"
                overall_sentiment_score = negative_percent
            else:
                overall_sentiment_label = "NEUTRAL"
                overall_sentiment_score = (positive_percent + negative_percent) / 2
        else:
            overall_sentiment_label = "NEUTRAL"
            overall_sentiment_score = 0.0

        # Write summary and get reduction
        summary_text_length = len(summary_text)
        percent_reduction = round(
            (1 - (summary_text_length / original_text_length)) * 100, 2
        )
        # if there is negative reduction, set to 0
        if percent_reduction < 0:
            percent_reduction = 0

        console.print("")
        console.print("-------------------------")
        console.print(f"Summary: [blue]Reduction: {percent_reduction}%[/blue]")
        if overall_sentiment_label == "NEUTRAL":
            console.print(
                f"Sentiment: {overall_sentiment_label}:{round(overall_sentiment_score, 2)}%"
            )
        else:
            sent_color = "green" if overall_sentiment_label == "POSITIVE" else "red"
            console.print(
                "Sentiment:",
                f"[{sent_color}]{overall_sentiment_label}: {round(overall_sentiment_score, 4)}[/{sent_color}]",
            )

        console.print("-------------------------")
        console.print(f"[green]{summary_text}[/green]")

        # Save subtitles to file
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

        # Save summary to file
        summary_path = os.path.join(output_dir, f"{slugify(title)}_summary.txt")
        with open(summary_path, "w") as f:
            f.write(summary_text)
