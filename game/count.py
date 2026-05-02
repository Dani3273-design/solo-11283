class GameCounter:
    def __init__(self):
        self.score = 0
        self.paddle_hits = 0
        self.bricks_remaining = 0
        self.total_bricks = 0

    def reset(self):
        self.score = 0
        self.paddle_hits = 0
        self.bricks_remaining = 0
        self.total_bricks = 0

    def add_score(self, points):
        self.score += points

    def increment_paddle_hits(self):
        self.paddle_hits += 1

    def set_bricks_count(self, count):
        self.total_bricks = count
        self.bricks_remaining = count

    def remove_brick(self):
        if self.bricks_remaining > 0:
            self.bricks_remaining -= 1
