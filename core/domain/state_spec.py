from dataclasses import dataclass


@dataclass
class StateSpec:
    name: str
    speed_m_per_sec: float
    next_state_when_finished: str
    is_loop: bool
    duration_ms: float | None  

    def is_finished(self, elapsed_ms):
        if self.is_loop:
            return False
        return elapsed_ms >= self.duration_ms
