from csv import reader as csv_reader
from random import randint

class Bingo:
    def __init__(self, list_file: str, size: int, pokemon: bool, active: bool=True, populate: bool=True):
        self.list_file = list_file
        self.size = size
        self.pokemon_bool = pokemon
        self.active = active

        self.grid = []
        self.grid_status = []   # 0 = not completed, 1 = completed, >1 = custom status
        self.list = []
        self.pokemon_list = []
        self.current_pokemon = ""
        if active:
            self.import_pokemon_list("resources/pokemon.csv")
            self.update_list(list_file)
            if populate:
                self.populate()

    @classmethod
    def fromSave(cls, list_file: str, size: int, pokemon: bool, grid: list, grid_status: list, active: bool=True):
        bingo = cls(list_file, size, pokemon, active, populate=False)
        bingo.grid = grid
        bingo.grid_status = grid_status
        return bingo
    
    def toDict(self) -> dict:
        return {"list_file": self.list_file,
                "size": self.size,
                "pokemon": self.pokemon_bool,
                "grid": self.grid,
                "grid_status": self.grid_status}

    def update_list(self, file: str) -> None:
        """
        Reads in the csv file. Also used to update it.
        """
        with open(file, 'r') as f:
            reader = csv_reader(f, delimiter='µ')   # Just make sure the list doesn't have any 'µ' in it.
            for row in reader:
                self.list.append(row[0])
        self.list_file = file

    def populate(self, keep_unlocked: bool=False) -> None:
        """
        Randomly populates the bingo with items from the list.
        """
        list_copy = []
        for item in self.list:
            list_copy.append(item)

        self.grid = []
        if not keep_unlocked:
            self.grid_status = []

        for i in range(self.size):
            row = []
            row_status = []
            for j in range(self.size):
                if self.pokemon_bool and i == j and i == int(self.size/2):   # middle square
                    self.current_pokemon = self.pick_random_pokemon()
                    row.append(self.current_pokemon)
                else:
                    row.append(list_copy.pop(randint(0, len(list_copy)-1)))
                if not keep_unlocked:
                    row_status.append(0)
            self.grid.append(row)
            self.grid_status.append(row_status)

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
        grid_status_list = []
        pokemon = ""
        pokemon_status = 0
        for i, row in enumerate(self.grid):
            for j, item in enumerate(row):
                grid_list.append(item)
                grid_status_list.append(self.grid_status[i][j])
        if self.pokemon_bool:
            pokemon = grid_list.pop(int((self.size**2)/2))
            pokemon_status = grid_status_list.pop(int((self.size**2)/2))
        
        self.grid = []
        self.grid_status = []

        for i in range(self.size):
            row = []
            row_status = []
            for j in range(self.size):
                if self.pokemon_bool and i == j and i == int(self.size/2):   # middle square
                    row.append(pokemon)
                    row_status.append(pokemon_status)
                else:
                    index = randint(0, len(grid_list)-1)
                    row.append(grid_list.pop(index))
                    row_status.append(grid_status_list.pop(index))
            self.grid.append(row)
            self.grid_status.append(row_status)

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
                    new_goal = self.list[randint(0, len(self.list)-1)]
        self.grid[i][j] = new_goal
        self.grid_status[i][j] = 0