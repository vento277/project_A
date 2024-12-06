# Group#: G5
# Student Names: Weifeng Ke & Peter Kim

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library
from tkinter import Tk, Canvas, Button
import random, time

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
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self) -> None:
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self) -> None:
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
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
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


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
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        #initialize the attribute
        self.prey_position=None
        self.createNewPrey()
        #this factor controls how fast the game goes
        self._time_factor = 1    #this is set to 1 at first

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
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

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
            x_head,y_head=NewSnakeCoordinates
            x1_prey,y1_prey,x2_prey,y2_prey=self.prey_position
            #if the snake head is in the snake head location and the snake head is within the bound of the prey +/- half the SNAKE_ICON_WIDTH it will be consider captured
            if (x1_prey-(SNAKE_ICON_WIDTH/2) <= x_head <= x2_prey+(SNAKE_ICON_WIDTH/2)) and (y1_prey-(SNAKE_ICON_WIDTH/2) <= y_head <= y2_prey+(SNAKE_ICON_WIDTH/2)):
                #the snake has ate the prey
                #so we need to make the snake longer
                self.snakeCoordinates.append(NewSnakeCoordinates)
                #need to give snake a point
                self.score=self.score+1
                #also need to let the game queue handler know to update the score too
                self.queue.put({"score":self.score})           
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
        #Game is over 
        else:
            #game over we need to let game queue handle know
            self.queue.put({"game_over":True})
            return
            

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
        #complete the method implementation below
        #the lastx and lasty are tuple of snake head
        match self.direction:
            case'Up':
                new_x=lastX
                #the y direct grows down, so the top left is (0,0) bottom right is (windows width, windous height), so - to go up
                new_y=lastY - MOVEMENT
            case 'Down':
                new_x=lastX
                #the y direct grows down, so the top left is (0,0) bottom right is (windows width, windous height), so + to go up
                new_y=lastY + MOVEMENT                
            case 'Left':
                new_x=lastX - MOVEMENT
                new_y=lastY
            case 'Right':
                new_x=lastX + MOVEMENT
                new_y=lastY
            case _:
                new_x=lastX
                new_y=lastY 
        #retun the new coordinate
        return (new_x,new_y)

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        #complete the method implementation below
        snake_die=False
        #check to see if the snake hits the border the border is at x[0 to window width] y[0 to window height]
        if x > WINDOW_WIDTH or x < 0 or y > WINDOW_HEIGHT or y <0:
            snake_die=True
        #check to see if the snake hit it's self on the head
        elif snakeCoordinates in self.snakeCoordinates:
            snake_die=True
            
        if snake_die:
            #Set gameNotOver to False and we need to trigger gameover in GameQueneHandle
            self.gameNotOver=False
            #let the game queue handle know =
            self.queue.put({'game_over': True})
            return

    def createNewPrey(self) -> None:
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
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()