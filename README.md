# Python YouTube Downloader

A lightweight Python CLI tool for downloading YouTube videos using the `pytube` library.  
Supports listing available resolutions, selecting a specific quality, and downloading the default best progressive video.

---

## 🚀 Features
- Download YouTube videos directly through the command line  
- List available resolutions and file sizes  
- Choose resolution by index  
- Clean error handling  
- Uses only standard Python + pytube  

---

## 📦 Installation

Install the required module:



Stream listings use approximate sizes by default, avoiding a separate exact-size network request per stream. Use `--exact-size` when an exact byte count is needed; missing estimates display “size unknown”.

Use `--filename lesson.mp4 --output-dir ./downloads` for a predictable output name. Directory traversal and path separators in the filename are rejected before metadata is requested.

Unavailable or malformed stream-size metadata now displays “size unknown” without aborting otherwise usable quality listings.

Custom filenames reject Windows drive-relative paths, reserved device names, control characters and trailing dots/spaces, preventing output-directory escapes and device aliases on Windows. Ordinary Unicode filenames remain supported.

Use `--json-streams` for a JSON array of filtered stream choices, including their one-based indexes, itags, resolution, bitrate and MIME type. This mode never downloads or requests exact sizes.

`--no-overwrite` stages a complete download in the destination filesystem and atomically publishes it with an exclusive hard link. Existing files (including concurrently created ones) are preserved, and failed downloads leave no final partial file. Filesystems without hard-link support fail without replacing an existing destination.

`--max-size-bytes N` checks the exact stream size before starting a download or creating its destination. Unknown or invalid sizes fail closed. This option may make an additional metadata request; the default listing and download paths do not request exact sizes for this check.

`--itag 140` selects a matching stream by its format identifier instead of a list position. It is mutually exclusive with `--index` and fails if the filtered stream list has no unique match. Discover identifiers with `--json-streams`; identifiers do not guarantee a format exists on every video.

`--audio-only --audio-format mp4` or `webm` restricts selection to a compatible audio container before sorting or itag selection. It also applies to JSON listings; no matching streams remains a controlled failure.

Programmatic `download_stream` calls now return the path reported by the underlying download operation, including the default-output-directory path. The exclusive no-overwrite mode continues to return its published final path.
