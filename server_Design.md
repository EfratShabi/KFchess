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
                          WS Player Gateway (דק) ★ ────────┘                  │
              TLS + rate limit + ticket(room_id+epoch+expiry) פעם אחת בחיבור,   │
              ואז proxy גולמי — לא מפרש הודעות, לא נוגע בלוגיקת משחק             ▼
              (Yossi + Dani — latency זניח, זה לא ה-Gateway החכם שנדחה)
                                                                  ┌─────────────────────────────────┐
                                                                  │  Redis Cluster (Streams) — מוזג      │
                                                                  │ room:*:stream — גיבוי + fan-out    │
                                                                  │ room:*:meta — snapshot אחרון       │
                                                                  │ owner+epoch+lease(TTL) ★ — fencing │
                                                                  │ עצמי-פג-תוקף, מתחדש ע"י Shard חי   │
                                                                  └────────────────┬────────────────┘
                                                                                    ▼
                                                                  ┌─────────────────────────────────┐
                                                                  │      Spectator Edge Servers ★       │
                                                                  │ consumer group על ה-stream           │
                                                                  │ fan-out לאלפי צופים                  │
                                                                  └─────────────────────────────────┘

                              ┌────────────────────────────────────────────────────┐
                              │        Observability ★ — logs · metrics · health         │
                              │   ניטור משלים בלבד — לא מקור האמת לכשל (זה ה-lease TTL)  │
                              │   Roadmap קבוע (לא מותנה): NATS נפרד לצופים — Step 7,      │
                              │   אחרי delta frames ופיצול תהליכים                        │
                              └────────────────────────────────────────────────────┘
```

## Component Overview

API Gateway (regular HTTP) and Matchmaker (pairing) are two separate entry points from the very first request — each with its own responsibility.
Matchmaker (stateless, Elo-based, ZSET) is responsible only for "who plays whom"; Game Allocator ★ is responsible only for "where it runs" (load / geography) — a split adopted from the team's proposal.
The Game Server Shard is the single source of truth for the match. Players connect through a thin WS Player Gateway ★ — not the heavier smart gateway we rejected earlier: it only terminates TLS, applies basic rate limiting, and validates the signed ticket (room_id + epoch + expiry) once at connect time, then becomes a raw pass-through proxy for the rest of the connection's life. It never parses game messages or touches game logic, so it adds negligible latency, not a real hop in the request-handling sense. Recovery logic (checking the fencing token against Redis, deciding on reassignment) lives as a handler inside the same Shard codebase — not as a separate microservice — since any live Shard can run it, and reconnect volume doesn't yet justify a standalone component.
Redis Cluster (Streams) — merged — is used both for asynchronous backup (Stream+Hash) and for spectator fan-out via Consumer Groups: multiple consumers read the same stream, each at its own pace, without contending. Fencing now uses owner + epoch + a self-expiring lease (TTL) ★: the live Shard renews its own lease in Redis every few seconds; if it crashes, the lease simply expires on its own, with no dependency on an external health-check deciding "it's dead." Observability's liveness probes become a secondary monitoring signal, not the primary failure-detection mechanism.
Spectator Edge Servers ★ subscribe as a Consumer Group on the stream and fan out to viewers — fully isolated from the Shard's load (Redis load scales with the number of Edge Servers, not the number of viewers), and can scale independently based on demand. This, together with splitting API Gateway/Matchmaker/Allocator, is justified by concrete load math — not a guess.
Observability ★ provides supplementary monitoring for every component, but failure detection itself is driven by the lease TTL above, not by Observability polling. Roadmap (a firm future step, not merely "if needed"): once delta frames and the process split are in place, add a dedicated NATS bus for spectator fan-out (Step 7), separate from Redis, which stays responsible for state/fencing/lease.