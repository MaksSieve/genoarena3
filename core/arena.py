from dataclasses import dataclass
import logging
from typing import Any, List
from pykka import ActorRef, Future, ThreadingActor
import pykka
from core.common import Point
import core.messages as messages
from core.warriors import Warrior

@dataclass
class GameObject:
	position: Point

	
@dataclass
class Obstacle(GameObject):
	pass

class Arena(ThreadingActor):

	warriors: List[ActorRef] = []

	def __init__(self, name: str, x_size: float, y_size: float) -> None:
		super().__init__()

		self.name = name

		self.logger = logging.getLogger('Arena_' + name)
		self.x_size, self.y_size = x_size, y_size


	def on_receive(self, message: messages.ArenaMessage) -> Any:

		self.logger.debug(f"Got message: {message}")

		match type(message):
			case messages.ArenaStart:
				pykka.ActorRegistry.broadcast(messages.WarriorStart(sender = self.actor_ref), Warrior)

			case messages.VisionRequest:
				message.sender.tell(
					messages.VisionResponse(
						sender = self.actor_ref, 
						vision =  self.warriors
						)
					)
			
			case messages.NewWarrior:
				self.warriors.append(message.warrior)



		 

