import base64 as _b64
_κ = 22845
def _ρ(s):
    return _b64.b64decode(s.encode('ascii')).decode('utf-8')
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamma_flip as gf

CSV_PATH = _ρ('YmFyY2hhcnRfb3B0aW9uc19jYXB0dXJlLmNzdg==')
META_PATH = _ρ('Y2FwdHVyZV9tZXRhLmpzb24=')


def main():
    print(_ρ('WzEvMl0gTlEvRVMg7Lqh7LKYIOykkSAoUGxheXdyaWdodCwgdWJ1bnR1LWxhdGVzdCDigJQgZ2xpYmMg66y47KCcIOyXhuydjCkuLi4='))
    gf.run_capture_sync([_ρ('TlE='), _ρ('RVM=')], CSV_PATH)

    if not os.path.exists(CSV_PATH):
        sys.exit(_ρ('7Lqh7LKYIOyLpO2MqDogQ1NWIO2MjOydvOydtCDsg53shLHrkJjsp4Ag7JWK7JWY7Iq164uI64ukLiDsnIQg66Gc6re466W8IO2ZleyduO2VmOyEuOyalC4='))

    print(_ρ('WzIvMl0g7Lqh7LKYIOyLnOqwgSDrqZTtg4DrjbDsnbTthLAg6riw66GdLi4u'))
    now = time.time()
    with open(META_PATH, _ρ('dw=='), encoding=_ρ('dXRmLTg=')) as f:
        json.dump({
            _ρ('Y2FwdHVyZWRfYXRfZXBvY2g='): now,
            _ρ('Y2FwdHVyZWRfYXRfdXRj'): time.strftime(_ρ('JVktJW0tJWRUJUg6JU06JVNa'), time.gmtime(now)),
        }, f)

    print(_ρ('7JmE66OMLiBnaXQg7Luk67CLL+2RuOyLnOuKlCDsm4ztgaztlIzroZzsmrAgeW1s7J20IOydtOyWtOyEnCDsspjrpqztlanri4jri6Qu'))


if __name__ == _ρ('X19tYWluX18='):
    main()
