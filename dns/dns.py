from cache import Cache
from dnslib import DNSRecord, RCODE

TRUST_SERVER = "77.88.8.1"


class DNS:
    def __init__(self):
        self.cache = Cache()
        self.cache.load_cache("cache")

    def process(self, query):
        try:
            query = DNSRecord.parse(query)
            query_key = (query.q.qtype, query.q.qname)
            rdata = self.cache.get_cache(query_key)
            if rdata:
                response = DNSRecord(header=query.header)
                response.add_question(query.q)
                response.rr.extend(rdata)
                print(f"Найденые записи в кэше:\n{response}",
                      end="\n\n")
                return response.pack()
            response = query.send(TRUST_SERVER, 53, timeout=5)
            response = DNSRecord.parse(response)
            if response.header.rcode == RCODE.NOERROR:
                records_by_type = {}
                for rr_section in (
                        response.rr, response.auth,
                        response.ar):
                    for rr in rr_section:
                        if (rr.rtype, rr.rname) not in records_by_type:
                            records_by_type[(rr.rtype, rr.rname)] = []
                        records_by_type[(rr.rtype, rr.rname)].append(rr)
                        self.cache.update_cache((rr.rtype, rr.rname),
                                                records_by_type[
                                                    (rr.rtype, rr.rname)],
                                                rr.ttl)

            return response
        except Exception:
            return None
