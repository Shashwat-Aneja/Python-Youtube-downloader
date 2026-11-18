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
