
from abc import ABC , abstractmethod

class BaseLoader (ABC): 
    @classmethod
    @abstractmethod 
    def Load (cls , file_path : str ) -> str:
        " Load Data from the source" 
        pass 
    