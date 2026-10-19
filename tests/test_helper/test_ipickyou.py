from detectmatelibrary.alert_aggregation.basic_concat import BasicConcatAggregation
from detectmatelibrary.detectors.random_detector import RandomDetector
from detectmatelibrary.parsers.drain import DrainParser

import detectmatelibrary.helper.i_pick_you as ipy


class TestFindFromName:
    def test_get_configs(self):
        assert (config := ipy.find_component_from_type("drain_parser", "parsers")) is not None
        assert isinstance(config(), DrainParser)

        assert (config := ipy.find_component_from_type("random_detector", "detectors")) is not None
        assert isinstance(config(), RandomDetector)

        assert (config := ipy.find_component_from_type(
            "basic_concat_aggregator", "alert_aggregators"
        )) is not None
        assert isinstance(config(), BasicConcatAggregation)

        assert ipy.find_component_from_type("aux", "alert_aggregators") is None
