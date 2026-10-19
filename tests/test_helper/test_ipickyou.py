from detectmatelibrary.alert_aggregation.basic_concat import BasicConcatAggregation
from detectmatelibrary.detectors.random_detector import RandomDetector
from detectmatelibrary.parsers.drain import DrainParser, DrainConfig

import detectmatelibrary.helper.i_pick_you as ipy


class TestFindFromName:
    def test_get_configs(self):
        assert (comp := ipy._find_component_from_type("drain_parser", "parsers")) is not None
        assert isinstance(comp(), DrainParser)

        assert (comp := ipy._find_component_from_type("random_detector", "detectors")) is not None
        assert isinstance(comp(), RandomDetector)

        assert (comp := ipy._find_component_from_type(
            "basic_concat_aggregator", "alert_aggregators"
        )) is not None
        assert isinstance(comp(), BasicConcatAggregation)

        assert ipy._find_component_from_type("aux", "alert_aggregators") is None


class TestPickComponets:
    def test_pick_component_dict(self):
        config = {
            "detectors": {
                "TestDetector": {"method_type": "random_detector"}
            }
        }
        comp = ipy.pickComponent(
            name="TestDetector", config=config, component_type="detectors"
        )

        assert isinstance(comp, RandomDetector)

    def test_pick_component_dict_no_name(self):
        config = {
            "detectors": {
                "TestDetector": {"method_type": "random_detector"}
            }
        }
        comp = ipy.pickComponent(config=config, component_type="detectors")

        assert isinstance(comp, RandomDetector)

    def test_pick_component(self):
        config = DrainConfig()
        comp = ipy.pickComponent(
            name="Drain", config=config, component_type="parsers"
        )

        assert isinstance(comp, DrainParser)

    def test_pick_component_no_name(self):
        config = DrainConfig()
        comp = ipy.pickComponent(config=config, component_type="parsers")

        assert isinstance(comp, DrainParser)
