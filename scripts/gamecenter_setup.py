"""Creates the game's Game Center leaderboards through the App Store Connect API.

Runs on Codemagic with the the App Store Connect integration, which exposes the API key as
APP_STORE_CONNECT_ISSUER_ID / APP_STORE_CONNECT_KEY_IDENTIFIER / APP_STORE_CONNECT_PRIVATE_KEY.
Safe to run again: leaderboards that already exist are skipped.
"""
import json, os, ssl, sys, time, traceback, urllib.request, urllib.error
import certifi
import jwt  # PyJWT

CTX = ssl.create_default_context(cafile=certifi.where())

BUNDLE = "com.mematiii.capecove"
API = "https://api.appstoreconnect.apple.com/v1"
BOARDS = [("weekly_contest", "Weekly Town Contest", "INTEGER", "DESC"),
          ("player_level", "Town Level", "INTEGER", "DESC")]


def env(*names):
    for n in names:
        if os.environ.get(n):
            return os.environ[n]
    sys.exit("Eksik ortam değişkeni: " + " / ".join(names))


def resolve(v):
    # Codemagic may pass the key as a reference: "@file:/path" or "@env:NAME"
    v = v.strip()
    for _ in range(3):
        if v.startswith("@file:"):
            v = open(os.path.expanduser(v[6:].strip())).read().strip()
        elif v.startswith("@env:"):
            v = os.environ.get(v[5:].strip(), "").strip()
        else:
            break
    return v



ISSUER = resolve(env("APP_STORE_CONNECT_ISSUER_ID"))
KEY_ID = resolve(env("APP_STORE_CONNECT_KEY_IDENTIFIER"))
PRIVATE = resolve(env("APP_STORE_CONNECT_PRIVATE_KEY")).replace("\\n", "\n").strip()
print("Anahtar biçimi:", "PEM" if "BEGIN" in PRIVATE else "çıplak", "| uzunluk", len(PRIVATE), "| ilk karakter", repr(PRIVATE[:1]))
if "BEGIN PRIVATE KEY" not in PRIVATE:
    PRIVATE = "-----BEGIN PRIVATE KEY-----\n" + PRIVATE + "\n-----END PRIVATE KEY-----"


def token():
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "iat": now, "exp": now + 900, "aud": "appstoreconnect-v1"},
                      PRIVATE, algorithm="ES256", headers={"kid": KEY_ID, "typ": "JWT"})


def call(method, path, body=None):
    url = path if path.startswith("http") else API + path
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=180) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw.decode(errors="replace")}


def must(res, what):
    code, data = res
    if code >= 300:
        print(f"HATA ({what}): HTTP {code}\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        sys.exit(1)
    return data



def main():
    app = must(call("GET", f"/apps?filter[bundleId]={BUNDLE}"), "uygulama bulma")["data"]
    if not app:
        sys.exit(f"{BUNDLE} App Store Connect'te bulunamadı")
    app_id = app[0]["id"]
    print("Uygulama:", app_id)

    code, data = call("GET", f"/apps/{app_id}/gameCenterDetail")
    if code == 200 and data.get("data"):
        detail = data["data"]["id"]
    else:
        detail = must(call("POST", "/gameCenterDetails", {"data": {"type": "gameCenterDetails",
                      "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}}), "Game Center'ı açma")["data"]["id"]
    print("Game Center:", detail)

    def list_existing():
        found, url = {}, f"/gameCenterDetails/{detail}/gameCenterLeaderboards?limit=200"
        while url:
            d = must(call("GET", url), "sıralamaları listeleme")
            for x in d.get("data", []):
                found[x["attributes"].get("vendorIdentifier")] = x["id"]
            url = d.get("links", {}).get("next")
        return found

    def ensure_en(lb, vid, name):
        d = must(call("GET", f"/gameCenterLeaderboards/{lb}/localizations?limit=50"), "dil listesi " + vid)
        if any(x["attributes"].get("locale") == "en-US" for x in d.get("data", [])):
            return
        must(call("POST", "/gameCenterLeaderboardLocalizations", {"data": {"type": "gameCenterLeaderboardLocalizations",
            "attributes": {"locale": "en-US", "name": name},
            "relationships": {"gameCenterLeaderboard": {"data": {"type": "gameCenterLeaderboards", "id": lb}}}}}), "English name " + vid)
        print("  English name added:", vid)

    failed = []
    for vid, name, fmt, order in BOARDS:
        for attempt in range(3):
            try:
                existing = list_existing()
                if vid in existing:
                    ensure_en(existing[vid], vid, name)
                    print("Hazır:", vid)
                else:
                    lb = must(call("POST", "/gameCenterLeaderboards", {"data": {"type": "gameCenterLeaderboards",
                        "attributes": {"referenceName": name, "vendorIdentifier": vid, "defaultFormatter": fmt,
                                       "submissionType": "BEST_SCORE", "scoreSortType": order},
                        "relationships": {"gameCenterDetail": {"data": {"type": "gameCenterDetails", "id": detail}}}}}), "sıralama " + vid)["data"]["id"]
                    ensure_en(lb, vid, name)
                    print("Oluşturuldu:", vid, "-", name)
                break
            except (TimeoutError, OSError) as e:
                print(f"  {vid}: bağlantı yavaş ({type(e).__name__}), tekrar deneniyor...")
                time.sleep(10)
        else:
            failed.append(vid)

    if failed:
        print("\n>>> HATA ÖZETİ: şu sıralamalar oluşturulamadı, iş akışını bir kez daha çalıştır:", ", ".join(failed))
        sys.exit(1)
    print("Bitti. Sıralamalar App Store Connect'te hazır.")


try:
    main()
except SystemExit:
    raise
except Exception as e:
    traceback.print_exc()
    print("\n>>> HATA ÖZETİ:", type(e).__name__, str(e)[:300])
    sys.exit(1)
