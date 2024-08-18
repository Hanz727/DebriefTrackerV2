from dataclasses import dataclass, field
import numpy as np

@dataclass
class CVW17Database:
    size: int = field(default=0)
    date: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    fl_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    squadron: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    rio_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    plt_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    tail_number: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    weapon_type: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    weapon: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    target: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    target_angels: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    angels: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    speed: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    range: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    hit: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    destroyed: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    qty: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    msn_nr: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    msn_name: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    event: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    notes: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))

@dataclass
class MsnDataEntry:
    type: int
    weapon_name: str
    dl_callsign: str
    tail_number: str
    pilot_name: str
    rio_name: str
    tgt_name: str
    tgt_tname: str
    speed: float
    angels: int
    angels_tgt: int
    range: int
    destroyed: bool
    hit: bool
