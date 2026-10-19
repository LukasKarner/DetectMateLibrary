from detectmatelibrary.common.core import CoreConfig
from detectmatelibrary import detectors, parsers, alert_aggregation

from typing import Optional


__types = {
    "parsers": parsers,
    "detectors": detectors,
    "alert_aggregators": alert_aggregation
}


def find_config_from_name(
    method_type: str, component_type: str
) -> Optional[type[CoreConfig]]:

    for obj in (dir(module := __types[component_type])):
        try:
            if isinstance(conf := getattr(module, obj)(), CoreConfig):
                if conf.method_type == method_type:
                    return getattr(module, obj)  # type: ignore
        except TypeError:
            pass

    return None
