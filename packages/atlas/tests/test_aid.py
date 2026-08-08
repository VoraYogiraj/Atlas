from atlas.core.aid import AtlasID


def test_generate_unique_ids():
    aid1 = AtlasID.generate()
    aid2 = AtlasID.generate()

    assert aid1 != aid2


def test_from_string():
    aid = AtlasID.generate()

    restored = AtlasID.from_string(str(aid))

    assert restored == aid


def test_serialization():
    aid = AtlasID.generate()

    assert aid.to_dict()["aid"] == str(aid)