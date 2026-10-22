"""秘湯WEBの料金一覧から、寒の地獄旅館の各プランの最低料金（大人1名・税込）を取り、prices.json に書く。
GitHub Actions が毎晩これを動かす。読み取りに失敗したときは prices.json を変えない。
"""
import datetime as dt
import json
import re
import sys
import urllib.request

LIST_URL = "https://www.hitou.or.jp/provider/711/plans"  # 寒の地獄旅館（providerId=711）
OUT = "prices.json"


def main():
    req = urllib.request.Request(LIST_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", errors="replace")

    heads = list(re.finditer(r'planId=(\d+)"\s+class="title04__link"', html))
    plans = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(html)
        nums = [int(n.replace(",", "")) for n in
                re.findall(r'cont01__priceNum">\s*([\d,]+)\s*<', html[m.end():end])]
        if nums:
            plans[m.group(1)] = min(nums)

    if len(plans) < 5:
        sys.exit(f"料金一覧の読み取りに失敗した可能性があります（{len(plans)}件）。prices.json は変えません。")

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="minutes")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"checked": now, "plans": plans}, f, ensure_ascii=False, indent=1)
    print(f"{len(plans)}件の料金を保存しました")


if __name__ == "__main__":
    main()
