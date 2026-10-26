"""The event timeline that drives the synthesized parts of the data (SCENARIO.md is the source).

Real prices come from EIA and are never adjusted by these events; the events move only what has no public source:
differentials, basis, forward curves, refinery runs, freight and deal flow. Each event names the scenario section it
comes from.
"""
import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    key: str
    start: dt.date
    end: dt.date
    label: str
    scenario: str  # the SCENARIO.md heading it comes from

    def active(self, day):
        return self.start <= day <= self.end

    def ramp(self, day):
        """0 outside the event, rising to 1 at its midpoint and back to 0 at its end."""
        if not self.active(day):
            return 0.0
        span = max((self.end - self.start).days, 1)
        x = (day - self.start).days / span
        return 1 - abs(2 * x - 1)


EVENTS = (
    Event("diesel_scarcity", dt.date(2026, 9, 20), dt.date(2026, 10, 20),
          "Distillate scarcity: Russia extends its export ban, China suspends October product exports",
          "October 5, 2026: Diesel became a policy market as well as a commodity market"),
    Event("g7_release", dt.date(2026, 10, 2), dt.date(2026, 10, 20),
          "G7 coordinated release of 100 million barrels of emergency stocks",
          "October 5, 2026: Diesel became a policy market as well as a commodity market"),
    Event("hurricane_isaias", dt.date(2026, 10, 7), dt.date(2026, 10, 15),
          "Hurricane Isaias: Gulf offshore shut-ins, Gulf Coast refinery and terminal disruption",
          "October 9 and 12, 2026: Operational disruption"),
    Event("freight_spike", dt.date(2026, 9, 1), dt.date(2026, 10, 20),
          "Tanker freight up more than 300% since mid-August; arbitrage closing",
          "October 9 and 12, 2026: Physical trading and logistics"),
    Event("turnaround_season", dt.date(2026, 9, 15), dt.date(2026, 10, 31),
          "Autumn turnaround season",
          "October 5, 2026: North American operational risk"),
)

BY_KEY = {e.key: e for e in EVENTS}

# Refineries the hurricane takes down, and by how much of capacity at the event's peak (scenario, not an MPC fact).
HURRICANE_RUN_CUTS = {"GV": 0.45, "GB": 0.20}
# Turnarounds: refinery code, start, end (scenario, not MPC's schedule).
TURNAROUNDS = (("RB", dt.date(2026, 9, 21), dt.date(2026, 10, 12)), ("AN", dt.date(2026, 10, 1), dt.date(2026, 10, 25)))


def intensity(key, day):
    return BY_KEY[key].ramp(day)


def active_events(day):
    return [e.key for e in EVENTS if e.active(day)]
