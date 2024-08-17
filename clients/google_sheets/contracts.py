from dataclasses import dataclass, field


@dataclass
class CVW17Database:
    date: list[str] = field(default_factory=list)
    fl_name: list[str] = field(default_factory=list)
    squadron: list[str] = field(default_factory=list)
    rio_name: list[str] = field(default_factory=list)
    plt_name: list[str] = field(default_factory=list)
    tail_number: list[str] = field(default_factory=list)
    weapon_type: list[str] = field(default_factory=list)
    weapon: list[str] = field(default_factory=list)
    target: list[str] = field(default_factory=list)
    target_angels: list[str] = field(default_factory=list)
    angels: list[str] = field(default_factory=list)
    speed: list[str] = field(default_factory=list)
    range: list[str] = field(default_factory=list)
    hit: list[str] = field(default_factory=list)
    destroyed: list[str] = field(default_factory=list)
    qty: list[str] = field(default_factory=list)
    msn_nr: list[str] = field(default_factory=list)
    msn_name: list[str] = field(default_factory=list)
    event: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


