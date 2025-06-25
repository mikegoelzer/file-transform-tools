from dataclasses import dataclass

@dataclass(frozen=True, slots=True, init=False)
class FileLineRange:
    """
    Represent a range of lines in a file and whether they are at the end of the file.
    The range is inclusive of start and end.
    """
    start_line:int
    num_lines:int   # 0 means empty range starting at start_line
                    # 1 means single line i.e., the entire block is the line at start_line
                    # 2 means two-line range, i.e., the block is the two lines at start_line and start_line + 1
                    # etc.

    def __init__(self, *, start_line: int, num_lines: int):
        # The bare star says that the arguments are keyword-only, not positional.
        if num_lines < 0:
            raise ValueError("num_lines must be >= 0")
        object.__setattr__(self, "start_line", start_line)
        object.__setattr__(self, "num_lines", num_lines)

    def __str__(self):
        if self.num_lines == 0:
            return f"{self.start_line} (empty)"
        elif self.num_lines == 1:
            return f"{self.start_line} (1 line)"
        else:
            return f"{self.start_line}-{self.start_line + self.num_lines - 1} ({self.num_lines} lines)"

    def __repr__(self):
        return f"FileLineRange(start_line={self.start_line}, num_lines={self.num_lines})"
    
    def is_empty(self)->bool:
        return self.num_lines == 0
    
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
        return self.start_line <= n <= self.start_line + self.num_lines - 1
    
    def __len__(self)->int:
        """
        Returns the number of lines in the range.
        """
        if self.is_empty():
            return 0
        else:
            return self.num_lines
