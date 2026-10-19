
# --8<-- [start:pickyou]
from detectmatelibrary.detectors.random_detector import RandomDetectorConfig

import detectmatelibrary.helper.i_pick_you as ipy

configs = [
    {
        "detectors": {
            "a": {"method_type": "random_detector"}
        }
    },
    RandomDetectorConfig(),
]
names = ["a", "b"]

components = ipy.pickComponents(
    configs=configs, names=names, component_type="detectors"
)
print(len(components))  # 2

# --8<-- [end:pickyou]
