import pygame
import time
import random
import math

pygame.font.init()

WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  
pygame.display.set_caption("BRICKS")

PLAYER_WIDTH = 100
PLAYER_HEIGHT = 10
PLAYER_VEL = 5

BALL_RADIUS = 10
BALL_VEL = 5

BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = WIDTH / BRICK_COLS - 2  # Adding space for rounding effect
BRICK_HEIGHT = 30

FONT = pygame.font.SysFont("comicsans", 20)

ball_moving = False
paused = False
score = 0
paused_time = 0
end_message = False
win_message = False
elapsed_time = 0
pause_start_time = 0
game_started = False
final_time = 0 

# Define a small tolerance to avoid precision issues with floating-point comparisons
tolerance = 0.01    

angles = [math.radians(angle) for angle in range(45, 135) if 45 <= angle <= 80 or 100 <= angle < 135
          and abs(math.cos(math.radians(angle))) > tolerance 
          and abs(math.sin(math.radians(angle))) > tolerance]

def draw_rounded_rect_with_border(surface, rect, border_color, fill_color, border_radius, border_width):
    # Draw the background rectangle (border)
    pygame.draw.rect(surface, border_color, rect, border_radius=border_radius)
    # Draw the foreground rectangle (fill)
    inner_rect = rect.inflate(-border_width*2, -border_width*2)
    pygame.draw.rect(surface, fill_color, inner_rect, border_radius=border_radius-border_width)


def draw(player, elapsed_time, ball, bricks, score, show_start_message, paused, end_message, final_time, win_message):
    WIN.fill("black")
    
    if not end_message and not win_message and game_started and not paused:
        time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "orange")
        WIN.blit(time_text, (10, 10))
        
    if game_started:
        score_text = FONT.render(f"Score: {score}", 1, "orange")
        WIN.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    pygame.draw.rect(WIN, "blue", player)

    pygame.draw.circle(WIN, "yellow", (ball.x, ball.y), BALL_RADIUS)
    
    for brick in bricks:
        draw_rounded_rect_with_border(WIN, brick['rect'], "white", "brown", 10, 3)
        
    if show_start_message and not end_message and not win_message:
        start_text = f"Press Enter to Play\n\n Key Bindings \n <- or A : Move left \n -> or D : Move right \n Space : Pause \n q : Quit"
        text_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        draw_multiline_text(WIN, start_text, FONT, "white", text_rect)
        
    if paused and not show_start_message:
        pause_text = f"Game Paused\n\n Press Space to Resume or q to Quit"  
        text_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        draw_multiline_text(WIN, pause_text, FONT, "purple", text_rect)
     
    if end_message:
        lost_text = f"You Lost!\nTime Taken: {round(final_time)}s\nFinal Score: {score}\n\nBetter Luck Next Time! \nPress Enter to Play Again or q to Quit"  
        text_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        draw_multiline_text(WIN, lost_text, FONT, "red", text_rect)
    
    if win_message:
        win_text = f"You Won!\nTime Taken: {round(final_time)}s\nFinal Score: {score}\n\nPress Enter to Play Again or q to Quit"
        text_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        draw_multiline_text(WIN, win_text, FONT, "green", text_rect)

    pygame.display.update()
    
def handle_ball_brick_collision(ball, bricks, ball_vel):
    for brick in bricks:
        if ball.colliderect(brick['rect']):
            bricks.remove(brick)
            brick_rect = brick['rect']
            # Reverse ball direction based on the collision side
            if abs(ball.centerx - (brick_rect.x + brick_rect.width / 2)) > abs(ball.centery - (brick_rect.y + brick_rect.height / 2)):
                ball_vel['x'] = -ball_vel['x']
            else:
                ball_vel['y'] = -ball_vel['y']
            return True
    return False

def draw_multiline_text(surface, text, font, color, rect):
    lines = text.splitlines()
    y = rect.y
    for line in lines:
        rendered_text = font.render(line, True, color)
        surface.blit(rendered_text, (rect.x + (rect.width - rendered_text.get_width()) / 2, y + (HEIGHT/3 + rendered_text.get_height())))
        y += rendered_text.get_height()

def reset_game():
    global player, ball, ball_vel, bricks, score, ball_moving, paused, paused_time, game_started, start_time, end_message, elapsed_time, pause_start_time, final_time, win_message
    ball_moving = False
    paused = False
    end_message = False
    win_message = False
    score = 0
    paused_time = 0
    start_time = time.time()  # Initialize start time
    elapsed_time = 0
    game_started = False
    pause_start_time = 0
    final_time = 0  
    
    player = pygame.Rect((WIDTH - PLAYER_WIDTH) / 2, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    ball = pygame.Rect(WIDTH / 2, (HEIGHT - (BALL_RADIUS + PLAYER_HEIGHT)), BALL_RADIUS * 2, BALL_RADIUS * 2)
    ball_vel = {'x': 0, 'y': 0}

    bricks = [{'rect': pygame.Rect(col * (BRICK_WIDTH + 2), ((row * BRICK_HEIGHT)+50), BRICK_WIDTH, BRICK_HEIGHT)}
              for row in range(BRICK_ROWS) for col in range(BRICK_COLS)]

def main():
    global game_started, paused, start_time, paused_time, ball_moving, end_message, elapsed_time, score, pause_start_time, final_time, win_message
    run = True
    reset_game()  # Initialize game state
    clock = pygame.time.Clock()
   
    while run:
        clock.tick(60)

        if game_started and not paused:
            elapsed_time = time.time() - start_time - paused_time 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 run = False
                 break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    if not game_started and not end_message and not win_message:
                        game_started = True
                        start_time = time.time()  # Initialize start time

                    if not ball_moving and game_started and not end_message and not win_message:
                        ball_moving = True
                        
                        # Random initial angle in radians
                        angle = random.choice(angles)                           
                        ball_vel['x'] = BALL_VEL * math.cos(angle)
                        ball_vel['y'] = BALL_VEL * math.sin(angle)
                        
                    if end_message or win_message:
                        reset_game()
                elif event.key == pygame.K_q:
                    run = False
                    break
                elif event.key == pygame.K_SPACE and game_started:
                    paused = not paused
                    if paused:
                        pause_start_time = time.time()
                    else:
                        paused_time += time.time() - pause_start_time 
                    
        keys = pygame.key.get_pressed()
        if game_started and not paused and ball_moving :
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player.x - PLAYER_VEL >= 0:
                    player.x -= PLAYER_VEL
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
                if player.x + PLAYER_VEL + player.width <= WIDTH:
                    player.x += PLAYER_VEL     

        if game_started and ball_moving and not paused:
        # Move the ball
            ball.x += ball_vel['x']
            ball.y += ball_vel['y']

            # Ball bouncing from sides 
            if ball.x - BALL_RADIUS <= 0:
                ball.x = BALL_RADIUS
                ball_vel['x'] = -ball_vel['x']
                
            elif ball.x + BALL_RADIUS >= WIDTH:
                ball.x = WIDTH - BALL_RADIUS
                ball_vel['x'] = -ball_vel['x']
            
            #Prevent ball from falling below 
            #if ball.y + BALL_RADIUS >= HEIGHT:
                # final_time = elapsed_time
                # ball_moving = False
                # end_message = True                  
                
            #Handle top bar    
            if ball.y - BALL_RADIUS <= 50:
                ball.y = 50 + BALL_RADIUS
                ball_vel['y'] = -ball_vel['y']
            
            #Handle ball and player collision
            if ball.colliderect(player) and score!=0:
                if ball_vel['x'] == 0:
                    angs = [math.radians(angle) for angle in range(45, 135) if 45 <= angle <= 80 or 100 <= angle < 135]
                    ball_vel['x'] += BALL_VEL * math.cos(math.radians(random.choice(angs))) 
                    
                if ball.y + BALL_RADIUS > player.y and ball.y - BALL_RADIUS < player.y + player.height:
                # Ball is within the vertical bounds of the player
                    if ball.x < player.x or ball.x > player.x + player.width:
                        # Ball hits the side of the player, so reverse its x velocity
                        ball_vel['x'] = -ball_vel['x']

            #Handle losing
            if ball.y + BALL_RADIUS >= HEIGHT: #and ball.x + BALL_RADIUS >= player.x:
                if not ball.colliderect(player):
                    final_time = elapsed_time
                    ball_moving = False
                    end_message = True
                else:    
                    ball.y = player.y - BALL_RADIUS
                    ball_vel['y'] = -ball_vel['y']

            # Handle collision with bricks
            if handle_ball_brick_collision(ball, bricks, ball_vel):
                score += 1
                
            # Check for win condition
            if not bricks:
                final_time = elapsed_time
                ball_moving = False
                win_message = True
    
        draw(player, elapsed_time, ball, bricks, score, not ball_moving, paused,end_message, final_time, win_message)
        
    pygame.quit()
       
if __name__ == "__main__":
    main()



