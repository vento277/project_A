import threading
import queue  # Thread-safe queue
import pygame
import random
import time


class Gui:
    def __init__(self):
        pygame.init()
        # GUI constants
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()

        # Colors and font
        self.text_colour = pygame.Color("white")
        self.font = pygame.font.Font(None, 36)

        # Game state tracking
        self.running = True
        self.snakeIcon = None
        self.preyIcon = None
        self.score_text = 0

    def gameOver(self):
        """
        This method is used at the end to display a
        game over message and gracefully exit on SPACE key press.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.running = False  # Graceful exit

            if not self.running:
                break  # Exit the loop if the game is no longer running

            # Clear screen
            self.screen.fill(pygame.Color(BACKGROUND_COLOUR))

            # Game Over message
            game_over_text = self.font.render("Game Over!", True, pygame.Color("white"))
            button_text = self.font.render("Press SPACE to Exit", True, pygame.Color("white"))

            # Text positioning
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
            button_rect = button_text.get_rect(center=(WINDOW_WIDTH // 2, 2 * WINDOW_HEIGHT // 3))

            # Draw text
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(button_text, button_rect)

            # Update display
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def draw_game(self):
        try:
            self.screen.fill(pygame.Color(BACKGROUND_COLOUR))
            if self.snakeIcon:
                for segment in self.snakeIcon:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color(ICON_COLOUR),
                        (segment[0] - 5, segment[1] - 5, SNAKE_ICON_WIDTH, SNAKE_ICON_WIDTH),
                    )
            if self.preyIcon:
                pygame.draw.rect(
                    self.screen,
                    pygame.Color(ICON_COLOUR),
                    (self.preyIcon[0], self.preyIcon[1],
                     PREY_ICON_WIDTH, PREY_ICON_WIDTH)
                )

            score_text = self.font.render(
                f"Score: {self.score_text}", True, pygame.Color("white")
            )

            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
        except pygame.error:
            self.running = False  # Exit gracefully if the display surface is closed

    def main_loop(self, game):
        handler = QueueHandler(gameQueue, self)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.whenAnArrowKeyIsPressed("Up")
                    elif event.key == pygame.K_DOWN:
                        game.whenAnArrowKeyIsPressed("Down")
                    elif event.key == pygame.K_LEFT:
                        game.whenAnArrowKeyIsPressed("Left")
                    elif event.key == pygame.K_RIGHT:
                        game.whenAnArrowKeyIsPressed("Right")
            handler.process_queue()
            self.draw_game()
            self.clock.tick(30)


class QueueHandler:
    def __init__(self, queue, gui):
        self.queue = queue
        self.gui = gui

    def process_queue(self):
        try:
            while not self.queue.empty():
                task = self.queue.get_nowait()
                if "game_over" in task:
                    self.gui.gameOver()
                    return
                elif "move" in task:
                    self.gui.snakeIcon = task["move"]
                elif "prey" in task:
                    self.gui.preyIcon = task["prey"]
                elif "score" in task:
                    self.gui.score_text = task["score"]
                self.queue.task_done()
        except queue.Empty:
            pass


class Game:
    '''
        This class implements most of the game functionalities.
    '''
        
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55), (465, 55), (455, 55)]
        self.direction = "Left"
        self.gameNotOver = True
        self.prey_position = None
        self.createNewPrey()
        self._time_factor = 1
        self.last_key_time = 0   

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
        """
        SPEED = 0.15     
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED * self._time_factor)

    def whenAnArrowKeyIsPressed(self, e) -> None:
        currentDirection = self.direction
        current_time = pygame.time.get_ticks()
        key_delay = 10  # Delay in milliseconds to prevent rapid direction changes

        # Ignore rapid key presses within key_delay milliseconds
        if current_time - self.last_key_time < key_delay:
            return
        self.last_key_time = current_time

        if (currentDirection == "Left" and e == "Right" or 
            currentDirection == "Right" and e == "Left" or
            currentDirection == "Up" and e == "Down" or
            currentDirection == "Down" and e == "Up"):
            return
        self.direction = e

    def move(self):
        new_head = self.calculateNewCoordinates()
        self.isGameOver(new_head)

        if self.gameNotOver:
            x_head, y_head = new_head 
            x1_prey, y1_prey, x2_prey, y2_prey = self.prey_position
            if (x1_prey <= x_head <= x2_prey) and (y1_prey <= y_head <= y2_prey):
                self.snakeCoordinates.append(new_head)
                self.score += 1
                self.queue.put({"score": self.score})           
                self.createNewPrey()
                # we increase the snake by 10% each time it has ate a prey but we do not reduce too much where it takes longer to process the program than increase the speed
                if self._time_factor > 0.4:
                    #if the time factor is > 40% then we increase the speed by 10% every time it ate.
                    self._time_factor-=0.1
            else:
                self.snakeCoordinates.append(new_head)
                self.snakeCoordinates.pop(0)  
            self.queue.put({"move": self.snakeCoordinates})
        else:
            self.queue.put({"game_over": True})

    def calculateNewCoordinates(self) -> tuple:
        lastX, lastY = self.snakeCoordinates[-1]
        match self.direction:
            case 'Up': new_x = lastX; new_y = lastY - MOVEMENT
            case 'Down': new_x = lastX; new_y = lastY + MOVEMENT
            case 'Left': new_x = lastX - MOVEMENT; new_y = lastY
            case 'Right': new_x = lastX + MOVEMENT; new_y = lastY
        return (new_x, new_y)

    def isGameOver(self, snakeCoordinates) -> None:
        x, y = snakeCoordinates
        snake_die = False
        if x > WINDOW_WIDTH or x < 0 or y > WINDOW_HEIGHT or y < 0:
            snake_die = True
        elif snakeCoordinates in self.snakeCoordinates:
            snake_die = True
        if snake_die:
            self.gameNotOver = False
            self.queue.put({'game_over': True})

    def createNewPrey(self):
        THRESHOLD = 15   
        x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
        y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)
        rectangleCoordinates = (x - PREY_ICON_WIDTH, y - PREY_ICON_WIDTH, x + PREY_ICON_WIDTH, y + PREY_ICON_WIDTH)
        self.prey_position = rectangleCoordinates
        self.queue.put({'prey': self.prey_position})


if __name__ == "__main__":
    WINDOW_WIDTH, WINDOW_HEIGHT = 500, 300
    SNAKE_ICON_WIDTH, PREY_ICON_WIDTH = 15, 15
    MOVEMENT = 15
    BACKGROUND_COLOUR, ICON_COLOUR = "black", "yellow"

    gameQueue = queue.Queue()
    game = Game()
    gui = Gui()

    threading.Thread(target=game.superloop, daemon=True).start()
    gui.main_loop(game)
