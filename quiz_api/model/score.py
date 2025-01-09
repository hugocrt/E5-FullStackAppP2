class Score:
    def __init__(self, playerName: str, score: str, date: str):
        self.player_name = playerName
        self.score = score
        self.date = date

    def to_json(self):
        """
        Create a JSON from an Object.
        :return: The dictionary containing the question data.
        """
        return self.__dict__

    @classmethod
    def from_json(cls, json_data):
        """
        Create a Question instance from a dictionary (or JSON).
        :param json_data: dict: The dictionary containing the question data.
        :return: Question: The Question instance created from the dictionary.
        """
        return cls(**json_data)
