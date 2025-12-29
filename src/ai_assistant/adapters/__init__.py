from ai_assistant.adapters.hyprland import HyprlandAdapter
from ai_assistant.core.adapter import BaseAdapter
from .null import NullAdapter

_NULL_ADAPTER = NullAdapter()

_REGISTRY = {
    "hyprland": HyprlandAdapter,
}

def get_adapter(app_name: str | None) -> BaseAdapter:
    if not app_name:
        return _NULL_ADAPTER
        
    adapter_class = _REGISTRY.get(app_name.lower())
    if adapter_class:
        return adapter_class()
        
    return _NULL_ADAPTER
