from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSpan:
    entered_at: int
    current_time: int

    def elapsed_ms(self):
        return self.current_time - self.entered_at
