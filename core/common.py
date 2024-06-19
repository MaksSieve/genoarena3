
from dataclasses import dataclass
import math


@dataclass
class Point:
	x: float
	y: float

	def __sub__(self, p2):
		return Point(x = self.x - p2.x, y = self.y - p2.y)
	
	def __mul__(self, n: int):
		return Point(self.x * n, self.y * n)
	
	def __add__(self, p2):
		return Point(x = self.x + p2.x, y = self.y + p2.y) 
	
	def __iadd__(self, p2):
		return Point(x = self.x + p2.x, y = self.y + p2.y) 

def distance(p1, p2):
	return math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)

