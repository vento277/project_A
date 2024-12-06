# Group#: G5
# Student Names: Weifeng Ke & Peter Kim

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue  # Thread-safe queue
import pygame
import random
import time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self) -> None:
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """       
        pygame.init()

        #create the game window with specified dimensions
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock() #create a clock to control game frame rate

        #colors and font
        self.text_colour = pygame.Color("white")
        self.font = pygame.font.Font(None, 36)

        #game state tracking
        self.running = True  #flag to control game loop
        self.snakeIcon = None  #snake body segments
        self.preyIcon = None  #current prey location
        self.score_text = 0  #player's current score

        self.screen.fill(pygame.Color(BACKGROUND_COLOUR))

    def gameOver(self) -> None:
        """
        This method is used at the end to display a
        game over message and gracefully exit on SPACE key press.
        """
        while self.running:
            for event in pygame.event.get(): #process pygame events
                if event.type == pygame.QUIT: #allow window close
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #exit game on space key
                    self.running = False  # Graceful exit

            #exit the loop if the game is no longer running
            if not self.running:
                break  

            self.screen.fill(pygame.Color(BACKGROUND_COLOUR)) #clear screen
            game_over_text = self.font.render("Game Over! Press SPACE to Exit", True, pygame.Color("white")) #game over message
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))    #text positioning
            self.screen.blit(game_over_text, game_over_rect)    #draw text
            pygame.display.flip() #update display
        #free up system resources
        pygame.quit()
        #return to the main loop and finish
        return None
    
    def draw_game(self) -> None:
        '''
        This method is used to set up the GUI and draw the necessary objects using pygame.
        '''
        try:
            self.screen.fill(pygame.Color(BACKGROUND_COLOUR))

            if self.snakeIcon: #draw snake segments as rectangles
                for segment in self.snakeIcon:
                    pygame.draw.rect(
                        self.screen,
                        pygame.Color(ICON_COLOUR),
                        (segment[0] - 5, segment[1] - 5, SNAKE_ICON_WIDTH, SNAKE_ICON_WIDTH),
                    )

            if self.preyIcon: #draw prey as a rectangle
                pygame.draw.rect(
                    self.screen,
                    pygame.Color(ICON_COLOUR),
                    (self.preyIcon[0], self.preyIcon[1],
                     PREY_ICON_WIDTH, PREY_ICON_WIDTH)
                )

            score_text = self.font.render(
                f"Score: {self.score_text}", True, pygame.Color("white")
            )
            
            #display current score
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip() #update the display

        except pygame.error:
            self.running = False  #exit gracefully if the display is closed

    def main_loop(self, game) -> None:
        '''
        This method is to run the game continuously using pygame (alternative to gui.root.mainloop()). 
        The purpose is to provide modularity to the alternative approach.
        '''
        handler = QueueHandler(gameQueue, self) #create a queue handler to manage game events

        #main game event loop
        while self.running:
            for event in pygame.event.get(): #process pygame events
                if event.type == pygame.QUIT: #allow window close
                    self.running = False

                if event.type == pygame.KEYDOWN: #handle keyboard input for the snake
                    if event.key == pygame.K_UP:
                        game.whenAnArrowKeyIsPressed("Up")
                    elif event.key == pygame.K_DOWN:
                        game.whenAnArrowKeyIsPressed("Down")
                    elif event.key == pygame.K_LEFT:
                        game.whenAnArrowKeyIsPressed("Left")
                    elif event.key == pygame.K_RIGHT:
                        game.whenAnArrowKeyIsPressed("Right")

            handler.queueHandler()  #process any pending game events from the queue
            self.draw_game()    #redraw the game state
            self.clock.tick(30) #control game frame rate


class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self, queue, gui) -> None:
        self.queue = queue
        self.gui = gui

    def queueHandler(self) -> None:
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
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

class Game():
    '''
        This class implements most of the game functionalities.
    '''
        
    def __init__(self) -> None:
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        #(x, y) tuple. Initially its size is 5 tuples. 
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55), (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        #initialize the attribute
        self.prey_position = None
        self.createNewPrey()
        self._time_factor = 1
        #this factor controls how fast the game goes
        self._time_factor = 1    #this is set to 1 at first
        #to control the key press speed
        self.last_key_time = 0 

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            #call the move instance to get the sneak moving
            self.move()
            #We can set fixed wait time between each move task is called
            #later on we can change time factor so we can speed up or down the movements
            time.sleep(SPEED*self._time_factor)

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.

            Had been modified for pygame.
        """
        currentDirection = self.direction
        current_time = pygame.time.get_ticks() #get current time to prevent rapid direction changes
        key_delay = 10  #delay in milliseconds to prevent rapid direction changes

        #ignore rapid key presses within key_delay milliseconds
        if current_time - self.last_key_time < key_delay:
            return
        self.last_key_time = current_time

        #ignore invalid keys
        if (currentDirection == "Left" and e == "Right" or 
            currentDirection == "Right" and e == "Left" or
            currentDirection == "Up" and e == "Down" or
            currentDirection == "Down" and e == "Up"):
            return
        self.direction = e

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        #NewSnakeCorrdinates has the snake head coordinates as a tuples
        NewSnakeCoordinates = self.calculateNewCoordinates()
        #complete the method implementation below
        #first check if the agan is over if over inside the isGameOver will call gameover
        self.isGameOver(NewSnakeCoordinates)

        #game is not over yet
        if self.gameNotOver:
            #check to see if the snake has eat the prey
            #that requrires snake location and prey location comparison
            #express the snake head coordinates to head_x and head_y
            x_head, y_head = NewSnakeCoordinates 
            x1_prey, y1_prey, x2_prey, y2_prey = self.prey_position
            #if the snake head is in the snake head location and the snake head is within the bound of the prey +/- half the SNAKE_ICON_WIDTH it will be consider captured
            if (x1_prey-(SNAKE_ICON_WIDTH/2) <= x_head <= x2_prey+(SNAKE_ICON_WIDTH/2)) and (y1_prey-(SNAKE_ICON_WIDTH/2) <= y_head <= y2_prey+(SNAKE_ICON_WIDTH/2)):
                #the snake has ate the prey
                #so we need to make the snake longer 
                self.snakeCoordinates.append(NewSnakeCoordinates)
                #need to give snake a point
                self.score += 1
                #also need to let the game queue handler know to update the score too
                self.queue.put({"score": self.score})    
                #we need to call the next prey location       
                self.createNewPrey()
                #we increase the snake speed by 10% each time it has ate a prey 
                if self._time_factor > 0.4:
                    #if the time factor is > 40% then we increase the speed by 10% every time it ate.
                    self._time_factor-=0.1
            else:
                #the sanek head has not ate the prey 
                #so nothign happens aside from updating the snake corrdinates tuple list
                #the head is at the last of the tuple list so append to the last
                self.snakeCoordinates.append(NewSnakeCoordinates)
                #remove the tail so pop the first
                self.snakeCoordinates.pop(0)  
            
            #put the move task to the game handleing queue
            self.queue.put({"move": self.snakeCoordinates})
        else:
            #game over we need to let game queue handle know
            self.queue.put({"game_over": True})

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]
        match self.direction:
            case 'Up': new_x = lastX; new_y = lastY - MOVEMENT
            case 'Down': new_x = lastX; new_y = lastY + MOVEMENT
            case 'Left': new_x = lastX - MOVEMENT; new_y = lastY
            case 'Right': new_x = lastX + MOVEMENT; new_y = lastY
        return (new_x, new_y)

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
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
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        #this randomly generate prey in side the canvas and also not on the border. 
        x=random.randint(THRESHOLD,WINDOW_WIDTH-THRESHOLD)
        y=random.randint(THRESHOLD,WINDOW_HEIGHT-THRESHOLD)
        #this ensures the randomly generate prey don't land on top of the snake
        while (x,y) in self.snakeCoordinates:
            #complete the method implementation 
            x=random.randint(THRESHOLD,WINDOW_WIDTH-THRESHOLD)
            y=random.randint(THRESHOLD,WINDOW_HEIGHT-THRESHOLD)
        
        #calcuate the rectangle coordinates
        rectangleCoordinates=(x-(PREY_ICON_WIDTH/2),y-(PREY_ICON_WIDTH/2),x+(PREY_ICON_WIDTH/2),y+(PREY_ICON_WIDTH/2))
        #we need the prey position to be know to other instances and this creay new prey does not even return anything
        self.prey_position=rectangleCoordinates
        
        #add the prey task to the queue
        self.queue.put({'prey':self.prey_position})


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    #add the specified constant PREY_ICON_WIDTH here     
    #the prey icon is about 15x15 pixel big
    PREY_ICON_WIDTH = 15
    #each movement is about 15 pixel wide
    MOVEMENT = 15
    
    BACKGROUND_COLOUR, ICON_COLOUR = "black", "yellow"

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface  
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's event loop
    gui.main_loop(game)