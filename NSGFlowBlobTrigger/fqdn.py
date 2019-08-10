import socket
# FQDNs from: docs.microsoft.com/en-us/azure/hdinsight/hdinsight-restrict-outbound-traffic#fqdn-httphttps-dependencies
FQDNS = [
    ('azure.archive.ubuntu.com',80),
    ('security.ubuntu.com',80),
    ('ocsp.msocsp.com',80),
    ('ocsp.digicert.com',80),
    ('wawsinfraprodbay063.blob.core.windows.net',443),
    ('registry-1.docker.io',443),
    ('auth.docker.io',443),
    ('production.cloudflare.docker.com',443),
    ('download.docker.com',443),
    ('us.archive.ubuntu.com',80),
    ('download.mono-project.com',80),
    ('packages.treasuredata.com',80),
    ('security.ubuntu.com',80),
    ('azure.archive.ubuntu.com',80),
    ('ocsp.msocsp.com',80),
    ('ocsp.digicert.com',80)
]


def get_current_ip_for_fqdns(fqdns):
    """
    :param fqdns list: List of fully qualified domain names to retrieve the IP address for.
    """
    FQDN_IPS = []
    for url,port in fqdns:
        ip = socket.gethostbyname(url)
        FQDN_IPS.append((ip, port))
    
    return FQDN_IPS