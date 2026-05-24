"""REST quick tour (sync). Run with:  SIFTING_API_KEY=sft_… python examples/rest.py"""

import os

from siftingio import SiftingAPIError, SiftingClient, auto_paginate


def main() -> None:
    with SiftingClient(api_key=os.environ.get("SIFTING_API_KEY")) as client:
        # 1. Live snapshot
        trade = client.last.trade("crypto", "BTCUSD")
        print("BTC last trade:", trade["p"], "@", trade["t"])

        # 2. Fundamentals
        profile = client.stocks.profile("AAPL")
        print(f"{profile['name']} ({profile['ticker']}) — {profile.get('sic_description')}")

        ratios = client.stocks.ratios("AAPL")
        latest = ratios.get("latest") or {}
        print("Latest net margin:", latest.get("net_margin"))

        # 3. Historical bars (gzip negotiated automatically)
        bars = client.crypto.bars("ETHUSD", start="2024-01-01", end="2024-01-02", interval="1h")
        print(f"Got {len(bars['data'])} ETH bars")

        # 4. Auto-paginated 10-K filings
        count = 0
        for filing in auto_paginate(
            lambda cursor: client.stocks.filings("AAPL", cursor=cursor, form="10-K")
        ):
            count += 1
            if count <= 3:
                print("10-K:", filing["filed_at"], filing["accession"])
        print(f"Total 10-Ks: {count}")

        # 5. Markets + economic calendar
        status = client.markets.status("us_equities")
        print("US equities open?", status["data"].get("is_open"))

        cal = client.economic_calendar.list(impact="high", limit=5)
        print(f"{cal['count']} high-impact events upcoming")


if __name__ == "__main__":
    try:
        main()
    except SiftingAPIError as err:
        raise SystemExit(f"API error {err.status} ({err.code}): {err.message}") from err
