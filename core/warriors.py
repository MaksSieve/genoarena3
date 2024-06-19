
from dataclasses import dataclass
from enum import Enum
import logging

from random import randint
from typing import Any, List
from pykka import ActorRef, ThreadingActor
import pykka

from core.common import Point, distance
import core.messages as messages


class WarriorState(Enum):
	IDLE = 0
	WAITING_VISION = 1
	WAITING_POSITIONS = 2
	HUNTING = 3
	DEAD = 4

@dataclass
class Target:
	ref: ActorRef
	pos: Point

class Warrior(ThreadingActor):
	vision = []
	target = None

	state: WarriorState

	def __init__(self, name: str, arena: ActorRef, position: Point, genome: Genome | None) -> None:
		super().__init__()

		self.name = name

		self.logger = logging.getLogger(self.name)
		self.logger.info(f"name: {self.name}, ref: {self.actor_ref}")
		self.position: Point = position

		self.max_hp = 10
		self.hp = self.max_hp

		self.collision_rad = 0.5
		self.attack_rad = 1.5
		self.speed = 1.5

		self.attack_roll = lambda: randint(2,4)

		self.arena = arena

		self.state = WarriorState.IDLE

		self.targetBuffer: List[Target] = []

		self.target: Target = None

		self.unsuccessfull_moves_counter = 0

	
	def on_receive(self, message: messages.WarriorMessage) -> Any:

		self.logger.debug(f'Got message {message}')

		match type(message):
			case  messages.WarriorStart:
				if self.state != WarriorState.DEAD:
					self.state = WarriorState.WAITING_POSITIONS
					pykka.ActorRegistry.broadcast(messages.PositionResponse(
						sender = self.actor_ref,
						position = self.position
					))

			case messages.PositionRequest:
				if self.state != WarriorState.DEAD:
					message.sender.tell(messages.PositionResponse(
						sender = self.actor_ref,
						position = self.position
					))
			
			case messages.VisionResponse:
				self.unsuccessfull_moves_counter = 0
				vision = filter(lambda w: w != self.actor_ref, message.vision)
				self.state = WarriorState.WAITING_POSITIONS
				for w in vision:
					w.tell(messages.PositionRequest(sender = self.actor_ref))
				
			case messages.PositionResponse:
				match self.state:
					case WarriorState.WAITING_POSITIONS:
						self.targetBuffer.append(Target(message.sender, message.position))
						self.target = self.detectTarget()
						self.logger.info(f"Target detected: {self.target} (distance {distance(self.position, self.target.pos)}). Start Hunting")

						self.state = WarriorState.HUNTING
						self.hunt()
					
					case WarriorState.HUNTING:
						if message.sender is self.target.ref:
							if self.unsuccessfull_moves_counter > 3:
						
								self.logger.info("hunt failed....")

								self.state = WarriorState.WAITING_VISION
								self.arena.tell(messages.VisionRequest(sender=self.actor_ref))
							else:
								self.hunt()
		
			case messages.Attack:
				self.hp -= message.damage
				if self.hp <= 0:
					pykka.ActorRegistry.broadcast(messages.Dead(sender = self.actor_ref))
					self.state = WarriorState.DEAD
				else:
					self.state = WarriorState.WAITING_POSITIONS
					self.target.ref.tell(messages.PositionRequest(sender = self.actor_ref))
			
			case messages.Dead:
				if message.sender != self.actor_ref:
					self.targetBuffer = list(filter(lambda t: t.ref != message.sender, self.targetBuffer))
					if len(self.targetBuffer) == 0:
						self.actor_ref.tell(messages.WarriorStop(sender = self.actor_ref))
					elif message.sender is self.target.ref:
						self.target.ref = None
						self.actor_ref.tell(messages.WarriorStart(sender = self.actor_ref))
					else:
						self.hunt()

			case messages.WarriorStop:
				self.state = WarriorState.IDLE
				
	def detectTarget(self):
		min_d = 100*100
		target = None

		for w in self.targetBuffer:
			d = distance(self.position, w.pos)
			if min_d > d:
				target = w
				min_d = d

		return target
	
	def moveToPoint(self, point: Point):
		factor = self.speed / distance(self.position, point)
		d = point - self.position
		new_position = self.position + (d * factor)
		
		self.logger.info(f"Moving to {new_position} (delta-vector: { d * factor})")	
		self.position = new_position

		pykka.ActorRegistry.broadcast(messages.PositionResponse(
			sender = self.actor_ref,
			position = self.position
		))

	def moveToTarget(self):
		self.moveToPoint(self.target.pos)

	def attack(self, ref: ActorRef):
		dmg = self.attack_roll()
		ref.tell(messages.Attack(sender = self.actor_ref, damage = dmg))
		self.logger.debug(f"Attack {ref} with {dmg} damage")
 
	def attackTarget(self):
		self.attack(self.target.ref)


	def hunt(self):
		if (distance(self.position, self.target.pos) > self.attack_rad):
			self.moveToTarget()
			self.target.ref.tell(
				messages.PositionRequest(sender=self.actor_ref)
			)
			self.unsuccessfull_moves_counter += 1
		else:
			self.attackTarget()
			self.target.ref.tell(messages.PositionRequest(sender = self.actor_ref))