import pygame

from src.board.constants import BOARD_SIZE


class Renderer:
    def __init__(self, cell_size=60, speed_ms=200, step_by_step=False):
        self.cell_size = cell_size
        self.speed_ms = speed_ms
        self.step_by_step = step_by_step

        self.width = BOARD_SIZE * cell_size
        self.height = BOARD_SIZE * cell_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Learn2Slither")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        self.waiting_step = False
        self.running = True

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

            if self.step_by_step and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.waiting_step = False

        return True

    def draw(self, grid, info_text=None):
        if not self.running:
            return False

        self._handle_events()
        if not self.running:
            return False

        self.screen.fill((30, 30, 30))

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = grid[row][col]

                x = col * self.cell_size
                y = row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                color = (240, 240, 240)  # empty
                if value == 1:
                    color = (0, 200, 0)    # green apple
                elif value == 2:
                    color = (220, 0, 0)    # red apple
                elif value == 3:
                    color = (0, 120, 255)  # snake head
                elif value == 4:
                    color = (0, 180, 255)  # snake body

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (60, 60, 60), rect, 1)

        if info_text:
            text_surface = self.font.render(info_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (8, 8))

        pygame.display.flip()

        if self.step_by_step:
            self.waiting_step = True
            while self.waiting_step and self.running:
                self._handle_events()
                self.clock.tick(30)
        else:
            self.clock.tick(1000 // max(1, self.speed_ms))

        return self.running

    def close(self):
        pygame.quit()
