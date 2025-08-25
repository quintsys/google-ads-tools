#!/usr/bin/env python3
from google_auth_oauthlib.flow import InstalledAppFlow
import argparse

SCOPE = ["https://www.googleapis.com/auth/adwords"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--console", action="store_true",
                    help="Use copy/paste flow instead of local browser")
    args = ap.parse_args()

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPE)
    creds = (flow.run_console() if args.console else flow.run_local_server(port=0, prompt="consent"))
    print("\nREFRESH TOKEN:\n" + creds.refresh_token)

if __name__ == "__main__":
    main()
