#!/usr/bin/env python3
"""Download a progressive MP4 stream from a YouTube video URL."""

import argparse
import sys
from pathlib import Path


def select_stream(streams, index=None):
    """Select from streams ordered highest-resolution first.

    Indexes are one-based for CLI consistency. Without an index, choose the
    first stream, which is the highest-resolution stream in the supplied list.
    """
    available = list(streams)
    if not available:
        raise ValueError("No progressive MP4 streams are available for this video.")
    if index is None:
        return available[0]
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("Stream index must be a positive integer.")
    if index > len(available):
        raise ValueError(f"Stream index {index} is out of range; choose 1 to {len(available)}.")
    return available[index - 1]


def list_streams(streams):
    print("\nAvailable Video Streams:")
    for index, stream in enumerate(streams, start=1):
        size = getattr(stream, "filesize", None)
        size_label = f"{size / 1_000_000:.2f}MB" if size is not None else "size unknown"
        print(f"{index}. {stream.resolution} — {stream.fps}fps — {size_label}")


def download_stream(stream, output_dir=None):
    """Download a selected stream, optionally creating a destination directory."""
    print(f"\nDownloading: {stream.default_filename}")
    if output_dir is None:
        stream.download()
    else:
        destination = Path(output_dir).expanduser()
        destination.mkdir(parents=True, exist_ok=True)
        stream.download(output_path=str(destination))
    print("\nDownload complete!")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Simple YouTube video downloader using pytube")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--list", action="store_true", help="List available resolutions")
    parser.add_argument("--index", type=int, help="Download a stream by its one-based listed index")
    parser.add_argument(
        "--output-dir",
        help="Directory where the video will be saved (created if it does not exist)",
    )
    args = parser.parse_args(argv)

    try:
        from pytube import YouTube
    except ImportError:
        parser.exit(1, "Error: pytube is not installed. Install it with pip install pytube.\n")

    try:
        yt = YouTube(args.url)
        print(f"\nTitle: {yt.title}")
        print(f"Author: {yt.author}")
        streams = list(
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
        )
        if not streams:
            parser.exit(1, "Error: no progressive MP4 streams are available for this video.\n")

        if args.list or args.index is not None:
            list_streams(streams)
        if args.index is not None or not args.list:
            try:
                stream = select_stream(streams, args.index)
            except ValueError as exc:
                parser.exit(2, f"Error: {exc}\n")
            download_stream(stream, output_dir=args.output_dir)
    except SystemExit:
        raise
    except Exception as exc:
        parser.exit(1, f"Error processing video: {exc}\n")


if __name__ == "__main__":
    main()
