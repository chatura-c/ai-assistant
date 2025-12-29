import os
import sys
from enum import Enum
from pathlib import Path
from platformdirs import user_config_path

class SystemOs(Enum):
    LINUX = 'linux'
    WINDOWS = 'win32'
    MACOS = 'darwin'
    UNKNOWN = 'unknown'

class DesktopEnv(Enum):
    HYPRLAND = 'hyprland'
    GNOME = 'gnome'
    KDE = 'kde'
    SWAY = 'sway'
    WINDOWS = 'windows'
    UNKNOWN = 'unknown'

class Compositor(Enum):
    WAYLAND = 'wayland'
    X11 = 'x11'
    WINDOWS = 'windows'
    UNKNOWN = 'unknown'

class Host:
    APP_ID = "ai_assistant"

    @classmethod
    def get_system(cls) -> SystemOs:
        raw_os = sys.platform.lower()
        return next((s for s in SystemOs if s.value == raw_os), SystemOs.UNKNOWN)

    @classmethod
    def get_desktop(cls) -> DesktopEnv:
        system = cls.get_system()
        raw_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        
        if system == SystemOs.WINDOWS:
            return DesktopEnv.WINDOWS
        
        if "hyprland" in raw_desktop or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
            return DesktopEnv.HYPRLAND
            
        return next((d for d in DesktopEnv if d.value in raw_desktop), DesktopEnv.UNKNOWN)

    @classmethod
    def get_compositor(cls) -> Compositor:
        system = cls.get_system()
        raw_session = os.environ.get("XDG_SESSION_TYPE", "").lower()
        
        if system == SystemOs.WINDOWS:
            return Compositor.WINDOWS
            
        if "wayland" in raw_session:
            return Compositor.WAYLAND
        if "x11" in raw_session:
            return Compositor.X11
            
        return Compositor.UNKNOWN

    @classmethod
    def get_config_dir(cls) -> Path:
        return user_config_path(appname=cls.APP_ID)

    @classmethod
    def ensure_config_exists(cls) -> Path:
        path = cls.get_config_dir()
        path.mkdir(parents=True, exist_ok=True)
        return path


