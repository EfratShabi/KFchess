from core.domain.active_state import ActiveState


class PieceStateTracker:
    def __init__(self, registry):
        self.registry = registry
        self.states = {}

    def get_state(self, position):
        return self.states.get(position)

    def set_state(self, position, state_name, current_time):
        spec = self.registry[state_name]
        self.states[position] = ActiveState(spec=spec, entered_at=current_time)

    def move_state(self, from_position, to_position):
        if from_position in self.states:
            self.states[to_position] = self.states.pop(from_position)

    def advance(self, current_time):
        for position, active in list(self.states.items()):
            if active.is_finished(current_time):
                self.set_state(position, active.spec.next_state_when_finished, current_time)
