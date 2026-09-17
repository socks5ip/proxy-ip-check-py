# proxy-ip-check

> Identify an IP's **ASN owner, ISP, country and network type** — residential, hosting/datacenter, proxy/VPN or mobile carrier.

**Zero dependencies. No API key. Works from a single function call or the command line.**

This is the Python port of the npm package [`proxy-ip-check`](https://www.npmjs.com/package/proxy-ip-check) (JS source: [proxy-ip-check](https://github.com/socks5ip/proxy-ip-check)) — same behaviour, same data sources.

---

## Install

```bash
pip install proxy-ip-check
```

## Command line

```bash
$ proxy-ip-check 8.8.8.8

  IP           8.8.8.8
  ASN          AS15169
  AS name      GOOGLE
  ISP          Google LLC
  Location     United States, California, Mountain View
  Type         HOSTING / DATACENTER
  Source       ip-api.com
```

```bash
$ proxy-ip-check 114.114.114.114

  IP           114.114.114.114
  ASN          AS137702
  AS name      China Mobile
  ISP          China Mobile
  Location     China, Jiangsu, Nanjing
  Type         PROXY / VPN RANGE
  Source       ip-api.com
```

Multiple IPs and JSON output (for scripts, pipelines and LLM agents):

```bash
proxy-ip-check 8.8.8.8 1.1.1.1 --json
```

## Python API

```python
from proxy_ip_check import lookup, is_residential

r = lookup('8.8.8.8')
print(r['asn'])               # 'AS15169'
print(r['asName'])            # 'GOOGLE'
print(r['networkType'])       # 'hosting'
print(r['isResidentialLike']) # False

# Quick boolean check (True / False / None when undecidable)
if is_residential(ip) is False:
    print('this looks like a datacenter IP — risky for account operations')
```

## Why ASN instead of "IP type databases"

Third-party IP-type databases *guess*. The **ASN is a registration fact** — an IP either belongs to a consumer broadband ISP or to a datacenter / cloud provider. Most anti-fraud systems evaluate this signal first, which is why it is the most reliable single indicator of whether an IP will be treated as a real household user.

| Signal | Reliability | Notes |
|---|---|---|
| **ASN ownership** | Highest | Registration fact — cannot be faked by the IP holder |
| IP-type database label | Medium | Varies between databases |
| Blacklist / abuse score | Medium | Depends on the list's freshness |
| DNS / WebRTC leaks | Supporting | Catches misconfiguration, not IP quality |

## Returned fields

| Field | Meaning |
|---|---|
| `ip` | Queried IP (echoed back from the source) |
| `asn` | e.g. `AS15169` |
| `asName` | AS / organisation name, e.g. `GOOGLE` |
| `isp` | ISP name |
| `org` | Organisation |
| `country` / `countryCode` / `region` / `city` | Location |
| `networkType` | `residential` \| `hosting` \| `proxy` \| `mobile` \| `unknown` |
| `isResidentialLike` | `True` = looks residential, `False` = looks datacenter/proxy, `None` = no signal |
| `source` | Which data source answered |

## Data sources & limits

1. **ip-api.com** (primary) — free tier, **45 requests/minute per IP**. Exposes `hosting`, `proxy` and `mobile` flags.
2. **ipinfo.io** (fallback) — used automatically when the primary fails.

Please respect the free-tier rate limit. For bulk validation, add a throttle (e.g. one request per 1.5 s) and cache results.

## Related resources

- **Price comparison (20+ providers)**: https://socks5ip.com.cn/jiagezhongxin/
- **Free IP quality checker (web)**: https://socks5ip.com.cn/ip-check-center/
- **Dataset: proxy IP pricing in China (CSV/JSON)**: https://github.com/socks5ip/proxy-ip-pricing
- **Source code (this Python package)**: https://github.com/socks5ip/proxy-ip-check-py
- **npm version**: https://www.npmjs.com/package/proxy-ip-check

## License

MIT

## Disclaimer

`proxy-ip-check` queries public IP-intelligence APIs and reports what they return. It is a diagnostic helper, not a guarantee: an IP labelled `residential` can still be blocked by a specific platform, and different risk engines weigh signals differently. Always verify against the platform you actually care about.
