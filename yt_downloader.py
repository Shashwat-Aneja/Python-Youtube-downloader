#!/usr/bin/env python3
"""Download progressive MP4 video or audio-only streams from a YouTube URL."""

import argparse
import json
import os
import tempfile
import math
import re
import sys
import unicodedata
from pathlib import Path


def select_stream(streams, index=None, itag=None):
    """Select from streams ordered highest-quality first.

    Indexes are one-based for CLI consistency. Without an index, choose the
    first stream, which is the highest-quality stream in the supplied list.
    """
    available = list(streams)
    if not available:
        raise ValueError("No matching streams are available for this video.")
    if itag is not None:
        if index is not None:
            raise ValueError("Select a stream by index or itag, not both.")
        if not isinstance(itag, int) or isinstance(itag, bool) or itag < 1:
            raise ValueError("Stream itag must be a positive integer.")
        matches = [stream for stream in available if getattr(stream, "itag", None) == itag]
        if len(matches) != 1:
            raise ValueError("Requested itag must identify exactly one matching stream.")
        return matches[0]
    if index is None:
        return available[0]
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("Stream index must be a positive integer.")
    if index > len(available):
        raise ValueError(f"Stream index {index} is out of range; choose 1 to {len(available)}.")
    return available[index - 1]


def audio_bitrate_kbps(stream):
    """Extract the numeric bitrate from pytube values such as '160kbps'."""
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)kbps\s*", str(getattr(stream, "abr", "")), flags=re.IGNORECASE)
    value = float(match.group(1)) if match else -1.0
    return value if math.isfinite(value) and value > 0 else -1.0


def sort_audio_streams(streams):
    """Order audio streams by numeric bitrate, not lexicographic text order."""
    return sorted(streams, key=audio_bitrate_kbps, reverse=True)


def video_resolution_height(stream):
    """Return the vertical pixel count for resolutions such as '720p' or '1080p60'."""
    resolution = str(getattr(stream, "resolution", "") or "")
    match = re.fullmatch(r"\s*([1-9]\d*)p(?:[1-9]\d*)?\s*", resolution, flags=re.IGNORECASE)
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


def list_streams(streams, stream_type="Video", exact_size=False):
    """Print available stream quality, frame rate when present, and size."""
    print(f"\nAvailable {stream_type} Streams:")
    for index, stream in enumerate(streams, start=1):
        quality = getattr(stream, "resolution", None) or getattr(stream, "abr", None) or "quality unknown"
        fps = getattr(stream, "fps", None)
        try:
            size = getattr(stream, "filesize" if exact_size else "filesize_approx", None)
        except (AttributeError, KeyError, TypeError, ValueError):
            size = None
        details = [str(quality)]
        if fps is not None:
            details.append(f"{fps}fps")
        valid_size = (
            isinstance(size, (int, float)) and not isinstance(size, bool)
            and 0 <= size <= sys.float_info.max and math.isfinite(size)
        )
        details.append(f"{size / 1_000_000:.2f}MB" if valid_size else "size unknown")
        print(f"{index}. {' - '.join(details)}")


def stream_metadata(streams, include_approx_size=False):
    """Describe stream choices without requesting exact sizes or downloading."""
    records = []
    for index, stream in enumerate(streams, start=1):
        records.append({"index": index, "itag": getattr(stream, "itag", None),
                        "resolution": getattr(stream, "resolution", None),
                        "abr": getattr(stream, "abr", None), "fps": getattr(stream, "fps", None),
                        "mime_type": getattr(stream, "mime_type", None)})
        if include_approx_size:
            try:
                size = getattr(stream, "filesize_approx", None)
            except (AttributeError, KeyError, TypeError, ValueError):
                size = None
            valid = isinstance(size, (int, float)) and not isinstance(size, bool) and 0 <= size <= sys.float_info.max and math.isfinite(size)
            records[-1]["filesize_approx_bytes"] = size if valid else None
    return records


def validate_timeout(value):
    """Return a positive finite download timeout in seconds."""
    if isinstance(value, bool):
        raise ValueError("Download timeout must be a positive finite number.")
    try:
        timeout = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Download timeout must be a positive finite number.") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Download timeout must be a positive finite number.")
    return timeout


def positive_timeout(value):
    try:
        return validate_timeout(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def validate_filename(filename):
    if (not isinstance(filename, str) or not filename.strip() or filename in {".", ".."}
            or "/" in filename or "\\" in filename or "\0" in filename):
        raise ValueError("Filename must be a non-empty file name without path separators.")
    if (any(ord(char) < 32 or char in '<>:"|?*' for char in filename)
            or filename.endswith((".", " "))):
        raise ValueError("Filename must use portable characters and cannot end in a dot or space.")
    stem = unicodedata.normalize("NFKC", filename.split(".", 1)[0]).rstrip(" .").upper()
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in range(1, 10)}
    if stem in reserved:
        raise ValueError("Filename cannot use a reserved device name.")
    return filename


def download_stream(stream, output_dir=None, timeout=None, filename=None, no_overwrite=False, max_size_bytes=None):
    """Download a selected stream with an optional network timeout."""
    if max_size_bytes is not None:
        if not isinstance(max_size_bytes, int) or isinstance(max_size_bytes, bool) or max_size_bytes < 1:
            raise ValueError("Maximum download size must be a positive integer of bytes.")
        size = getattr(stream, "filesize", None)
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError("Cannot enforce the size limit without a valid exact stream size.")
        if size > max_size_bytes:
            raise ValueError(f"Stream size {size} exceeds download limit {max_size_bytes} bytes.")
    timeout_value = validate_timeout(timeout) if timeout is not None else None
    download_options = {"timeout": timeout_value} if timeout_value is not None else {}
    if filename is not None:
        download_options["filename"] = validate_filename(filename)
    if no_overwrite:
        destination = Path(output_dir or ".").expanduser()
        destination.mkdir(parents=True, exist_ok=True)
        name = validate_filename(filename if filename is not None else stream.default_filename)
        final_path = destination / name
        if final_path.exists() or final_path.is_symlink():
            raise FileExistsError(f"Destination already exists: {final_path}")
        with tempfile.TemporaryDirectory(prefix=".download-", dir=destination) as staging:
            staged = Path(stream.download(output_path=staging, **download_options))
            if staged.parent.resolve() != Path(staging).resolve() or staged.is_symlink() or not staged.is_file():
                raise ValueError("Downloader returned an invalid staged file.")
            os.link(staged, final_path)
        print(f"Download complete: {final_path}")
        return str(final_path)
    print(f"\nDownloading: {stream.default_filename}")
    if output_dir is None:
        downloaded_path = stream.download(**download_options)
    else:
        destination = Path(output_dir).expanduser()
        destination.mkdir(parents=True, exist_ok=True)
        downloaded_path = stream.download(output_path=str(destination), **download_options)
    print("\nDownload complete!")
    return downloaded_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download YouTube video or audio streams using pytube")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--list", action="store_true", help="List available stream qualities")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--index", type=int, help="Download a stream by its one-based listed index")
    selection.add_argument("--itag", type=int, help="Download the matching stable YouTube stream format identifier")
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
        "--timeout",
        type=positive_timeout,
        metavar="SECONDS",
        help="Network timeout for each download request (positive finite seconds)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Select audio-only streams ordered by numeric audio bitrate instead of progressive MP4 video",
    )
    parser.add_argument("--exact-size", action="store_true", help="Request exact sizes when listing streams (may make extra network requests)")
    parser.add_argument("--filename", help="Save using this base file name inside the output directory")
    parser.add_argument("--json-streams", action="store_true", help="Print stream metadata as JSON without downloading or requesting sizes")
    parser.add_argument("--no-overwrite", action="store_true", help="Stage downloads and publish only when the destination does not exist")
    parser.add_argument("--max-size-bytes", type=int, help="Reject an oversized download using its exact size (may make an extra metadata request)")
    parser.add_argument("--audio-format", choices=("mp4", "webm"), help="Restrict audio-only streams to a selected container")
    parser.add_argument("--include-approx-size", action="store_true", help="Include approximate byte sizes in JSON stream metadata")
    args = parser.parse_args(argv)
    if args.include_approx_size and not args.json_streams:
        parser.error("--include-approx-size requires --json-streams")
    if args.audio_format is not None and not args.audio_only:
        parser.error("--audio-format requires --audio-only")
    if args.max_size_bytes is not None and args.max_size_bytes < 1:
        parser.error("--max-size-bytes must be positive")
    if args.filename is not None:
        try:
            validate_filename(args.filename)
        except ValueError as exc:
            parser.error(str(exc))
    if args.itag is not None and args.itag < 1:
        parser.error("--itag must be a positive integer")
    if args.index is not None and args.index < 1:
        parser.error("--index must be a positive integer")
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
        if not args.json_streams:
            print(f"\nTitle: {yt.title}")
            print(f"Author: {yt.author}")
        if args.audio_only:
            filters = {"only_audio": True}
            if args.audio_format:
                filters["file_extension"] = args.audio_format
            streams = sort_audio_streams(yt.streams.filter(**filters))
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

        if args.json_streams:
            print(json.dumps(stream_metadata(streams, **({"include_approx_size": True} if args.include_approx_size else {})), allow_nan=False))
            return
        if args.list or args.index is not None or args.itag is not None:
            list_streams(streams, stream_type=stream_type, exact_size=args.exact_size)
        if args.index is not None or args.itag is not None or not args.list:
            try:
                stream = select_stream(streams, args.index, **({"itag": args.itag} if args.itag is not None else {}))
            except ValueError as exc:
                parser.exit(2, f"Error: {exc}\n")
            options = {"filename": args.filename} if args.filename is not None else {}
            if args.no_overwrite:
                options["no_overwrite"] = True
            if args.max_size_bytes is not None:
                options["max_size_bytes"] = args.max_size_bytes
            download_stream(stream, output_dir=args.output_dir, timeout=args.timeout, **options)
    except SystemExit:
        raise
    except Exception as exc:
        parser.exit(1, f"Error processing video: {exc}\n")


if __name__ == "__main__":
    main()
