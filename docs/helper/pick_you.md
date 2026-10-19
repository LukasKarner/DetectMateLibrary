# I pick you

Methods that make it easy to choose components solely through configuration settings.

```python
def pickComponent(
    config: CoreConfig | dict[str, Any],
    component_type: str,
    name: Optional[str] = None
) -> CoreComponent:
    """Pick a single component"""


def pickComponents(
    configs: list[CoreConfig | dict[str, Any]],
    component_type: str,
    names: Optional[list[str | None]] = None
) -> list[CoreComponent]:
    """Pick multiple components"""
```

## Usage

```python
--8<-- "docs/examples/others/i_pick_you.py:pickyou"
```
