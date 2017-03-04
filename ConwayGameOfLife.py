#pygame used for bulk of drawing functions and frame draw timing
import pygame
#os used to center the screen, pretty much
import os

#some constants for drawing, W and H are counted in cells, though the screen loops
W, H = 60, 40
SQUARE_SIDE = 16
FRAMERATE = 120
STARTING_FRAMES_UNTIL_UPDATE = 4

#rules of the game defined as a constant dict since they aren't many, where the keys are the sum of live neighbors and the values are the next state of the cell
COUNT_CASES = {0: 0, 1: 0, 2: "stay", 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}


#returns a new grid based on the old one's state and the game's rules
def updateGrid(grid):
    new_grid = [[0 for x in range(H)] for y in range(W)]
    for i in range(W):
        for j in range(H):
            #need to manually loop index overflow, underflow is handled by python magic
            count = grid[i-1][j] + grid[(i+1)%W][j] + grid[i][j-1] + grid[i][(j+1)%H] + grid[i-1][j-1] + grid[i-1][(j+1)%H] + grid[(i+1)%W][j-1] + grid[(i+1)%W][(j+1)%H]
            #write the new cell state
            if not (COUNT_CASES[count] == "stay"):
                new_grid[i][j] = COUNT_CASES[count]
            else:
                new_grid[i][j] = grid[i][j]
    return new_grid


#main function for refreshing the screen and drawing the grid
def drawGrid(grid, screen, light, dark):
    screen.fill(light)

    #these two draw the grid
    for i in range(W):
        pygame.draw.line(screen, dark, [i*(SQUARE_SIDE+1),0], [i*(SQUARE_SIDE+1),H*(SQUARE_SIDE+1)], 1)
    pygame.draw.line(screen, dark, [W*(SQUARE_SIDE+1),0], [W*(SQUARE_SIDE+1),H*(SQUARE_SIDE+1)], 1)
    for j in range(H):
        pygame.draw.line(screen, dark, [0,j*(SQUARE_SIDE+1)], [W*(SQUARE_SIDE+1),j*(SQUARE_SIDE+1)], 1)
    pygame.draw.line(screen, dark, [0, H*(SQUARE_SIDE+1)], [W*(SQUARE_SIDE+1),H*(SQUARE_SIDE+1)], 1)

    #this fills in alive cells
    for j in range(H):
        for i in range(W):
            if grid[i][j] == 1:
                pygame.draw.rect(screen, dark, [i*(SQUARE_SIDE+1)+1+1, j*(SQUARE_SIDE+1)+1+1, SQUARE_SIDE-2, SQUARE_SIDE-2], 0)
        
    #updates the full display Surface to the screen
    pygame.display.flip()


#updates the window's caption based on current speed and pause state
def updateCaption(screen, frames_until_update, unpaused):
    if unpaused:
        pygame.display.set_caption('Conway\'s Game of Life -- Speed: {:.4f}'.format(1/frames_until_update))
    else:
        pygame.display.set_caption('Conway\'s Game of Life -- Speed: {:.4f} -- PAUSED'.format(1/frames_until_update))


#draws the splashscreen and waits for input before going on to the simulation
def splashscreen():

    light = (255, 255, 255)
    dark = (0, 0, 0)

    splashW = 500
    splashH = 450
    
    #set up screen
    size = (splashW, splashH)
    screen = pygame.display.set_mode(size)

    screen.fill(light)

    #set up fonts
    myfont = pygame.font.SysFont("monospace", 15)
    titlefont = pygame.font.SysFont("monospace", 25)

    #draw text to screen
    title = titlefont.render("Conway's Game of Life", 1, dark)
    screen.blit(title, (splashW/2-title.get_width()/2, 50))
    
    label = myfont.render("Left click: turn cell on/off", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150))
    label = myfont.render("Right click/space bar: pause/unpause simulation", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*1))
    label = myfont.render("Down arrow key/mouse wheel down: slow down simulation", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*2))
    label = myfont.render("Up arrow key/mouse wheel up: speed up simulation", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*3))
    label = myfont.render("C: clear board", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*4))
    label = myfont.render("1-5: change palette", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*5))
    label = myfont.render("Escape: exit the simulation", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*6))
    label = myfont.render("press any key to proceed to simulation", 1, dark)
    screen.blit(label, (splashW/2-label.get_width()/2, 150+(label.get_height()+10)*8))
    
    #update screen
    pygame.display.flip()

    #wait for any input
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                done = True


#manages player input, paused state and screen update rate during the simulation
def game():
    done = False
    clicked_position = [0, 0]
    frames_passed = 0
    unpaused = False

    light = (255, 255, 255)
    dark = (0, 0, 0)

    size = (W*(SQUARE_SIDE+1)+1, H*(SQUARE_SIDE+1)+1)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    frames_until_update = STARTING_FRAMES_UNTIL_UPDATE
    updateCaption(screen, frames_until_update, unpaused)

    grid = [[0 for x in range(H)] for y in range(W)]

    #main game loop
    while not done:
        pressed = pygame.key.get_pressed()
        #handles input
        for event in pygame.event.get():
            #window's exit button
            if event.type == pygame.QUIT:
                done = True
            #key input
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                if event.key == pygame.K_SPACE:
                    unpaused = not unpaused
                    updateCaption(screen, frames_until_update, unpaused)
                if event.key == pygame.K_c:
                    grid = [[0 for x in range(H)] for y in range(W)]
                if event.key == pygame.K_DOWN or event.key == pygame.K_LEFT:
                    frames_until_update += 1
                    updateCaption(screen, frames_until_update, unpaused)
                if event.key == pygame.K_UP or event.key == pygame.K_RIGHT:
                    if frames_until_update > 1:
                        frames_until_update -= 1
                        updateCaption(screen, frames_until_update, unpaused)
                if event.key == pygame.K_1:
                    light = (255, 255, 255)
                    dark = (0, 0, 0)
                if event.key == pygame.K_2:
                    light = (227, 213, 184)
                    dark = (208, 57, 88)
                if event.key == pygame.K_3:
                    light = (247, 176, 42)
                    dark = (232, 113, 16)
                if event.key == pygame.K_4:
                    light = (255, 252, 151)
                    dark = (146, 31, 58)
                if event.key == pygame.K_5:
                    light = (241, 234, 220)
                    dark = (20, 147, 165)
                
            #mouse input
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #left mouse button
                    clicked_position = pygame.mouse.get_pos()
                    grid[clicked_position[0]//(SQUARE_SIDE+1)][clicked_position[1]//(SQUARE_SIDE+1)] = not grid[clicked_position[0]//(SQUARE_SIDE+1)][clicked_position[1]//(SQUARE_SIDE+1)]
                elif event.button == 3: #right mouse button
                    unpaused = not unpaused
                    updateCaption(screen, frames_until_update, unpaused)
                elif event.button == 4: #wheel rolled up
                    if frames_until_update > 1:
                        frames_until_update -= 1
                        updateCaption(screen, frames_until_update, unpaused)
                elif event.button == 5: #wheel rolled down
                    frames_until_update += 1
                    updateCaption(screen, frames_until_update, unpaused)
                    
        #calls update function based on update speed and pause state
        if unpaused:
            if frames_passed >= frames_until_update:
                grid = updateGrid(grid)
                frames_passed = 0
            frames_passed += 1

        #draws screen and passes enough time to keep up the framerate using pygame's clock
        drawGrid(grid, screen, light, dark)
        clock.tick(FRAMERATE)
        


#main function; initializes pygame, handles flow of screens and ultimately kills program
def main():
    #magic words to center the screens
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    pygame.init()

    splashscreen()
    
    game()

    pygame.quit()


#no need to import this I guess
if __name__ == "__main__":
    main()
