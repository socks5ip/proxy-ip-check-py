# -*- coding: utf-8 -*-
"""proxy-ip-check（Python 版）—— 查询 IP 的 ASN / ISP / 国家 / 网络类型。

零依赖（仅标准库 urllib），无需 API Key。
数据源：ip-api.com（主）→ ipinfo.io（备），与 npm 版行为一致。
"""
import json
import socket
import urllib.request
import urllib.error

__version__ = '1.0.0'

SOURCES = [
    ('ip-api.com', 'http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,'
                   'isp,org,as,asname,proxy,hosting,mobile,reverse,query'),
    ('ipinfo.io', 'https://ipinfo.io/{ip}/json'),
]
UA = 'proxy-ip-check/1.0 (+https://socks5ip.com.cn/ip-check-center/)'


def _get(url, timeout=10):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))


def _classify(hosting=None, proxy=None, mobile=None, org='', isp='', asname=''):
    """把数据源给的布尔字段 + AS 名称，归一成 networkType。"""
    low = ('%s %s %s' % (org or '', isp or '', asname or '')).lower()
    if proxy:
        return 'proxy', False
    if hosting:
        return 'hosting', False
    if mobile:
        return 'mobile', True
    # 没有明确布尔字段时，从 AS 名称猜（关键词表）
    DC = ('amazon', 'google', 'microsoft', 'azure', 'cloud', 'digitalocean', 'linode', 'vultr',
          'ovh', 'hetzner', 'alibaba', 'aliyun', 'tencent', 'huawei', 'oracle', 'idc',
          'datacenter', 'data center', 'hosting', 'server', 'colo', 'leaseweb', 'choopa',
          'contabo', 'rackspace', 'fastly', 'cloudflare', 'akamai')
    RESI = ('chinanet', 'china telecom', 'china unicom', 'china mobile', 'telecom', 'unicom',
            'comcast', 'verizon', 'at&t', 'spectrum', 'vodafone', 'deutsche telekom', 'orange',
            'broadband', 'cable', 'fiber', 'ftth', 'dsl', 'telefonica', 'telia')
    if any(k in low for k in DC):
        return 'hosting', False
    if any(k in low for k in RESI):
        return 'residential', True
    return 'unknown', None


def lookup(ip):
    """查一个 IP。

    返回 dict：
      ip / asn / asName / isp / org / country / countryCode / region / city
      networkType（residential | hosting | proxy | mobile | unknown）
      isResidentialLike（True=像住宅，False=像机房/代理，None=无法判定）
      source（数据源域名）
    """
    last_err = None
    for name, tpl in SOURCES:
        url = tpl.format(ip=ip)
        try:
            j = _get(url)
        except Exception as e:
            last_err = e
            continue
        if name == 'ip-api.com':
            if j.get('status') != 'success':
                last_err = RuntimeError(j.get('message') or 'query failed')
                continue
            ntype, resi = _classify(j.get('hosting'), j.get('proxy'), j.get('mobile'),
                                    j.get('org'), j.get('isp'), j.get('asname'))
            asn = (j.get('as') or '').split(' ')[0] or None
            return {
                'ip': j.get('query') or ip,
                'asn': asn,
                'asName': j.get('asname') or j.get('org') or None,
                'isp': j.get('isp') or None,
                'org': j.get('org') or None,
                'country': j.get('country') or None,
                'countryCode': j.get('countryCode') or None,
                'region': j.get('regionName') or None,
                'city': j.get('city') or None,
                'networkType': ntype,
                'isResidentialLike': resi,
                'source': 'ip-api.com',
            }
        else:  # ipinfo.io
            if j.get('error'):
                last_err = RuntimeError(str(j.get('error')))
                continue
            org = j.get('org') or ''
            asn = org.split(' ')[0] if org.startswith('AS') else None
            ntype, resi = _classify(None, None, None, org, '', org)
            return {
                'ip': j.get('ip') or ip,
                'asn': asn,
                'asName': org or None,
                'isp': org or None,
                'org': org or None,
                'country': j.get('country') or None,
                'countryCode': j.get('country') or None,
                'region': j.get('region') or None,
                'city': j.get('city') or None,
                'networkType': ntype,
                'isResidentialLike': resi,
                'source': 'ipinfo.io',
            }
    raise RuntimeError('all sources failed: %s' % (last_err or 'unknown'))


def is_residential(ip):
    """便捷判断：返回 True / False / None（无法判定）"""
    try:
        return lookup(ip).get('isResidentialLike')
    except Exception:
        return None
