#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Update your Discord custom status"""

import uuid

from requests import Session
import datetime


def gen_cfduid() -> str:
    """Spoof a Cloudflare uuid"""
    return str(uuid.uuid4().hex) + str(uuid.uuid4().hex)[0:43]


UPDATE_STATUS_URL = "https://discordapp.com/api/v6/users/@me/settings"
DEFAULT_DISCORD_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36"


def update_custom_status(
    authorization: str,
    custom_status_text: str,
    custom_status_expiry: datetime.datetime = datetime.datetime.utcnow()
    + datetime.timedelta(hours=4),
):
    """Update the Discord custom status tied to the given authorization"""
    session = Session()
    session.headers.update(
        {
            "user-agent": DEFAULT_DISCORD_USER_AGENT,
            "authorization": authorization,
            "cookie": f"__cfduid={gen_cfduid()}",
        }
    )
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
        f"Setting discord custom status text: '{custom_status_text}' expiring at: '{custom_status_expiry}"
    )
    resp = session.patch(UPDATE_STATUS_URL, json=custom_status_payload)
    resp.raise_for_status()
    assert resp.json()["custom_status"]["text"] == custom_status_text


def main():
    with open("token_me.txt", "r") as f:
        token = f.read().strip()
    update_custom_status(token, "hello")


if __name__ == "__main__":
    main()
