from dataclasses import dataclass
from core.domain.state_spec import StateSpec


@dataclass
class ActiveState:
    spec: StateSpec
    entered_at: int

    def elapsed_ms(self, current_time):
        return current_time - self.entered_at

    def is_finished(self, current_time):
        return self.spec.is_finished(self.elapsed_ms(current_time))
