# Architectural Design Document: High-Scale Chess Server

## 1. Introduction & System Goals
This document outlines the upgraded architectural design for the chess game server, engineered to support:
*   **100 Million** registered users.
*   **10 Million** concurrent active users (CCU).
*   **5 Million** requests per second (approximately 1 Gigabyte/sec network throughput).

To meet these high-scale demands, the system transitions from a localized, monolithic architecture to a distributed cloud architecture based on **Microservices** deployed inside lightweight **Docker containers**.

---

## 2. System Component Breakdown (Container Architecture)
The application is decoupled into autonomous components, each running as an isolated, lightweight container leveraging **Kernel Sharing** to minimize resource overhead:

### Load Balancer
The primary gateway of the system. It intercepts all incoming HTTP/WebSockets traffic from the internet and dynamically distributes it across available authentication and matchmaking servers to prevent single-point overloads.

### Stateless Auth & Matchmaking Services
Stateless microservices responsible for verifying user credentials, handling user registrations, and pairing players with similar skill levels (Elo rating). 
> **Scale Advantage:** Being completely stateless allows hundreds of instances to spin up within fractions of a second via **Autoscaling** during traffic spikes.

### Stateful Game Servers
Stateful microservices. Once a match is made, players are routed to a specific game server instance tasked with running the dedicated game session tick-loop for the duration of the 30–90 second match. These containers are protected against abrupt scale-down events to ensure active games are never interrupted.

---

## 3. Data & Memory Management Layers

To prevent performance bottlenecks and file-locking contentions, we strictly isolate persistent data from real-time transient data:

| Feature | Persistent Data Layer | Transient Data Layer |
| :--- | :--- | :--- |
| **Technology** | PostgreSQL / MySQL | Redis (In-Memory DB) |
| **Data Stored** | User profiles, secure password hashes, historical Elo ratings | Active game session states, live match move-data, player routing maps |
| **Storage Medium** | Hard Disk / SSD (Persistent) | RAM Memory (Ultra-fast, volatile) |

### Security & SQL Injection Prevention
Hardened defense against **SQL Injection** is handled natively within the Repository layer using **Parameterized Queries** with placeholders (`?`). User inputs are treated strictly as isolated data variables and are never evaluated as executable code. 
*   *Note on Error Handling:* Returning generic errors to the client acts merely as a secondary defensive layer to prevent Error-Based SQLi; the primary protection is achieved completely via query parameterization.
*   *Why not SQLite?* SQLite operates on a single database file that locks the entire file on every write operation. Under high concurrent load, this causes immediate write bottlenecks and timeouts.

### Live Communication via Redis Pub/Sub
Each match operates on its own dedicated, isolated **Channel** mapped inside a fast Redis **Hash**. When a player executes a move, Redis awakens and updates *only* the specific game server subscribing to that particular channel, preventing system-wide broadcast storms and maintaining microsecond response times.

---

## 4. System Sequence Diagram: Game Move Lifecycle

The following diagram illustrates how the distributed containers (discovered within the internal network via Docker's internal DNS resolution) communicate end-to-end when a player makes a move:

```text
[Player 1: Yossi]                                          [Player 2: Dani]
      │                                                          │
      ▼ (Connection Request)                                     ▼ (Connection Request)
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Load Balancer                                    │
└──────────────────────┬──────────────────────────────────┬───────────────────┘
                       │ (Smart Load Routing)             │
                       ▼                                  ▼
┌────────────────────────────────────────┐      ┌─────────────────────────────┐
│    Stateless Auth Container 1          │      │    Stateless Auth Container 2 │
└──────────────────────┬─────────────────┘      └─────────────────┬───────────┘
                       │ (Secure Parameterized DB Auth)             │
                       ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Central Matchmaker Container                         │
│         - Pairs Yossi and Dani; assigns room_123 on Game Server A.          │
│         - Establishes isolated Redis channel: `game_room_123`.               │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Central In-Memory RAM (Redis)                       │
│                   [Active Channel: game_room_123]                           │
└──────────────────────▲──────────────────────────────────▲───────────────────┘
                       │ (Server A Subscribes)            │ (Server B Subscribes)
                       │                                  │
┌──────────────────────┴─────────────────┐      ┌─────────┴───────────────────┐
│     Stateful Game Server A             │      │     Stateful Game Server B  │
│    (Connected to Yossi via WS)         │      │   (Connected to Dani via WS)│
└──────────────────────▲─────────────────┘      └─────────────────┬───────────┘
                       │                                  │
                       │ (1. Yossi moves a piece)         │ (3. Server B pushes move)
                       │ (2. Server A Publishes to Ch.123)│
                       │                                  ▼
                [Player 1: Yossi]                          [Player 2: Dani]



Execution Steps BreakdownConnection & Load Balancing: Yossi and Dani connect to the platform. The Load Balancer evenly routes their traffic to independent, scaling authentication containers.Matchmaking & Routing: The Matchmaker service pairs the players based on Elo, assigns them to an active room identifier (room_123), and stores a highly optimized routing key map within Redis.Channel Subscription: The respective game servers hosting each player subscribe to the isolated game_room_123 event stream in Redis.Live Move Transmission: Yossi moves a chess piece $\rightarrow$ Game Server A intercepts the action and publishes the state payload directly to channel game_room_123 inside Redis $\rightarrow$ Redis transmits the event in sub-milliseconds strictly to Game Server B (which is listening to that specific stream) $\rightarrow$ Game Server B pushes the updated board layout live to Dani's UI via the active WebSocket connection.Session Teardown: Once the match concludes, the definitive match result is transmitted to the external persistent PostgreSQL database, and the transient keys are purged from the Redis RAM space to optimize resource efficiency.