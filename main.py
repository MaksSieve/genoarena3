import logging
import os
import signal

import pykka.debug
from core.arena import Arena
from core.common import Point
from core.warriors import Warrior
import core.messages as messages

logging.basicConfig(level=logging.DEBUG)

signal.signal(signal.SIGUSR1, pykka.debug.log_thread_tracebacks)

if __name__ == "__main__":

	print(os.getpid())
	
	arena = Arena.start('Total', 20, 20)

	arena.tell(messages.NewWarrior(sender =  None, warrior = Warrior.start("Loki", arena, Point(0, 0))))
	arena.tell(messages.NewWarrior(sender =  None, warrior = Warrior.start("Thorin", arena, Point(20, 20))))
	# arena.tell(messages.NewWarrior(sender =  None, warrior = Warrior.start("Maximus", arena, Point(10, 10))))

	arena.tell(messages.ArenaStart(sender = None))

	while arena.is_alive():
		pass


