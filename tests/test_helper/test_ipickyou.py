from detectmatelibrary.alert_aggregation.basic_concat import BasicConcatAggregationConfig
from detectmatelibrary.detectors.random_detector import RandomDetectorConfig
from detectmatelibrary.parsers.drain import DrainConfig

import detectmatelibrary.helper.i_pick_you as ipy


class TestFindFromName:
    def test_get_configs(self):
        assert (config := ipy.find_config_from_name("drain_parser", "parsers")) is not None
        assert isinstance(config(), DrainConfig)

        assert (config := ipy.find_config_from_name("random_detector", "detectors")) is not None
        assert isinstance(config(), RandomDetectorConfig)

        assert (config := ipy.find_config_from_name(
            "basic_concat_aggregator", "alert_aggregators"
        )) is not None
        assert isinstance(config(), BasicConcatAggregationConfig)

        assert ipy.find_config_from_name("aux", "alert_aggregators") is None
