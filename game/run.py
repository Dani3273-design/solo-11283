import pygame
import random
import math


class PhysicsEngine:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ball_radius = 10
        self.ball_speed = 5
        self.ball_pos = [0, 0]
        self.ball_vel = [0, 0]
        self.is_ball_moving = False
        
        self.paddle_width = 120
        self.paddle_height = 20
        self.paddle_pos = [screen_width // 2 - self.paddle_width // 2, 
                            screen_height - 50]
        
        self.brick_width = self.ball_radius * 2 * 2
        self.brick_height = self.ball_radius * 2
        self.bricks = []
        self.counter = None
        self.sound_enabled = True
        self._init_sound()

    def _normalize_velocity(self):
        if self.ball_vel[0] == 0 and self.ball_vel[1] == 0:
            return
        current_speed = math.sqrt(self.ball_vel[0] ** 2 + self.ball_vel[1] ** 2)
        if current_speed > 0:
            ratio = self.ball_speed / current_speed
            self.ball_vel[0] *= ratio
            self.ball_vel[1] *= ratio

    def _init_sound(self):
        try:
            pygame.mixer.init()
            self.sound_wall = self._create_sound(440, 0.1)
            self.sound_paddle = self._create_sound(523, 0.1)
            self.sound_brick = self._create_sound(659, 0.1)
        except Exception:
            self.sound_enabled = False

    def _create_sound(self, frequency, duration):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        buf = []
        for i in range(n_samples):
            t = i / sample_rate
            value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * t) * 
                        math.exp(-t / 0.1))
            buf.append(value)
            buf.append(value)
        
        try:
            sound_array = pygame.mixer.Sound(buffer=bytes(b % 256 for b in buf))
            return sound_array
        except Exception:
            return None

    def set_counter(self, counter):
        self.counter = counter

    def reset_ball(self, paddle_x=None):
        if paddle_x is None:
            paddle_x = self.paddle_pos[0]
        self.ball_pos = [paddle_x + self.paddle_width // 2, 
                         self.paddle_pos[1] - self.ball_radius]
        self.ball_vel = [0, 0]
        self.is_ball_moving = False

    def launch_ball(self):
        if not self.is_ball_moving:
            angle = random.uniform(-60, 60)
            rad = math.radians(angle)
            self.ball_vel = [
                self.ball_speed * math.sin(rad),
                -self.ball_speed * math.cos(rad)
            ]
            self.is_ball_moving = True

    def update_paddle(self, x):
        new_x = x - self.paddle_width // 2
        if new_x < 0:
            new_x = 0
        elif new_x > self.screen_width - self.paddle_width:
            new_x = self.screen_width - self.paddle_width
        self.paddle_pos[0] = new_x

    def _play_sound(self, sound_type):
        if not self.sound_enabled:
            return
        sound = None
        if sound_type == "wall":
            sound = self.sound_wall
        elif sound_type == "paddle":
            sound = self.sound_paddle
        elif sound_type == "brick":
            sound = self.sound_brick
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def _check_wall_collision(self):
        if self.ball_pos[0] - self.ball_radius <= 0:
            self.ball_pos[0] = self.ball_radius
            self.ball_vel[0] = abs(self.ball_vel[0])
            self._play_sound("wall")
            self._normalize_velocity()
            return True
        elif self.ball_pos[0] + self.ball_radius >= self.screen_width:
            self.ball_pos[0] = self.screen_width - self.ball_radius
            self.ball_vel[0] = -abs(self.ball_vel[0])
            self._play_sound("wall")
            self._normalize_velocity()
            return True
        
        if self.ball_pos[1] - self.ball_radius <= 0:
            self.ball_pos[1] = self.ball_radius
            self.ball_vel[1] = abs(self.ball_vel[1])
            self._play_sound("wall")
            self._normalize_velocity()
            return True
        
        return False

    def _check_paddle_collision(self):
        if not self.is_ball_moving:
            return False
        
        paddle_left = self.paddle_pos[0]
        paddle_right = self.paddle_pos[0] + self.paddle_width
        paddle_top = self.paddle_pos[1]
        paddle_bottom = self.paddle_pos[1] + self.paddle_height
        
        ball_left = self.ball_pos[0] - self.ball_radius
        ball_right = self.ball_pos[0] + self.ball_radius
        ball_top = self.ball_pos[1] - self.ball_radius
        ball_bottom = self.ball_pos[1] + self.ball_radius
        
        if self.ball_vel[1] > 0:
            if (ball_right > paddle_left and 
                ball_left < paddle_right and
                ball_bottom >= paddle_top and
                ball_top <= paddle_bottom):
                
                self.ball_pos[1] = paddle_top - self.ball_radius
                self.ball_vel[1] = -abs(self.ball_vel[1])
                
                hit_offset = self.ball_pos[0] - (paddle_left + self.paddle_width / 2)
                max_offset = self.paddle_width / 2
                ratio = hit_offset / max_offset
                max_vel_x = self.ball_speed * 0.8
                self.ball_vel[0] = max_vel_x * ratio
                
                if self.counter:
                    self.counter.increment_paddle_hits()
                self._play_sound("paddle")
                self._normalize_velocity()
                return True
        return False

    def _check_brick_collision(self):
        ball_left = self.ball_pos[0] - self.ball_radius
        ball_right = self.ball_pos[0] + self.ball_radius
        ball_top = self.ball_pos[1] - self.ball_radius
        ball_bottom = self.ball_pos[1] + self.ball_radius
        
        for brick in self.bricks[:]:
            bx, by, bcolor = brick
            b_right = bx + self.brick_width
            b_bottom = by + self.brick_height
            
            if (ball_right > bx and ball_left < b_right and
                ball_bottom > by and ball_top < b_bottom):
                
                overlap_left = ball_right - bx
                overlap_right = b_right - ball_left
                overlap_top = ball_bottom - by
                overlap_bottom = b_bottom - ball_top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_left:
                    self.ball_pos[0] = bx - self.ball_radius
                    self.ball_vel[0] = -abs(self.ball_vel[0])
                elif min_overlap == overlap_right:
                    self.ball_pos[0] = b_right + self.ball_radius
                    self.ball_vel[0] = abs(self.ball_vel[0])
                elif min_overlap == overlap_top:
                    self.ball_pos[1] = by - self.ball_radius
                    self.ball_vel[1] = -abs(self.ball_vel[1])
                else:
                    self.ball_pos[1] = b_bottom + self.ball_radius
                    self.ball_vel[1] = abs(self.ball_vel[1])
                
                self.bricks.remove(brick)
                if self.counter:
                    self.counter.add_score(10)
                    self.counter.remove_brick()
                self._play_sound("brick")
                self._normalize_velocity()
                return True
        
        return False

    def update(self):
        if not self.is_ball_moving:
            self.ball_pos[0] = self.paddle_pos[0] + self.paddle_width // 2
            return "playing"
        
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        self._check_wall_collision()
        self._check_paddle_collision()
        self._check_brick_collision()
        
        if self.ball_pos[1] + self.ball_radius > self.screen_height:
            return "lost"
        
        if len(self.bricks) == 0:
            return "won"
        
        return "playing"

    def generate_bricks(self):
        self.bricks = []
        colors = [
            (255, 69, 0),
            (255, 140, 0),
            (255, 215, 0),
            (144, 238, 144),
            (135, 206, 235),
            (173, 216, 230),
            (221, 160, 221),
        ]
        
        brick_gap = 5
        max_rows = 8
        max_cols = self.screen_width // (self.brick_width + brick_gap) - 1
        upper_half_height = self.screen_height * 0.5 - 50
        
        start_x = (self.screen_width - max_cols * (self.brick_width + brick_gap) + brick_gap) // 2
        
        for row in range(max_rows):
            row_y = 50 + row * (self.brick_height + brick_gap)
            if row_y + self.brick_height > upper_half_height:
                break
            
            cols_in_row = random.randint(max_cols // 2, max_cols)
            offset = random.randint(0, max_cols - cols_in_row)
            
            for col in range(cols_in_row):
                actual_col = col + offset
                x = start_x + actual_col * (self.brick_width + brick_gap)
                color = random.choice(colors)
                self.bricks.append([x, row_y, color])
        
        if self.counter:
            self.counter.set_bricks_count(len(self.bricks))

    def get_ball_rect(self):
        return (self.ball_pos[0] - self.ball_radius, 
                self.ball_pos[1] - self.ball_radius,
                self.ball_radius * 2, 
                self.ball_radius * 2)

    def get_paddle_rect(self):
        return (self.paddle_pos[0], 
                self.paddle_pos[1],
                self.paddle_width, 
                self.paddle_height)
