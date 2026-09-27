"""QR codes for the coffee card, and the floating cards that show them (partials/qr-btc.html, qr-ln.html).

- Bitcoin on-chain: a BIP21 URI (bitcoin:<address>), which every wallet reads.
- Lightning: the LNURL of the Lightning Address (LUD-01 bech32 of the LUD-16 URL). Every Lightning
  wallet scans an LNURL; not all of them scan a plain "user@domain".
Each card also has an "Open in my wallet" link with the same URI, for visitors already on a phone.

Needs segno (pip install segno).
"""
import html
import os

import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BTC_ADDRESS = "bc1qlwrptn0jgnexylsycpecpqrekl7zert5hsrxv9"
LN_ADDRESS = "satoshi@gabrielrcl.dev"
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32(hrp, data):
    """BIP173 bech32 without the 90-character limit, as LNURL uses it."""
    def polymod(values):
        gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
        chk = 1
        for v in values:
            top = chk >> 25
            chk = (chk & 0x1FFFFFF) << 5 ^ v
            for i in range(5):
                chk ^= gen[i] if (top >> i) & 1 else 0
        return chk

    acc, bits, words = 0, 0, []
    for byte in data:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            words.append((acc >> bits) & 31)
    if bits:
        words.append((acc << (5 - bits)) & 31)
    expanded = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    mod = polymod(expanded + words + [0] * 6) ^ 1
    checksum = [(mod >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(CHARSET[w] for w in words + checksum)


def lnurl(address):
    user, domain = address.split("@")
    return bech32("lnurl", f"https://{domain}/.well-known/lnurlp/{user}".encode()).upper()


# The button and its floating card; page.src.html shows it on hover (mouse) or tap (touch).
POPOVER = """<span class="qr-wrap">
                <button type="button" class="copy qr-btn" aria-expanded="false" aria-controls="{id}" aria-label="QR code"><svg class="ic"><use href="#lu-qr-code"/></svg></button>
                <span class="qr-pop" id="{id}" role="group" aria-label="{label}: QR code">
                  <span class="qr-title">{icon}{label}</span>
                  <span class="qr-box"><img src="{img}" alt="{alt}" width="200" height="200"></span>
                  <span class="qr-hint"><span class="en">Scan it with the wallet on your phone.</span><span class="pt">Escaneie com a carteira do celular.</span></span>
                  <a class="btn primary small qr-open" href="{uri}"><svg class="ic"><use href="#lu-wallet"/></svg><span class="en">Open in my wallet</span><span class="pt">Abrir na carteira</span></a>
                </span>
              </span>
"""


def main():
    ln = lnurl(LN_ADDRESS)
    codes = [
        ("qr-btc", "assets/qr-bitcoin.svg", f"bitcoin:{BTC_ADDRESS}",
         '<svg class="ic" style="color:#f7931a"><use href="#si-bitcoin"/></svg>', "Bitcoin on-chain", "QR code of the Bitcoin address"),
        ("qr-ln", "assets/qr-lightning.svg", f"lightning:{ln}",
         '<img class="ic" src="assets/lightning.svg" alt="">', "Lightning", "QR code of the Lightning address"),
    ]
    for pid, img, uri, icon, label, alt in codes:
        segno.make(uri, error="m").save(os.path.join(ROOT, img), kind="svg", scale=8, border=0, dark="#0b1530", light=None, xmldecl=False)
        with open(os.path.join(ROOT, "partials", f"{pid}.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(POPOVER.format(id=pid, img=img, uri=html.escape(uri), icon=icon, label=label, alt=alt))
    print("LNURL", ln)
    print("partials/qr-btc.html, partials/qr-ln.html, assets/qr-bitcoin.svg, assets/qr-lightning.svg")


if __name__ == "__main__":
    main()
