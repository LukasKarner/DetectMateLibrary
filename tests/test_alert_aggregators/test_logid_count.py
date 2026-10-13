
from detectmatelibrary.alert_aggregation.logid_count import Counter


class TestCounter:
    def test_basic_count(self) -> None:
        counter = Counter(max_count=2, overall_size=10)

        assert not counter.add_and_check("a")
        assert not counter.add_and_check("b")
        assert counter.add_and_check("a")
        assert counter.add_and_check("b")

        assert not counter.add_and_check("a")  # should not generate new ones
        assert not counter.add_and_check("b")  # should not generate new ones

    def test_surpass_memory(self) -> None:
        counter = Counter(max_count=2, overall_size=2)

        assert not counter.add_and_check("a")
        assert not counter.add_and_check("b")
        assert not counter.add_and_check("c")

        assert counter.add_and_check("b")
        assert not counter.add_and_check("a")  # was rename by c 
        assert counter.add_and_check("c")
        assert counter.add_and_check("a")  

        assert not counter.add_and_check("a")  # should not generate new ones
        assert not counter.add_and_check("c")  # should not generate new ones