

class SearchResult:
    path: list
    distance: float
    visited: int
    time_taken: float
    def __init__(self, path, distance, visited, time_taken):
        self.path = path
        self.distance = distance
        self.visited = visited
        self.time_taken = time_taken

