from typing import NamedTuple

class FileLineRange(NamedTuple):
    """
    Represent a range of lines in a file and whether they are at the end of the file.
    The range is inclusive of start and end.
    """
    start_line:int
    end_line:int

    def __str__(self):
        return f"{self.start_line}-{self.end_line}"

    def __repr__(self):
        return f"FileLineRange(start_line={self.start_line}, end_line={self.end_line})"
    
    def is_empty(self)->bool:
        return self.start_line == 0 and self.end_line == 0
    
    def __contains__(self, n: int) -> bool:
        """
        Return True if n is within the line range (inclusive).
        Example:
          f = FileLineRange(start_line=1, end_line=3)
          (0 in f) == False
          (1 in f) == True
          (2 in f) == True
          (3 in f) == True
          (4 in f) == False
        """
        return self.start_line <= n <= self.end_line
    
    def __len__(self)->int:
        """
        Returns the number of lines in the range.
        """
        if self.is_empty():
            return 0
        else:
            return self.end_line - self.start_line + 1
