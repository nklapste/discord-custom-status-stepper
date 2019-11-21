#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Update your Discord custom status"""

import argparse
import datetime
import uuid
from time import sleep
from typing import Generator

import requests


def gen_cfduid() -> str:
    """Spoof a Cloudflare uuid"""
    return str(uuid.uuid4().hex) + str(uuid.uuid4().hex)[0:43]


UPDATE_STATUS_URL: str = "https://discordapp.com/api/v6/users/@me/settings"
DEFAULT_DISCORD_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36"

MAX_STATUS_LENGTH: int = 128


def update_custom_status(
    authorization: str,
    custom_status_text: str,
    custom_status_expiry: datetime.datetime,
):
    """Update the Discord custom status tied to the given authorization"""
    custom_status_expiry = (
        custom_status_expiry.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    )
    custom_status_payload = {
        "custom_status": {
            "text": custom_status_text,
            "expires_at": custom_status_expiry,
        }
    }
    print(
        f"Setting discord custom status text: '{custom_status_text}' expiring at: {custom_status_expiry}"
    )
    resp = requests.patch(
        UPDATE_STATUS_URL,
        json=custom_status_payload,
        headers={
            "user-agent": DEFAULT_DISCORD_USER_AGENT,
            "authorization": authorization,
            "cookie": f"__cfduid={gen_cfduid()}",
        },
    )
    resp.raise_for_status()
    assert resp.json()["custom_status"]["text"] == custom_status_text


def chunk_string(string: str, length: int) -> Generator[str, None, None]:
    return (string[i : length + i].strip() for i in range(0, len(string), length))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-tf",
        "--token-file",
        dest="token_file",
        help="Path to file containing the Discord authorization token.",
    )

    status_text_group = parser.add_argument_group().add_mutually_exclusive_group(
        required=True
    )
    status_text_group.add_argument(
        "-st",
        "--status-text",
        dest="status_text",
        help="Custom status text to iterate through.",
    )
    status_text_group.add_argument(
        "-stf",
        "--status-text-file",
        dest="status_text_file",
        help="Path to file containing the status text to iterate through.",
    )

    parser.add_argument(
        "-c",
        "--chunk-length",
        dest="chunk_length",
        type=int,
        default=MAX_STATUS_LENGTH,
        help=f"Length to chunk long custom status text too (min: 1 maximum: {MAX_STATUS_LENGTH}).",
    )
    parser.add_argument(
        "-t",
        "--iter-time",
        dest="iter_time",
        default=60 * 10,
        type=float,
        help="Time (in seconds) to wait between iterating through custom status text.",
    )
    parser.add_argument(
        "-l",
        "--loop",
        dest="loop",
        action="store_true",
        help="Enable iterating through the custom status text infinitely.",
    )
    return parser


def main():
    args = get_parser().parse_args()
    with open(args.token_file, "r") as f:
        token = f.read().strip()

    if args.status_text_file:
        with open(args.status_text_file, "r") as f:
            status_text = f.read()
    else:
        status_text = args.status_text

    while True:
        for chunk in chunk_string(status_text, args.chunk_length):
            update_custom_status(
                authorization=token,
                custom_status_text=chunk,
                custom_status_expiry=datetime.datetime.utcnow()
                + datetime.timedelta(seconds=args.iter_time),
            )
            sleep(args.iter_time)
        if not args.loop:
            break


if __name__ == "__main__":
    main()
