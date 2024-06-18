from abc import ABC
from dataclasses import dataclass
from typing import List

from pykka import ActorRef

from core.common import Point

@dataclass
class Message(ABC):
	sender: ActorRef

@dataclass
class WarriorMessage(Message):
	pass


@dataclass
class ArenaMessage(Message):
	pass

@dataclass
class WarriorStart(WarriorMessage):
	pass

@dataclass
class PositionRequest(WarriorMessage):
	pass

@dataclass
class Attack(WarriorMessage):
	damage: float

@dataclass
class ArenaStart(ArenaMessage):
	pass

@dataclass
class VisionRequest(ArenaMessage):
	pass

@dataclass
class VisionResponse(ArenaMessage):
	vision: List[ActorRef]
	
@dataclass
class PositionResponse(ArenaMessage):
	position: Point

@dataclass
class NewWarrior(ArenaMessage):
	warrior: ActorRef

