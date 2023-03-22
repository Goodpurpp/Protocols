import os
import re
from urllib.request import urlopen
from json import loads
from argparse import ArgumentParser
IP_MAX_LEN = 15
ASN_MAX_LEN = 8
PROVIDER_MAX_LEN = 20
COUNTRY_MAX_LEN = 7
PRIVATE_IP = {
    ('10.0.0.0', '10.255.255.255'),
    ('172.16.0.0', '172.31.255.255'),
    ('192.168.0.0', '192.168.255.255'),
    ('127.0.0.0', '127.255.255.255')
}
ip_regex = r"\([\d.]*\)"


def main():
    parser = ArgumentParser(description="Трассировка автономных систем")
    parser.add_argument("location", type=str, help="Айпи или домен")
    parser.add_argument("-hops", default=64, type=int, help="Максимальный TTL")
    arguments = parser.parse_args()
    for column in trace(arguments.location, arguments.hops):
        print(column)


def trace(location, hops) -> str:
    ttl = 1
    os.system(f"traceroute -q 1 -m {hops} {location} > logs.txt")
    print(f"NUM{' ' * (len(str(hops)) - 1)}|        IP       |   ASN    |   PROVIDER           | COUNTRY | CITY")
    with open("logs.txt", "r") as data:
        ips = re.findall(ip_regex, data.read())
    for ip in ips:
        about_ip = f"{str(ttl) + ' ' * (len(str(hops)) - len(str(ttl)))}  | {ip[1:-1] + ' ' * (IP_MAX_LEN - len(ip[1:-1]))} |"
        if is_public_ip(ip[1:-1]):
            about_ip += get_info(ip[1:-1])
        yield about_ip
        ttl += 1


def get_info(ip) -> str:
    info = loads(urlopen(f"http://ipinfo.io/{ip}/json").read())
    try:
        info_asn = info['org'].split()
        asn = info_asn[0]
        provider = ""
        for i in range(1, len(info_asn)):
            provider += f"{info_asn[i]} "
        return f" {asn + ' ' * (ASN_MAX_LEN - len(asn))} | {provider[:-1] + ' ' * (PROVIDER_MAX_LEN - len(provider[:-1]))}" \
               f" | {info['country'] + ' ' * (COUNTRY_MAX_LEN - len(info['country']))} | {info['city']}"
    except KeyError:
        return f" {' ' * ASN_MAX_LEN} | {' ' * PROVIDER_MAX_LEN} | {info['country'] + ' ' *(COUNTRY_MAX_LEN-len(info['country']))}" \
               f" | {info['city']}"


def is_public_ip(ip):
    for private_ip in PRIVATE_IP:
        if private_ip[0] <= ip <= private_ip[1]:
            return False
    return True


if __name__ == '__main__':
    main()
