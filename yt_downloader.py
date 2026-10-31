#!/usr/bin/env python3
"""Download progressive MP4 video or audio-only streams from a YouTube URL."""

import argparse
import re
import sys
from pathlib import Path


def select_stream(streams, index=None):
    """Select from streams ordered highest-quality first.

    Indexes are one-based for CLI consistency. Without an index, choose the
    first stream, which is the highest-quality stream in the supplied list.
    """
    available = list(streams)
    if not available:
        raise ValueError("No matching streams are available for this video.")
    if index is None:
        return available[0]
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("Stream index must be a positive integer.")
    if index > len(available):
        raise ValueError(f"Stream index {index} is out of range; choose 1 to {len(available)}.")
    return available[index - 1]


def audio_bitrate_kbps(stream):
    """Extract the numeric bitrate from pytube values such as '160kbps'."""
    match = re.search(r"\d+(?:\.\d+)?", str(getattr(stream, "abr", "")))
    return float(match.group(0)) if match else -1.0


def sort_audio_streams(streams):
    """Order audio streams by numeric bitrate, not lexicographic text order."""
    return sorted(streams, key=audio_bitrate_kbps, reverse=True)


def video_resolution_height(stream):
    """Return the vertical pixel count for resolutions such as '720p' or '1080p60'."""
    resolution = str(getattr(stream, "resolution", "") or "")
    match = re.match(r"^\\s*(\\d+)p", resolution, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def filter_video_streams(streams, max_resolution=None):
    """Keep video streams at or below an optional vertical-resolution cap."""
    available = list(streams)
    if max_resolution is None:
        return available
    if (
        not isinstance(max_resolution, int)
        or isinstance(max_resolution, bool)
        or max_resolution < 1
    ):
        raise ValueError("Maximum resolution must be a positive integer.")
    return [
        stream
        for stream in available
        if (height := video_resolution_height(stream)) is not None
        and height <= max_resolution
    ]


def list_streams(streams, stream_type="Video"):
    """Print available stream quality, frame rate when present, and size."""
    print(f"\nAvailable {stream_type} Streams:")
    for index, stream in enumerate(streams, start=1):
        quality = getattr(stream, "resolution", None) or getattr(stream, "abr", None) or "quality unknown"
        fps = getattr(stream, "fps", None)
        size = getattr(stream, "filesize", None)
        details = [str(quality)]
        if fps is not None:
            details.append(f"{fps}fps")
        details.append(f"{size / 1_000_000:.2f}MB" if size is not None else "size unknown")
        print(f"{index}. {' - '.join(details)}")


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
    parser = argparse.ArgumentParser(description="Download YouTube video or audio streams using pytube")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--list", action="store_true", help="List available stream qualities")
    parser.add_argument("--index", type=int, help="Download a stream by its one-based listed index")
    parser.add_argument(
        "--output-dir",
        help="Directory where the download will be saved (created if it does not exist)",
    )
    parser.add_argument(
        "--max-resolution",
        type=int,
        metavar="HEIGHT",
        help="Limit video streams to this vertical resolution (for example, 720)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Select audio-only streams ordered by numeric audio bitrate instead of progressive MP4 video",
    )
    args = parser.parse_args(argv)
    if args.audio_only and args.max_resolution is not None:
        parser.error("--max-resolution cannot be combined with --audio-only")
    if args.max_resolution is not None and args.max_resolution < 1:
        parser.error("--max-resolution must be a positive integer")

    try:
        from pytube import YouTube
    except ImportError:
        parser.exit(1, "Error: pytube is not installed. Install it with pip install pytube.\n")

    try:
        yt = YouTube(args.url)
        print(f"\nTitle: {yt.title}")
        print(f"Author: {yt.author}")
        if args.audio_only:
            streams = sort_audio_streams(yt.streams.filter(only_audio=True))
            stream_type = "Audio"
        else:
            streams = list(
                yt.streams.filter(progressive=True, file_extension="mp4")
                .order_by("resolution")
                .desc()
            )
            streams = filter_video_streams(streams, args.max_resolution)
            stream_type = "Video"

        if not streams:
            parser.exit(1, f"Error: no matching {stream_type.lower()} streams are available for this video.\n")

        if args.list or args.index is not None:
            list_streams(streams, stream_type=stream_type)
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
