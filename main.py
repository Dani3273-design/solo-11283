import pygame
import threading
import time
import sys

from game.count import GameCounter
from game.run import PhysicsEngine
from game.control import MouseController
from game.ui import UIManager


class GameState:
    START = "start"
    PLAYING = "playing"
    END = "end"


class BrickBreakerGame:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.fps = 60
        
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("打砖块游戏")
        
        self.counter = GameCounter()
        self.physics = PhysicsEngine(self.screen_width, self.screen_height)
        self.controller = MouseController(self.physics)
        self.ui = UIManager(self.screen, self.screen_width, self.screen_height)
        
        self.physics.set_counter(self.counter)
        self.ui.set_physics(self.physics)
        self.ui.set_counter(self.counter)
        
        self.state = GameState.START
        self.won = False
        self.running = True
        self.clock = pygame.time.Clock()
        
        self.physics_thread = None
        self.physics_lock = threading.Lock()
        self.display_lock = threading.Lock()
        self._last_state = None

    def _update_mouse_visibility(self):
        if self.state != self._last_state:
            if self.state == GameState.PLAYING:
                pygame.mouse.set_visible(False)
            else:
                pygame.mouse.set_visible(True)
            self._last_state = self.state

    def _physics_loop(self):
        while self.running:
            if self.state == GameState.PLAYING:
                with self.physics_lock:
                    result = self.physics.update()
                
                if result == "lost":
                    self.state = GameState.END
                    self.won = False
                elif result == "won":
                    self.state = GameState.END
                    self.won = True
            
            time.sleep(1.0 / 120.0)

    def _start_physics_thread(self):
        if self.physics_thread is None or not self.physics_thread.is_alive():
            self.physics_thread = threading.Thread(target=self._physics_loop, daemon=True)
            self.physics_thread.start()

    def _reset_game(self):
        self.counter.reset()
        self.physics.generate_bricks()
        self.physics.reset_ball()
        self.won = False

    def run(self):
        self._start_physics_thread()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif self.state == GameState.START:
                    action = self.ui.handle_start_screen_events(event)
                    if action == "start_game":
                        self._reset_game()
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    with self.physics_lock:
                        self.controller.handle_event(event)
                
                elif self.state == GameState.END:
                    action = self.ui.handle_end_screen_events(event)
                    if action == "restart_game":
                        self._reset_game()
                        self.state = GameState.PLAYING
            
            self._update_mouse_visibility()
            
            with self.display_lock:
                if self.state == GameState.START:
                    self.ui.update_start_screen_display()
                elif self.state == GameState.PLAYING:
                    with self.physics_lock:
                        self.ui.draw_game_screen()
                elif self.state == GameState.END:
                    self.ui.update_end_screen_display(self.won)
            
            self.clock.tick(self.fps)
        
        self.running = False
        if self.physics_thread and self.physics_thread.is_alive():
            self.physics_thread.join(timeout=1.0)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BrickBreakerGame()
    game.run()
