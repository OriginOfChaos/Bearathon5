from copy import deepcopy
from csv import reader as csv_reader
from random import randint, choice as random_choice

class Bingo:
    def __init__(self, size: int, pokemon: bool, active: bool=True, new: bool=True, list_file: str=""):
        self.size = size
        self.pokemon_bool = pokemon
        self.active = active

        self.grid = []
        self.list = {}
        self.pokemon_list = []
        self.current_pokemon = ""
        self.pokemon_status = 0
        if active:
            self.import_pokemon_list("resources/pokemon.csv")
            if new:
                self.import_list(list_file)
                self.populate()

    @classmethod
    def fromSave(cls, size: int, pokemon: bool, grid: list, obj_list: dict, current_pokemon: str, pokemon_status: int, active: bool=True):
        bingo = cls(size, pokemon, active=active, new=False)
        bingo.grid = grid
        bingo.list = obj_list
        bingo.current_pokemon = current_pokemon
        bingo.pokemon_status = pokemon_status
        return bingo
    
    def toDict(self) -> dict:
        return {"size": self.size,
                "pokemon": self.pokemon_bool,
                "grid": self.grid,
                "list": self.list,
                "current_pokemon": self.current_pokemon,
                "pokemon_status": self.pokemon_status}

    def import_list(self, file: str) -> None:
        """
        Reads in the csv file.
        """
        with open(file, 'r') as f:
            reader = csv_reader(f, delimiter='µ')   # Just make sure the list doesn't have any 'µ' in it.
            for row in reader:
                self.list[row[0]] = 0

    def export_list(self, file:str) -> None:
        """
        Exports the list to file.
        """
        with open(file, "w") as f:
            for i, objective in enumerate(self.list):
                if i < len(self.list)-1:
                    f.write(objective+'\n')
                else:
                    f.write(objective)

    def populate(self) -> None:
        """
        Randomly populates the bingo with items from the list that are not completed yet.
        """
        list_copy = deepcopy(self.list)
        self.grid = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if self.pokemon_bool and i == j and i == int(self.size/2):   # middle square
                    self.current_pokemon = self.pick_random_pokemon()
                    row.append(self.current_pokemon)
                else:
                    key = random_choice(list(list_copy.keys()))
                    while list_copy[key] != 0:
                        list_copy.pop(key)
                        key = random_choice(list(list_copy.keys()))
                    list_copy.pop(key)
                    row.append(key)
            self.grid.append(row)
        self.pokemon_status = 0

    def import_pokemon_list(self, file: str) -> None:
        """
        Imports the pokemon list from file.
        """
        with open(file, "r") as f:
            reader = csv_reader(f, delimiter="µ")
            for row in reader:
                self.pokemon_list.append(row[0])

    def pick_random_pokemon(self) -> str:
        """
        Picks a random pokemon from the list, but makes sure its different than the current pokemon.
        """
        random_poke = self.current_pokemon
        while random_poke == self.current_pokemon:
            random_poke = self.pokemon_list[randint(0, len(self.pokemon_list)-1)]
        return random_poke
    
    def shuffle(self) -> None:
        """
        Shuffles the grid, but nothing gets added or deleted. Central pokemon stays.
        """
        grid_list = []
        for i, row in enumerate(self.grid):
            for j, item in enumerate(row):
                grid_list.append(item)
        
        self.grid = []

        for i in range(self.size):
            row = []
            for j in range(self.size):
                if self.pokemon_bool and i == j and i == int(self.size/2):   # middle square
                    row.append(self.current_pokemon)
                else:
                    index = randint(0, len(grid_list)-1)
                    row.append(grid_list.pop(index))
            self.grid.append(row)

    def replace(self, i: int, j: int, random: bool, new_goal: str="") -> None:
        """
        Replaces the cell at the given coordinates with either a random other objective from the list or a given one. The status is set to 0.
        """
        if random:
            if self.pokemon_bool and i == j and i == int(self.size/2):   # middle square
                self.current_pokemon = self.pick_random_pokemon()
                new_goal = self.current_pokemon
            else:
                old_goal = self.grid[i][j]
                new_goal = old_goal
                while new_goal == old_goal:
                    new_goal = random_choice(list(self.list.keys()))
        else:
            # Add goal to list
            self.list[new_goal] = 0
        self.grid[i][j] = new_goal

    def reset(self) -> None:
        """
        Resets the bingo. All objectives are reset to 0 and a new board is generated.
        """
        for key in self.list:
            self.list[key] = 0
        self.populate()