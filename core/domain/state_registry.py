from core.domain.state_spec import StateSpec

STATE_REGISTRY = {
    "idle":       StateSpec(name="idle", speed_m_per_sec=0.0, next_state_when_finished="idle", is_loop=True, duration_ms=None),
    "move":       StateSpec(name="move", speed_m_per_sec=1.5, next_state_when_finished="long_rest", is_loop=True, duration_ms=None),
    "jump":       StateSpec(name="jump", speed_m_per_sec=3.0, next_state_when_finished="short_rest", is_loop=False, duration_ms=625.0),
    "short_rest": StateSpec(name="short_rest", speed_m_per_sec=0.0, next_state_when_finished="idle", is_loop=False, duration_ms=625.0),
    "long_rest":  StateSpec(name="long_rest", speed_m_per_sec=0.0, next_state_when_finished="idle", is_loop=False, duration_ms=833.33),
}
