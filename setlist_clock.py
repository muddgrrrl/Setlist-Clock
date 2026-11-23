#!/usr/bin/env python3
"""Lay out a timed set list from tab-separated titles and durations."""
import argparse
from pathlib import Path
import re


def duration(value):
    if not re.fullmatch(r"\d+(?::[0-5]\d){0,2}", value):
        raise ValueError("use seconds, M:SS, or H:MM:SS")
    seconds = 0
    for part in value.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds


def clock(seconds, relative=False):
    if relative:
        hour, rest = divmod(seconds, 3600)
        minute, second = divmod(rest, 60)
        return f"{hour:02}:{minute:02}:{second:02}"
    days, within = divmod(seconds, 86400)
    hour, rest = divmod(within, 3600)
    minute, second = divmod(rest, 60)
    return f"{hour:02}:{minute:02}:{second:02}" + (f" (+{days}d)" if days else "")


def read_setlist(path):
    tracks = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            name, length = (part.strip() for part in line.rsplit("\t", 1))
            time = duration(length)
            if not name or not time:
                raise ValueError("title and positive duration required")
            tracks.append((name, time))
        except ValueError as error:
            raise ValueError(f"line {number}: expected title<TAB>duration ({error})") from error
    if not tracks:
        raise ValueError("no tracks found")
    return tracks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--start", metavar="HH:MM", help="show wall-clock times at this start")
    parser.add_argument("--gap", default="0", help="gap between tracks, in seconds or M:SS")
    args = parser.parse_args()
    try:
        gap = duration(args.gap)
        if args.start and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", args.start):
            raise ValueError("--start must be a 24-hour HH:MM time")
        start = duration(args.start + ":00") if args.start else 0
        elapsed = 0
        for index, (name, length) in enumerate(read_setlist(args.file)):
            elapsed += gap if index else 0
            timestamp = clock(start + elapsed, relative=args.start is None)
            print(f"{timestamp:<17} {clock(length, relative=True)}  {name}")
            elapsed += length
        print(f"Total             {clock(elapsed, relative=True)}")
        if args.start:
            print(f"Finishes          {clock(start + elapsed)}")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
