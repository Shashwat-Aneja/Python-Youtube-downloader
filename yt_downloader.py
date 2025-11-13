#!/usr/bin/env python3
"""
yt_downloader.py

A clean, simple YouTube video downloader CLI tool.
Uses pytube to fetch YouTube streams and download videos.

Usage:
    python yt_downloader.py <YouTube_URL>
    python yt_downloader.py <YouTube_URL> --list
"""

import argparse
from pytube import YouTube
import sys


def list_streams(yt: YouTube):
    print("\nAvailable Video Streams:")
    streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
    for i, stream in enumerate(streams, start=1):
        print(f"{i}. {stream.resolution} — {stream.fps}fps — {round(stream.filesize / 1_000_000, 2)}MB")
    return streams


def download_stream(stream):
    print(f"\nDownloading: {stream.default_filename}")
    stream.download()
    print("\nDownload complete!")


def main():
    parser = argparse.ArgumentParser(description="Simple YouTube video downloader using pytube")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--list", action="store_true", help="List available resolutions")
    parser.add_argument("--index", type=int, help="Choose resolution by index (when using --list first)")
    args = parser.parse_args()

    try:
        yt = YouTube(args.url)
    except Exception as e:
        print(f"Error: Invalid URL or connection issue.\n{e}")
        sys.exit(1)

    print(f"\nTitle: {yt.title}")
    print(f"Author: {yt.author}")

    if args.list:
        streams = list_streams(yt)
        if args.index:
            idx = args.index - 1
            if idx < 0 or idx >= len(streams):
                print("Error: Invalid index.")
                sys.exit(1)
            download_stream(streams[idx])
        sys.exit(0)

    # Default download: highest resolution progressive MP4
    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").last()
    download_stream(stream)


if __name__ == "__main__":
    main()
