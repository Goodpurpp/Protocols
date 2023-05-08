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
                response_record = DNSRecord(header=query.header)
                response_record.add_question(query.q)
                response_record.rr.extend(rdata)
                print(f"Found records in cache:\n{response_record}",
                      end="\n\n")
                return response_record.pack()
            response = query.send(TRUST_SERVER, 53, timeout=5)
            response_record = DNSRecord.parse(response)
            if response_record.header.rcode == RCODE.NOERROR:
                records_by_type = {}
                for rr_section in (
                        response_record.rr, response_record.auth,
                        response_record.ar):
                    for rr in rr_section:
                        if (rr.rtype, rr.rname) not in records_by_type:
                            records_by_type[(rr.rtype, rr.rname)] = []
                        records_by_type[(rr.rtype, rr.rname)].append(rr)
                        print(f"Cached record:\n{rr}", end="\n\n")
                        self.cache.update_cache((rr.rtype, rr.rname),
                                                records_by_type[
                                                    (rr.rtype, rr.rname)],
                                                rr.ttl)

            return response
        except Exception as e:
            print(f"Error: {e}")
            return None
