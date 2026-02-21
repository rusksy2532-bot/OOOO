from app.services.filter_presets import FILTER_PRESETS


def test_filter_presets_have_required_names():
    names = {item["name"] for item in FILTER_PRESETS}
    assert names == {"PostMigration_Expansion", "Early_LowCap", "Late_Scalp"}
