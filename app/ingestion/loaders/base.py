
from abc import ABC , abstractmethod

class BaseClass (ABC): 
    def __init () :
        pass 
    
    @abstractmethod 
    def Load (self , file_path : str ) -> str:
        " Load Data from the source" 
        pass 
    