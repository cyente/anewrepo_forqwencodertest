import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)

# 小鸟属性
BIRD_X = 80
BIRD_WIDTH = 34
BIRD_HEIGHT = 24
GRAVITY = 0.5
FLAP_STRENGTH = -9

# 管道属性
PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # 毫秒

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.alive = True
        
    def flap(self):
        if self.alive:
            self.velocity = FLAP_STRENGTH
    
    def update(self):
        if self.alive:
            self.velocity += GRAVITY
            self.y += self.velocity
            
            # 检查是否碰到地面或天花板
            if self.y + self.height >= SCREEN_HEIGHT - 50:
                self.y = SCREEN_HEIGHT - 50 - self.height
                self.alive = False
            if self.y <= 0:
                self.y = 0
                self.velocity = 0
    
    def draw(self):
        # 画小鸟身体（黄色椭圆）
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(screen, YELLOW, body_rect)
        pygame.draw.ellipse(screen, BLACK, body_rect, 2)
        
        # 画眼睛
        eye_x = self.x + self.width - 10
        eye_y = self.y + 5
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 6)
        pygame.draw.circle(screen, BLACK, (eye_x + 2, eye_y), 3)
        
        # 画嘴巴
        beak_points = [
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width + 8, self.y + self.height // 2 + 3),
            (self.x + self.width, self.y + self.height // 2 + 6)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
        # 画翅膀
        wing_x = self.x + 8
        wing_y = self.y + self.height // 2
        if self.velocity < 0:  # 向上飞时翅膀向上
            wing_y -= 5
        pygame.draw.ellipse(screen, ORANGE, (wing_x, wing_y, 12, 8))


class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.passed = False
        
        # 随机生成管道间隙位置
        min_height = 80
        max_height = SCREEN_HEIGHT - 50 - self.gap - min_height
        self.top_height = random.randint(min_height, max_height)
        self.bottom_y = self.top_height + self.gap
    
    def update(self):
        self.x -= PIPE_SPEED
    
    def draw(self):
        # 画上管道
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, DARK_GREEN, top_rect, 3)
        
        # 画上管道顶部装饰
        top_cap = pygame.Rect(self.x - 3, self.top_height - 20, self.width + 6, 20)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, DARK_GREEN, top_cap, 3)
        
        # 画下管道
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - 50 - self.bottom_y)
        pygame.draw.rect(screen, GREEN, bottom_rect)
        pygame.draw.rect(screen, DARK_GREEN, bottom_rect, 3)
        
        # 画下管道顶部装饰
        bottom_cap = pygame.Rect(self.x - 3, self.bottom_y, self.width + 6, 20)
        pygame.draw.rect(screen, GREEN, bottom_cap)
        pygame.draw.rect(screen, DARK_GREEN, bottom_cap, 3)
    
    def collides_with(self, bird):
        bird_rect = pygame.Rect(bird.x, bird.y, bird.width, bird.height)
        
        # 上管道碰撞
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        if bird_rect.colliderect(top_rect):
            return True
        
        # 下管道碰撞
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - 50 - self.bottom_y)
        if bird_rect.colliderect(bottom_rect):
            return True
        
        return False


class Game:
    def __init__(self):
        self.reset()
        self.last_pipe_time = pygame.time.get_ticks()
        self.high_score = 0
    
    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        self.reset()
                        self.last_pipe_time = pygame.time.get_ticks()
                    else:
                        self.bird.flap()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_started:
                    self.game_started = True
                elif self.game_over:
                    self.reset()
                    self.last_pipe_time = pygame.time.get_ticks()
                else:
                    self.bird.flap()
        
        return True
    
    def update(self):
        if not self.game_started or self.game_over:
            return
        
        self.bird.update()
        
        # 生成新管道
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > PIPE_FREQUENCY:
            self.pipes.append(Pipe())
            self.last_pipe_time = current_time
        
        # 更新管道
        for pipe in self.pipes[:]:
            pipe.update()
            
            # 检查碰撞
            if pipe.collides_with(self.bird):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
            
            # 检查是否通过管道
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
            
            # 移除超出屏幕的管道
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)
        
        # 检查小鸟是否死亡
        if not self.bird.alive:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
    
    def draw(self):
        # 画背景
        screen.fill(SKY_BLUE)
        
        # 画云朵装饰
        self.draw_clouds()
        
        # 画管道
        for pipe in self.pipes:
            pipe.draw()
        
        # 画地面
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        pygame.draw.rect(screen, BROWN, ground_rect)
        pygame.draw.rect(screen, DARK_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 10))
        
        # 画小鸟
        self.bird.draw()
        
        # 画分数
        score_text = font.render(str(self.score), True, WHITE)
        score_shadow = font.render(str(self.score), True, BLACK)
        screen.blit(score_shadow, (SCREEN_WIDTH // 2 - score_text.get_width() // 2 + 2, 52))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # 画开始提示
        if not self.game_started:
            self.draw_message("Flappy Bird", "按空格键或点击开始", "按 ESC 退出")
        
        # 画游戏结束信息
        if self.game_over:
            self.draw_message("游戏结束!", f"得分：{self.score}", f"最高分：{self.high_score}", "按空格键重新开始")
        
        pygame.display.flip()
    
    def draw_clouds(self):
        cloud_positions = [(50, 80), (200, 120), (320, 60)]
        for x, y in cloud_positions:
            pygame.draw.ellipse(screen, WHITE, (x, y, 60, 30))
            pygame.draw.ellipse(screen, WHITE, (x + 20, y - 15, 50, 35))
            pygame.draw.ellipse(screen, WHITE, (x + 40, y, 50, 25))
    
    def draw_message(self, title, subtitle1, subtitle2=None, subtitle3=None):
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = font.render(title, True, YELLOW)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 180))
        
        # 副标题
        sub1_text = small_font.render(subtitle1, True, WHITE)
        screen.blit(sub1_text, (SCREEN_WIDTH // 2 - sub1_text.get_width() // 2, 250))
        
        if subtitle2:
            sub2_text = small_font.render(subtitle2, True, WHITE)
            screen.blit(sub2_text, (SCREEN_WIDTH // 2 - sub2_text.get_width() // 2, 290))
        
        if subtitle3:
            sub3_text = small_font.render(subtitle3, True, WHITE)
            screen.blit(sub3_text, (SCREEN_WIDTH // 2 - sub3_text.get_width() // 2, 340))


def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
