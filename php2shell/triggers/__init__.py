# Python 3.11
from .base import Trigger, TriggerResult, probe
from .oom import OOMTrigger
from .fatal import FatalTrigger

__all__ = ["Trigger", "TriggerResult", "probe", "OOMTrigger", "FatalTrigger"]