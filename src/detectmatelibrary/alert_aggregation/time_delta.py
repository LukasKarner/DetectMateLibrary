from collections.abc import Callable
from typing import Any

from pydantic import NonNegativeFloat

from detectmatelibrary.alert_aggregation.density_clustering import (
    DensityClusteringAggregation,
    DensityClusteringAggregationConfig,
)
from detectmatelibrary.schemas import DetectorSchema


class TimeDeltaAggregationConfig(DensityClusteringAggregationConfig):
    """Configuration of the TimeDeltaAggregation class.

    Args:
        delta (NonNegativeFloat): The time threshold below which two alerts are allocated to the same group.
    """

    method_type: str = "time_delta_aggregator"
    delta: NonNegativeFloat = 10.0


class TimeDeltaAggregation(DensityClusteringAggregation):
    """This class implements alert aggregation by the time-delta method introduced by
    [Landauer et al.](https://dl.acm.org/doi/pdf/10.1145/3510581).
    Two alerts will be assigned to the same group if the time difference between them is below a certain
    threshold delta. The time difference is computed based on the last extracted timestamp of each alert.

    Args:
        name (str): The name identifying this aggregation method.
        config (TimeDeltaAggregationConfig): The configuration of this method.
    """

    def __init__(
        self,
        config: TimeDeltaAggregationConfig | dict[str, Any],
        name: str = "TimeDeltaAggregator",
    ) -> None:
        if isinstance(config, dict):
            config = TimeDeltaAggregationConfig.from_dict(config, name)

        super().__init__(name=name, config=config)
        self.timestamp_extraction_fn: Callable[[DetectorSchema], float] = lambda alert: float(
            alert["logTimestamps"][-1]
        )
        self.description = "Alert aggregation by the time-delta method."

    def single_metric(
        self,
        alert1: DetectorSchema,
        alert2: DetectorSchema,
    ) -> NonNegativeFloat:
        return abs(
            self.timestamp_extraction_fn(alert1) - self.timestamp_extraction_fn(alert2)
        )

    def discard_alert_fn(self, alerts: list[DetectorSchema]) -> list[bool]:
        return [i + 1 != len(alerts) for i in range(len(alerts))]
