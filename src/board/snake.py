class Snake:
    def __init__(self, body):
        self.body = body

    @property
    def head(self):
        if not self.body:
            return None
        return self.body[0]

    def move(self, position):
        self.body.insert(0, position)
        self.body.pop()

    def grow(self, position):
        self.body.insert(0, position)

    def shrink(self):
        if self.body:
            self.body.pop()

    def length(self):
        return len(self.body)
