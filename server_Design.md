# Kung Fu Chess — Server Architecture Diagram (Phase 1)

                              ┌─────────────────────┐
                              │   Client   │
                              └───────────┬───────────┘
                     ┌──────────────────────┴───────────────────────┐
                     ▼                                                ▼
          ┌─────────────────────┐                       ┌──────────────────────────┐
          │     API Gateway        │                       │        Matchmaker            │
          │ login / history / rooms│                       │  Stateless · Elo · ZSET      │
          └───────────┬───────────┘                       └────────────┬───────────────┘
                     ▼                                                 ▼
          ┌─────────────────────┐                       ┌──────────────────────────┐
          │      PostgreSQL         │                       │     Game Allocator  ★       │
          │  users · Elo · results  │                       │  geo latency + load balance  │
          └─────────────────────┘                       └────────────┬───────────────┘
                                                                       ▼
                                                     ┌────────────────────────────────────┐
                                                     │        Game Server Shard (A)          │
                                                     │  Stateful · Tick 100ms                │
                                                     │  GameEngine = Source of Truth         │
                                                     │  + Recovery handler בפנים (Phase 1)   │
                                                     └──────┬──────────────────┬──────────────┘
                                                            │                  │
                             WebSocket ישיר, בלי Gateway ──┘                  │
                             (Yossi + Dani — אפס Latency)                      ▼
                                                                  ┌─────────────────────────────────┐
                                                                  │  Redis Cluster (Streams) — מוזג ★   │
                                                                  │ room:*:stream — גיבוי + fan-out    │
                                                                  │ room:*:meta — snapshot אחרון       │
                                                                  │ owner+epoch — fencing ל-Recovery   │
                                                                  └────────────────┬────────────────┘
                                                                                    ▼
                                                                  ┌─────────────────────────────────┐
                                                                  │      Spectator Edge Servers ★       │
                                                                  │ consumer group על ה-stream           │
                                                                  │ fan-out לאלפי צופים                  │
                                                                  └─────────────────────────────────┘

                              ┌────────────────────────────────────────────────────┐
                              │        Observability ★ — logs · metrics · health         │
                              │   מזין Liveness Probes. Phase 2 (כשהנפח יצדיק): להוציא     │
                              │   את ה-Recovery handler ל-שירות נפרד, ולפצל NATS מ-Redis   │
                              └────────────────────────────────────────────────────┘
```

## Component Overview

API Gateway (regular HTTP) and Matchmaker (pairing) are two separate entry points from the very first request — each with its own responsibility.
Matchmaker (stateless, Elo-based, ZSET) is responsible only for "who plays whom"; Game Allocator ★ is responsible only for "where it runs" (load / geography) — a split adopted from the team's proposal.
The Game Server Shard is the single source of truth for the match; players connect to it directly over WebSocket, with no gateway in between, to keep real-time latency at zero. Recovery logic (checking the fencing token against Redis, deciding on reassignment) lives as a handler inside the same Shard codebase — not as a separate microservice — since any live Shard can run it, and reconnect volume doesn't yet justify a standalone component.
Redis Cluster (Streams) — merged ★ — is used both for asynchronous backup (Stream+Hash) and for spectator fan-out via Consumer Groups: multiple consumers read the same stream, each at its own pace, without contending. A separate NATS bus will only be added if the topics turn out, in practice, to need separating.
Spectator Edge Servers ★ subscribe as a Consumer Group on the stream and fan out to viewers — fully isolated from the Shard's load (Redis load scales with the number of Edge Servers, not the number of viewers), and can scale independently based on demand. This, together with splitting API Gateway/Matchmaker/Allocator, is justified by concrete load math — not a guess.
Observability ★ monitors every component and feeds the Liveness Probes. Future Phase 2: extract the Recovery handler into its own service and split NATS out from Redis — once real-world volume justifies it.