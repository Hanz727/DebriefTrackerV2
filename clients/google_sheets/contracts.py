from dataclasses import dataclass, field
import numpy as np

@dataclass
class CVW17Database:
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
