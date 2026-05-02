import pygame
import sys


class UIManager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fonts = {}
        self.colors = {
            "background": (20, 30, 50),
            "text": (255, 255, 255),
            "text_highlight": (100, 200, 255),
            "button": (70, 130, 180),
            "button_hover": (100, 160, 210),
            "button_text": (255, 255, 255),
            "paddle": (70, 130, 180),
            "ball": (255, 255, 255),
            "score_text": (255, 215, 0),
        }
        self.physics = None
        self.counter = None
        self.buttons = {}
        self._init_fonts()

    def _init_fonts(self):
        pygame.font.init()
        font_sizes = {
            "title": 64,
            "subtitle": 32,
            "instruction": 24,
            "button": 28,
            "score": 24,
            "stats": 28,
        }
        
        font_names = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "Arial Unicode MS",
            "simsun",
            "msyh",
        ]
        
        for size_name, size in font_sizes.items():
            font = None
            for font_name in font_names:
                try:
                    font = pygame.font.Font(font_name, size)
                    break
                except Exception:
                    continue
            if font is None:
                try:
                    font = pygame.font.Font(None, size)
                except Exception:
                    font = pygame.font.SysFont(None, size)
            self.fonts[size_name] = font

    def set_physics(self, physics_engine):
        self.physics = physics_engine

    def set_counter(self, counter):
        self.counter = counter

    def _draw_centered_text(self, text, font, color, y_offset=0):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.screen_width // 2
        text_rect.centery = self.screen_height // 2 + y_offset
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def _draw_left_aligned_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
        return text_surface.get_height()

    def _create_button(self, button_id, text, y_offset, action):
        button_width = 220
        button_height = 60
        button_x = (self.screen_width - button_width) // 2
        button_y = self.screen_height // 2 + y_offset
        
        self.buttons[button_id] = {
            "rect": pygame.Rect(button_x, button_y, button_width, button_height),
            "text": text,
            "action": action,
            "hovered": False,
        }

    def _draw_button(self, button_info):
        rect = button_info["rect"]
        color = self.colors["button_hover"] if button_info["hovered"] else self.colors["button"]
        
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=12)
        
        text_surface = self.fonts["button"].render(button_info["text"], True, self.colors["button_text"])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _update_button_hover(self, mouse_pos):
        for button_id, button_info in self.buttons.items():
            button_info["hovered"] = button_info["rect"].collidepoint(mouse_pos)

    def _handle_button_click(self, mouse_pos):
        for button_id, button_info in self.buttons.items():
            if button_info["rect"].collidepoint(mouse_pos):
                return button_info["action"]
        return None

    def draw_start_screen(self):
        self.screen.fill(self.colors["background"])
        self.buttons.clear()
        
        self._draw_centered_text("打砖块游戏", self.fonts["title"], self.colors["text_highlight"], -200)
        
        instructions = [
            "1、使用鼠标移动控制底部挡板",
            "2、点击鼠标左键发射小球",
            "3、小球击中砖块获得10分",
            "4、小球击中挡板边缘会改变反弹角度",
            "5、消灭所有砖块即可获胜",
            "6、小球落地则游戏结束",
        ]
        
        start_y = self.screen_height // 2 - 120
        line_height = 42
        
        for i, instruction in enumerate(instructions):
            text_surface = self.fonts["instruction"].render(instruction, True, self.colors["text"])
            text_width = text_surface.get_width()
            x = (self.screen_width - text_width) // 2
            y = start_y + i * line_height
            self.screen.blit(text_surface, (x, y))
        
        self._create_button("start", "开始游戏", 120, "start_game")
        self._draw_button(self.buttons["start"])
        
        mouse_pos = pygame.mouse.get_pos()
        self._update_button_hover(mouse_pos)
        
        pygame.display.flip()

    def handle_start_screen_events(self, event):
        if "start" not in self.buttons:
            self._create_button("start", "开始游戏", 160, "start_game")
        if event.type == pygame.MOUSEMOTION:
            self._update_button_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                action = self._handle_button_click(event.pos)
                return action
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "start_game"
        return None

    def draw_game_screen(self):
        self.screen.fill(self.colors["background"])
        
        if self.counter:
            score_text = f"分数: {self.counter.score}"
            text_surface = self.fonts["score"].render(score_text, True, self.colors["score_text"])
            self.screen.blit(text_surface, (20, 8))
        
        if self.physics:
            for brick in self.physics.bricks:
                bx, by, bcolor = brick
                brick_rect = pygame.Rect(bx, by, self.physics.brick_width, self.physics.brick_height)
                pygame.draw.rect(self.screen, bcolor, brick_rect)
                pygame.draw.rect(self.screen, (50, 50, 70), brick_rect, 2)
            
            paddle_rect = pygame.Rect(*self.physics.get_paddle_rect())
            pygame.draw.rect(self.screen, self.colors["paddle"], paddle_rect, border_radius=10)
            pygame.draw.rect(self.screen, (150, 200, 255), paddle_rect, 2, border_radius=10)
            
            pygame.draw.circle(
                self.screen, 
                self.colors["ball"], 
                (int(self.physics.ball_pos[0]), int(self.physics.ball_pos[1])),
                self.physics.ball_radius
            )
            pygame.draw.circle(
                self.screen, 
                (200, 220, 255), 
                (int(self.physics.ball_pos[0]), int(self.physics.ball_pos[1])),
                self.physics.ball_radius, 2
            )
            
            if not self.physics.is_ball_moving:
                hint_text = "点击鼠标发射小球"
                hint_surface = self.fonts["instruction"].render(hint_text, True, self.colors["text_highlight"])
                hint_rect = hint_surface.get_rect()
                hint_rect.centerx = self.screen_width // 2
                hint_rect.centery = self.screen_height - 100
                self.screen.blit(hint_surface, hint_rect)
        
        pygame.display.flip()

    def draw_end_screen(self, won):
        self.screen.fill(self.colors["background"])
        self.buttons.clear()
        
        if won:
            result_text = "恭喜获胜！"
            result_color = (100, 255, 100)
        else:
            result_text = "游戏结束"
            result_color = (255, 100, 100)
        
        self._draw_centered_text(result_text, self.fonts["title"], result_color, -150)
        
        if self.counter:
            stats = [
                f"最终分数: {self.counter.score}",
                f"挡板击中小球次数: {self.counter.paddle_hits}",
                f"剩余砖块数: {self.counter.bricks_remaining}",
                f"总砖块数: {self.counter.total_bricks}",
            ]
            
            start_y = self.screen_height // 2 - 50
            line_height = 50
            
            for i, stat in enumerate(stats):
                self._draw_centered_text(stat, self.fonts["stats"], self.colors["text"], -50 + i * line_height)
        
        self._create_button("restart", "重新开始", 140, "restart_game")
        self._draw_button(self.buttons["restart"])
        
        mouse_pos = pygame.mouse.get_pos()
        self._update_button_hover(mouse_pos)
        
        pygame.display.flip()

    def handle_end_screen_events(self, event):
        if "restart" not in self.buttons:
            self._create_button("restart", "重新开始", 140, "restart_game")
        if event.type == pygame.MOUSEMOTION:
            self._update_button_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                action = self._handle_button_click(event.pos)
                return action
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "restart_game"
        return None

    def update_start_screen_display(self):
        if "start" not in self.buttons:
            self._create_button("start", "开始游戏", 160, "start_game")
        self._update_button_hover(pygame.mouse.get_pos())
        self.screen.fill(self.colors["background"])
        self._draw_centered_text("打砖块游戏", self.fonts["title"], self.colors["text_highlight"], -200)
        
        instructions = [
            "1、使用鼠标移动控制底部挡板",
            "2、点击鼠标左键发射小球",
            "3、小球击中砖块获得10分",
            "4、小球击中挡板边缘会改变反弹角度",
            "5、消灭所有砖块即可获胜",
            "6、小球落地则游戏结束",
        ]
        
        max_width = 0
        for instruction in instructions:
            text_surface = self.fonts["instruction"].render(instruction, True, self.colors["text"])
            if text_surface.get_width() > max_width:
                max_width = text_surface.get_width()
        
        block_start_x = (self.screen_width - max_width) // 2
        start_y = self.screen_height // 2 - 120
        line_height = 42
        
        for i, instruction in enumerate(instructions):
            text_surface = self.fonts["instruction"].render(instruction, True, self.colors["text"])
            y = start_y + i * line_height
            self.screen.blit(text_surface, (block_start_x, y))
        
        self._draw_button(self.buttons["start"])
        pygame.display.flip()

    def update_end_screen_display(self, won):
        if "restart" not in self.buttons:
            self._create_button("restart", "重新开始", 140, "restart_game")
        self._update_button_hover(pygame.mouse.get_pos())
        self.screen.fill(self.colors["background"])
        
        if won:
            result_text = "恭喜获胜！"
            result_color = (100, 255, 100)
        else:
            result_text = "游戏结束"
            result_color = (255, 100, 100)
        
        self._draw_centered_text(result_text, self.fonts["title"], result_color, -150)
        
        if self.counter:
            stats = [
                f"最终分数: {self.counter.score}",
                f"挡板击中小球次数: {self.counter.paddle_hits}",
                f"剩余砖块数: {self.counter.bricks_remaining}",
                f"总砖块数: {self.counter.total_bricks}",
            ]
            
            start_y = self.screen_height // 2 - 50
            line_height = 50
            
            for i, stat in enumerate(stats):
                self._draw_centered_text(stat, self.fonts["stats"], self.colors["text"], -50 + i * line_height)
        
        self._draw_button(self.buttons["restart"])
        pygame.display.flip()
