Architecture Layers (strict one-direction imports)
Application → knows nothing about Server or UI
Server      → knows Application, knows nothing about UI

UI          → knows everything

Single Responsibility
Every class and function does exactly ONE thing.
If you find yourself writing "and" when describing what something does — split it.

Examples of violations to avoid:

A receiver that both receives bytes AND parses JSON → split

A manager that both manages connections AND runs business logic → split

No Magic Strings
Every string that crosses a boundary lives in a centralized protocol/constants file.
No exceptions. If a field name appears more than once in the codebase — it belongs in the constants file.

Dataclasses Over Dicts
Use @dataclass for any structured data that is passed between functions.
Use dataclasses.asdict() for final JSON conversion.
Plain dicts are only acceptable for one-off local usage.

Serializer / Deserializer Symmetry
If object_to_dict() exists → dict_to_object() must exist.
Server sends → client must be able to reconstruct real objects.
No parallel class hierarchies — reuse existing Entities classes.

WebSocket Is Transport Only
The WebSocket layer sends and receives bytes/strings.
It must not know about application rules, game/business states, or domain logic.
Concepts belong in the application services or connection managers — not in the transport layer.

Observer / Pub-Sub
Bus lives in Application/Infrastructure — not in Server or UI.
Only synchronous handlers subscribe to the bus.
Async reactions (broadcast) happen after _notify completes, via Queue if needed.

Naming Conventions
Classes: PascalCase
Functions/variables: snake_case

Constants: UPPER_SNAKE_CASE
Private methods: _leading_underscore

When In Doubt
Ask: "does this class know too much?"
Ask: "would I need to change this file if the transport layer changed?"
Ask: "is this string written in more than one place?"