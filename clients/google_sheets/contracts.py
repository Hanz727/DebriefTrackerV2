from dataclasses import dataclass, field


@dataclass
class Columns:
    date_column: list[str] = field(default_factory=list)
    fl_name_column: list[str] = field(default_factory=list)
    squadron_column: list[str] = field(default_factory=list)
    rio_name_column: list[str] = field(default_factory=list)
    plt_name_column: list[str] = field(default_factory=list)
    tail_number_column: list[str] = field(default_factory=list)
    weapon_type_column: list[str] = field(default_factory=list)
    weapon_column: list[str] = field(default_factory=list)
    target_column: list[str] = field(default_factory=list)
    target_angels_column: list[str] = field(default_factory=list)
    angels_column: list[str] = field(default_factory=list)
    speed_column: list[str] = field(default_factory=list)
    range_column: list[str] = field(default_factory=list)
    hit_column: list[str] = field(default_factory=list)
    destroyed_column: list[str] = field(default_factory=list)
    qty_column: list[str] = field(default_factory=list)
    msn_nr_column: list[str] = field(default_factory=list)
    msn_name_column: list[str] = field(default_factory=list)
    event_column: list[str] = field(default_factory=list)
    notes_column: list[str] = field(default_factory=list)
