"""Document generation scaffolds."""

from .adverse_action import render_adverse_action_notice
from .policy_packet import render_policy_packet

__all__ = ["render_adverse_action_notice", "render_policy_packet"]
