from dataclasses import dataclass
from enum import Enum

class SystemOs(Enum):
    Linux = 'linux'
    Windows = 'win32'


class DesktopEnv(Enum):
    Hyprland = 'hyprland'


class Compositor(Enum):
    Wayland = 'wayland'


@dataclass
class Host:
    system: SystemOs
    desktop: DesktopEnv
    compositor: Compositor

    def detect_host_env(self) -> Host:
        system = platform.system().lower()
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        compositor = os.environ.get("XDG_SESSION_TYPE", "")
        # signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")

        return Host(system, desktop, compositor)



