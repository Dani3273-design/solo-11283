import pygame


class MouseController:
    def __init__(self, physics_engine):
        self.physics = physics_engine
        self.last_mouse_x = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.last_mouse_x = mouse_x
            self.physics.update_paddle(mouse_x)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.physics.launch_ball()

    def update(self):
        pass
