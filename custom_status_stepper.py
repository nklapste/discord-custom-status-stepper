#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Update your Discord custom status"""

import argparse
import datetime
import uuid
import traceback
from time import sleep

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


def chunk_string(string: str, length: int):
    return (string[i : length + i].strip() for i in range(0, len(string), length))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-s",
        "--status-text",
        dest="status_text",
        required=True,
        help="Custom status text to iterate through.",
    )
    parser.add_argument(
        "-tf",
        "--token-file",
        dest="token_file",
        required=True,
        help="Path to file containing the Discord authorization token.",
    )
    return parser


def main():
    args = get_parser().parse_args()
    with open(args.token_file, "r") as f:
        token = f.read().strip()
    for chunk in chunk_string(args.status_text, MAX_STATUS_LENGTH):
        try:
            update_custom_status(
                authorization=token,
                custom_status_text=chunk,
                custom_status_expiry=datetime.datetime.utcnow()
                + datetime.timedelta(minutes=10),
            )
            sleep(60 * 10)
        except Exception:
            print(f"Failed update status with chunk {chunk}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
