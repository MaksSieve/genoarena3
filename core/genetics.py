from random import randint
from typing import Callable, List

class Gene:
    structure: List[int]
    structure_length: int
    nucleobase_magnitude: int

    def __init__(self, structure, magnitude):
        self.structure_length = len(structure)
        self.nucleobase_magnitude = magnitude  
        self.structure = structure        

    '''
    mutation_fun = (magnitude: int, nucleobasis_expression: int) -> int
    '''
    def mutate(self, mutation_fun: Callable[[int, int], int]):
        for i in range(0, len(self.structure)):
            self.structure[i] = mutation_fun(self.nucleobase_magnitude, self.structure[i])

    def roll(self) -> int:
        mean_expr = sum(self.structure)/len(self.structure)
        max_expr = max(self.structure)

        return int(max_expr - self.structure[randint(0, len(self.structure)-1)] + mean_expr / 2)


class Genome:

    strength: Gene
    constitution: Gene
    dexterity: Gene
    wisdom: Gene

    gene_len: int
    gene_mag: int

    def __init__(self, gene_len = 10, gene_mag = 10) -> None:
        self.strength = Gene([randint(0, gene_mag) for _ in range(0, gene_len)], gene_mag)
        self.constitution = Gene([randint(0, gene_mag) for _ in range(0, gene_len)], gene_mag)
        self.dexterity = Gene([randint(0, gene_mag) for _ in range(0, gene_len)], gene_mag)
        self.wisdom = Gene([randint(0, gene_mag) for _ in range(0, gene_len)], gene_mag)
        self.gene_len = gene_len
        self.gene_mag = gene_mag

    
    @classmethod
    def __chunks(self, l: List[int], n: int):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @classmethod
    def from_hash(self, hash):
        if isinstance(hash, list[int]):
            chs = list(Genome.__chunks(hash, int(self.gene_len/2)))
            g = self()

            a1, a2 = chs[0], chs[5]
            b1, b2 = chs[7], chs[2]
            c1, c2 = chs[3], chs[6]
            d1, d2 = chs[4], chs[1]


            g.strength = Gene(a1 + a2)
            g.constitution = Gene(b1 + b2)
            g.dexterity = Gene(c1 + c2)
            g.wisdom = Gene(d1 + d2)
            
            return g
        else:
            raise TypeError("hash must be a list of int")

    

    def __hash__(self):
        # generate a hash from the genome sequence
        #
        # initialy genome consttains 4 genes those are splitting in to two pieces:
        # str: a1|a2, dex: b1|b2, const: c1|c2, wis: d1|d2
        #
        # than it recombinates as
        # a1d2b2c1d1a2c2b1

        a1, a2 = self.strength.structure[:int(self.gene_len/2)], self.strength.structure[int(self.gene_len/2):]
        b1, b2 = self.constitution.structure[:int(self.gene_len/2)], self.constitution.structure[int(self.gene_len/2):]
        c1, c2 = self.dexterity.structure[:int(self.gene_len/2)], self.dexterity.structure[int(self.gene_len/2):]
        d1, d2 = self.wisdom.structure[:int(self.gene_len/2)], self.wisdom.structure[int(self.gene_len/2):]

        return (a1 + d2 + b2 + c1 + d1 + a2 + c2 + b1)

    def __str__(self) -> str:
        return f"str: {self.strength.structure}\nconst: {self.constitution.structure}\ndex: {self.dexterity.structure}\nwis: {self.wisdom.structure}"

def crossingover(g_left, g_right, magnitude = 0.1):

    g_left_hash, g_right_hash = g_left.__hash__(), g_right.__hash__()

    def generate_indices():
        idc = []
        while len(idc)+1 <= min(len(g_left_hash), len(g_right_hash)) * magnitude:
            idx_candidate = randint(0, min(len(g_left_hash), len(g_right_hash))-1)
            if idx_candidate not in idc:
                idc.append(idx_candidate)
        return idc

    
    idc = generate_indices()

    for i in idc:
        g_left_hash[i], g_right_hash[i] = g_right_hash[i], g_left_hash[i]

    return Genome.from_hash(g_left_hash), Genome.from_hash(g_right_hash)


class PhenoType:

    max_hp: int
    dmg: Callable[[], int]
    vision_depth: int
    speed: int

    def __init__(self, genome: Genome) -> None:
        self.max_hp = (int(sum(genome.constitution.structure) / genome.constitution.structure_length
        + (sum(genome.strength.structure) / 2) / genome.strength.structure_length)) * 100

        def dmg_roll() -> int :
            return genome.strength.roll + int(genome.dexterity.roll / 2)

        self.dmg = dmg_roll

        self.vision_depth = int(sum(genome.wisdom.structure) / (1.5 * genome.wisdom.structure_length))

        self.speed = int(sum(genome.dexterity.structure) / (2 * genome.dexterity.structure_length))
