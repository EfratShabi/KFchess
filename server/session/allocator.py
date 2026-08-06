from dataclasses import dataclass


@dataclass
class ShardInfo:
    shard_id: str
    active_rooms: int


class GameAllocator:
    """Chooses which Game Server Shard a new match should run on.

    Only one shard exists per process today, so choose_shard always sees
    a single candidate — but the selection itself (lowest load) is real,
    not a stub. Adding geo/multi-shard discovery later means feeding more
    candidates into this same method, not rewriting it.
    """

    @staticmethod
    def choose_shard(candidates: list[ShardInfo]) -> str:
        return min(candidates, key=lambda shard: shard.active_rooms).shard_id
