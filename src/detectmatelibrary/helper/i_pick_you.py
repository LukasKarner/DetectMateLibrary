from detectmatelibrary.common.core import CoreConfig, CoreComponent
from detectmatelibrary import detectors, parsers, alert_aggregation
from detectmatelibrary.schemas import BaseSchema

from typing import Optional


__types = {
    "parsers": parsers,
    "detectors": detectors,
    "alert_aggregators": alert_aggregation
}


def find_component_from_type(
    method_type: str, component_type: str
) -> Optional[type[CoreComponent[BaseSchema, BaseSchema]]]:

    for obj in dir(module := __types[component_type]):
        try:
            if isinstance(conf := getattr(module, obj)(), CoreConfig):  # Look for config
                if conf.method_type == method_type:
                    for comp in dir(__types[component_type]):  # Look for Component
                        try:
                            if isinstance(comp_ := getattr(module, comp)(), CoreComponent):
                                if type(comp_.config) == type(conf):  # noqa: E721
                                    return getattr(module, comp)  # type: ignore
                        except TypeError:
                            pass
        except TypeError:
            pass

    return None
