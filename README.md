# ASU SDC 2026-27 - Electrical & Controls

Software workspace for the Arizona State University ASME Student Design Competition Electrical/Controls subteam for the 2026-27 season.

The team is developing the electrical, controls, sensing, vision, and autonomous systems for a robot that will compete in **PODIUM**, Stage 1 of the CY2027 ASME Engineering Games.

## The challenge

PODIUM evaluates one robot across five disciplines:

| Discipline | Primary focus |
| --- | --- |
| The Sprint | Speed and agility |
| The Lift | Strength and power |
| The Cycle | Object throughput and handling |
| The Marksman | Accuracy and autonomy |
| The Ascent | Climbing and autonomy |


## Repository layout (might not be completely accurate)

```text
ASU-SDC-2026-27/
|-- README.md                Project overview and contributor orientation
|-- .gitignore               Local and generated files excluded from Git
|-- pyproject.toml           Python package metadata and tooling configuration
|-- src/
|   `-- sdc/
|       |-- main.py          Robot software entry point
|       |-- core/            Shared commands and robot state
|       |-- radio/           Operator-console communications
|       |-- control/         Control logic and coordination
|       |-- motor/           Motor interfaces and actuation
|       |-- sensors/         Sensor interfaces and processing
|       |-- vision/          Camera and vision processing
|       `-- autonomy/        Autonomous behaviors and sequencing
|-- tests/
|   |-- unit/                Isolated software tests
|   |-- integration/         Cross-subsystem tests
|   `-- hardware/            Tests requiring robot hardware
|-- scripts/                 Pi setup, deployment, and launch helpers
|-- config/                  Runtime configuration examples
|-- docs/                    Architecture, hardware, and protocol notes
`-- .github/                 GitHub contribution templates
```

## Working agreements

- Document electrical interfaces, safety assumptions, and radio protocol changes in `docs/`. We want to be able to justify why we implemented what we did, go through the reasoning, and it'll help if new people join or you forget or whatever.

## Development status

9/27 - This repository currently contains only the base architecture. There is no operational software yet. Add implementation and tests alongside each subsystem as hardware choices and team interfaces are actually put in place.

