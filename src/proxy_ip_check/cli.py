# -*- coding: utf-8 -*-
"""命令行入口：proxy-ip-check <ip> [<ip> ...] [--json]"""
import sys
import json

from . import lookup, __version__


def _print_human(res):
    nt = res.get('networkType')
    tag = {
        'residential': 'RESIDENTIAL (consumer ISP)',
        'hosting': 'HOSTING / DATACENTER',
        'proxy': 'PROXY / VPN RANGE',
        'mobile': 'MOBILE CARRIER',
        'unknown': 'UNKNOWN (no signal)',
    }.get(nt, nt)
    print('  IP           %s' % res.get('ip'))
    print('  ASN          %s' % (res.get('asn') or '-'))
    print('  AS name      %s' % (res.get('asName') or '-'))
    print('  ISP          %s' % (res.get('isp') or '-'))
    print('  Location     %s' % ', '.join(x for x in (res.get('country'), res.get('region'), res.get('city')) if x))
    print('  Type         %s' % tag)
    print('  Source       %s' % res.get('source'))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ('-h', '--help'):
        print('proxy-ip-check %s — identify an IP\'s ASN, ISP, country and network type.' % __version__)
        print()
        print('Usage:')
        print('  proxy-ip-check 8.8.8.8')
        print('  proxy-ip-check 8.8.8.8 114.114.114.114 --json')
        print()
        print('Data sources: ip-api.com (primary) -> ipinfo.io (fallback). No API key required.')
        print('Homepage: https://socks5ip.com.cn/ip-check-center/')
        return 0
    as_json = '--json' in argv
    ips = [a for a in argv if not a.startswith('-')]
    if not ips:
        print('error: no IP given', file=sys.stderr)
        return 2
    results, failed = [], []
    for ip in ips:
        try:
            results.append(lookup(ip))
        except Exception as e:
            failed.append({'ip': ip, 'error': str(e)})
    if as_json:
        print(json.dumps({'results': results, 'failed': failed}, ensure_ascii=False, indent=2))
        return 0 if not failed else 1
    for i, res in enumerate(results):
        if i:
            print()
        _print_human(res)
    for f in failed:
        print()
        print('  IP           %s' % f['ip'])
        print('  ERROR        %s' % f['error'])
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
