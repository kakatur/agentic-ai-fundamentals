from local_backends import SearchRecord, upsert_chroma
class FakeCollection:
    def upsert(self, **payload): print(payload)
records=[SearchRecord("a","reset password",[1.0,0.0],{"team":"support"}),SearchRecord("b","invoice",[0.0,1.0],{"team":"billing"})]
upsert_chroma(FakeCollection(),records)
