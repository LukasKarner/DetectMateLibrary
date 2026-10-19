
# --8<-- [start:example_1]
from detectmatelibrary.alert_aggregation.basic_concat import BasicConcatAggregation

import detectmatelibrary.schemas as sc


aggregations_config = {
    "alert_aggregators": {
        "BasicConcatAggregator": {
            "method_type": "basic_concat_aggregator",
            "buffer_size": 3,
            "deduplicate_values": False,
            "auto_config": False,
        }
    }
}


input_ = sc.DetectorSchema({
    "detectorID": "1",
    "detectorType": "dummy",
    "alertID": "2",
    "detectedTimestamp": 0,
    "logIDs": ["logID1"],
    "score": 0.2,
    "logTimestamps": [-1],
    "description": "hello there",
    "receivedTimestamp": 1,
    "alertDetails": {"99 problems": "but logs aint one"}
})

alert_aggregator = BasicConcatAggregation(
    "BasicConcatAggregator", aggregations_config
)
alert_aggregator.process(input_)

# --8<-- [end:example_1]
