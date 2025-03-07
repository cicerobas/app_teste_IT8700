from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Param:
    id: int
    tag: str
    va: float
    vb: float
    ia: float
    ib: float


@dataclass
class Step:
    id: int
    step_type: int
    description: str
    duration: float
    input_source: int
    channel_params: Dict[int, int]


@dataclass
class TestData:
    group: str
    model: str
    customer: str
    input_type: str
    input_sources: List[int]
    channels: Dict[int, str]
    params: List[Param]
    steps: List[Step]

    def __post_init__(self):
        self.steps = [Step(**step) if isinstance(step, dict) else step for step in self.steps]
        self.params = [Param(**param) if isinstance(param, dict) else param for param in self.params]
