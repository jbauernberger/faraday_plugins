"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
import logging
import os
import socket
import re
from urllib.parse import urlsplit

SERVICE_MAPPER = None
CVE_regex = re.compile(r'CVE-\d{4}-\d{4,7}')
logger = logging.getLogger(__name__)


def get_vulnweb_url_fields(url):
    """Given a URL, return kwargs to pass to createAndAddVulnWebToService."""
    parse = urlsplit(url)
    return {
        "website": "{}://{}".format(parse.scheme, parse.netloc),
        "path": parse.path,
        "query": parse.query
    }


def filter_services():
    global SERVICE_MAPPER
    if not SERVICE_MAPPER:
        logger.debug("Load service mappers")
        filename = os.path.join(os.path.dirname(__file__), "port_mapper.txt")
        with open(filename, encoding='utf-8') as fp:
            SERVICE_MAPPER = list(map(lambda x: x.strip().split('\t'), list(filter(len, fp.readlines()))))
    return SERVICE_MAPPER


def get_all_protocols():
    protocols = [
        'ip',
        'tcp',
        'udp',
        'icmp',
        'sctp',
        'hopopt',
        'igmp',
        'ggp',
        'ip-encap',
        'st',
        'egp',
        'igp',
        'pup',
        'hmp',
        'xns-idp',
        'rdp',
        'iso-tp4',
        'dccp',
        'xtp',
        'ddp',
        'idpr-cmtp',
        'ipv6',
        'ipv6-route',
        'ipv6-frag',
        'idrp',
        'rsvp',
        'gre',
        'ipsec-esp',
        'ipsec-ah',
        'skip',
        'ipv6-icmp',
        'ipv6-nonxt',
        'ipv6-opts',
        'rspf cphb',
        'vmtp',
        'eigrp',
        'ospfigp',
        'ax.25',
        'ipip',
        'etherip',
        'encap',
        'pim',
        'ipcomp',
        'vrrp',
        'l2tp',
        'isis',
        'fc',
        'udplite',
        'mpls-in-ip',
        'hip',
        'shim6',
        'wesp',
        'rohc',
        'mobility-header'
    ]

    for item in protocols:
        yield item


def resolve_hostname(hostname):
    try:
        socket.inet_aton(hostname)  # is already an ip
        return hostname
    except socket.error:
        pass
    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception as e:
        return hostname
    else:
        return ip_address


def get_severity_from_cvss(cvss):
    try:
        if type(cvss) != float:
            cvss = float(cvss)

        cvss_ranges = [(0.0, 0.1, 'info'),
                       (0.1, 4.0, 'low'),
                       (4.0, 7.0, 'med'),
                       (7.0, 9.0, 'high'),
                       (9.0, 10.1, 'critical')]
        for (lower, upper, severity) in cvss_ranges:
            if lower <= cvss < upper:
                return severity
    except ValueError:
        return 'unclassified'


def its_cve(cves:list):
    r = [cve for cve in cves if CVE_regex.match(cve)]
    return r
