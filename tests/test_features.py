from src.features.extractor import FeatureExtractor
from src.providers.historical_provider import HistoricalProvider


def test_extractor_builds_basic_features():
    provider = HistoricalProvider("data/raw")
    events = provider.get_events("SAMPLEMINT111")
    features = FeatureExtractor().build("SAMPLEMINT111", events)
    assert features.mint == "SAMPLEMINT111"
    assert features.price_usd is not None
