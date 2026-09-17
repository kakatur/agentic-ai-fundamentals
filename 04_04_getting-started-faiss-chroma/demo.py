from local_backends import SearchRecord, upsert_chroma


class InspectingCollection:
    def upsert(self, **payload):
        for record_id, document, metadata in zip(payload["ids"], payload["documents"], payload["metadatas"]):
            print(record_id, document, metadata)


records = [
    SearchRecord("reset", "Reset your password", [1.0, 0.0], {"team": "support"}),
    SearchRecord("invoice", "Download an invoice", [0.0, 1.0], {"team": "billing"}),
]
upsert_chroma(InspectingCollection(), records)
