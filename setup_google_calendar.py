"""
Guided helper to generate a Google Calendar OAuth token for Ultron.

Requires a Google Cloud OAuth client secret JSON (Desktop application type).
Usage:
    python setup_google_calendar.py --credentials path/to/client_secret.json \
        --token data/google_calendar_token.json
"""
from __future__ import annotations

import argparse
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Google Calendar token for Ultron.")
    parser.add_argument(
        "--credentials",
        required=True,
        help="Path to the OAuth client secret JSON downloaded from Google Cloud Console.",
    )
    parser.add_argument(
        "--token",
        default="data/google_calendar_token.json",
        help="Output path for the generated token JSON (default: data/google_calendar_token.json).",
    )
    parser.add_argument(
        "--scope",
        action="append",
        dest="scopes",
        help="Additional OAuth scope (may be supplied multiple times). Defaults to Calendar readonly.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Local port to use for OAuth callback during the setup flow (default: 8765).",
    )
    return parser.parse_args()


def load_credentials(token_path: Path, scopes: list[str]) -> Credentials | None:
    if not token_path.exists():
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    except Exception:
        return None
    return None


def main() -> None:
    args = parse_args()

    scopes = args.scopes or SCOPES
    credentials_path = Path(args.credentials).expanduser().resolve()
    token_path = Path(args.token).expanduser().resolve()
    token_path.parent.mkdir(parents=True, exist_ok=True)

    if not credentials_path.exists():
        raise FileNotFoundError(f"Client secret file not found: {credentials_path}")

    creds = load_credentials(token_path, scopes)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
        creds = flow.run_local_server(port=args.port, prompt="consent")

    token_path.write_text(creds.to_json(), encoding="utf-8")
    print(
        f"Google Calendar token saved to {token_path}.\n"
        "Update GOOGLE_CALENDAR_TOKEN_FILE in your .env if needed."
    )


if __name__ == "__main__":
    main()
