import pygame, sys, random
from pygame.locals import *
from itertools import chain

# Bonjour cher correcteur
# Ce Démineur est écrit avec un mauvaise format
#   un seul fichier, éléments redondants, snipets copier coller d'internet
# Je vous pris de m'en excuser, je découvre à peine pygame et ses concepts
# Ainsi je me suis concentré sur le fonctionnement du démineur 
#   plutôt que sur la forme et la maintenabilité du code

pygame.init()

# Preset of const
## Frames
FPS = 60
FramePerSec = pygame.time.Clock()

## Colors
WHITE = (255, 255, 255)
GRAY = (169,169,169)
RED = (255,0,0)
BLACK = (0,0,0)
## Fonts
FONT = pygame.font.SysFont( None, 36 ) 

## Screen information
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 250

# Game Window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Démineur")

# Clickable Tile
# Might be a hint
# Might be a bomb
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.size = size
        self.imageGray()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x*(size+1),y*(size+1))
        self.isBomb = False
        self.isFound = False
        self.isNumber = False
        self.flag = pygame.image.load("assets/flag.png").convert_alpha().copy()
    
    def imageGray(self):
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(GRAY)

    def imageFlag(self):
        self.image.blit(self.flag,(self.size/4,self.size/4))

    def getPos(self):
        return (self.x*(self.size+1), self.y*(self.size+1))

    def becomeBomb(self):
        self.isBomb = True
    
    def drawNumber(self, number):
        numberText = "% s" % number
        number_image = FONT.render( numberText, True, BLACK, GRAY )
        number_size = FONT.size(numberText)
        drawX = self.size/2 - (number_size[0] / 2.)
        drawY = self.size/2 - (number_size[1] / 2.)
        self.image.blit(number_image,(drawX,drawY))
        self.isNumber = True

#Clickable Button
class Button(pygame.sprite.Sprite):
    def __init__(self, text):
        pygame.sprite.Sprite.__init__(self)
        self.image = FONT.render( text, True, BLACK, GRAY )
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, BLACK, self.rect, 1)

class GameLoop:
    def __init__(self) -> None:
    # Preset of Game var
        ## The Game Grid
        self.grid = [[]]
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                newTile = Tile(i,j,25)
                self.grid[i].append(newTile)

        ## States var
        self.bombCount = 9
        self.bombFound = 0
        self.gameStarted = False
        self.gameLoopOngoing = True
        self.gameLost = False
        self.postGameLoopOngoing = True

        ## Buttons
        self.restartButton = Button("Commencer une nouvelle partie")

## Methods
    def startGame(self, pos):
        tileSample = random.sample(list(chain.from_iterable(self.grid)),self.bombCount)
        needToFindAnotherTile = False
        for bombTile in tileSample:
            if bombTile.rect.collidepoint(pos):
                needToFindAnotherTile = True
                continue
            bombTile.becomeBomb()
            while(needToFindAnotherTile):
                anotherTile = random.choice(list(chain.from_iterable(self.grid)))
                if anotherTile.rect.collidepoint(pos) or anotherTile.isBomb:
                    continue
                anotherTile.becomeBomb()
                needToFindAnotherTile = False
    
    def listTheNeighbors(self,x,y):
        neighbors = []
        if x != 0:
            neighbors.append((x-1,y))
            if y != 0:
                neighbors.append((x-1,y-1))
            if y != 8:
                neighbors.append((x-1,y+1))
        if y != 0:
            neighbors.append((x,y-1))
        if y != 8:
            neighbors.append((x,y+1))
        if x != 8:
            neighbors.append((x+1,y))
            if y != 0:
                neighbors.append((x+1,y-1))
            if y != 8:
                neighbors.append((x+1,y+1))
        return neighbors
        
    def checkNeighborhood(self, x,y):
        bombCount = 0
        if x != 0:
            if self.grid[x-1][y].isBomb :
                bombCount += 1
            if y != 0 and self.grid[x-1][y-1].isBomb :
                bombCount += 1
            if y != 8 and self.grid[x-1][y+1].isBomb :
                bombCount += 1
        if y != 0 and self.grid[x][y-1].isBomb :
            bombCount += 1
        if y != 8 and self.grid[x][y+1].isBomb :
            bombCount += 1
        if x != 8:
            if self.grid[x+1][y].isBomb :
                bombCount += 1
            if y != 0 and self.grid[x+1][y-1].isBomb :
                bombCount += 1
            if y != 8 and self.grid[x+1][y+1].isBomb :
                bombCount += 1
        return bombCount

    def leftClick(self, tile):
        if not tile.isFound:
            if tile.isBomb:
                self.gameLoopOngoing = False
                self.gameLost = True
            else :
                bombCount = self.checkNeighborhood(tile.x,tile.y)
                tile.drawNumber(bombCount)
                if bombCount == 0 :
                    self.showAllZeros(tile.x, tile.y)

    def rightClick(self, tile):
        if tile.isFound:
            tile.isFound = False
            self.bombFound -= 1
            tile.imageGray()
            if tile.isBomb:
                self.bombCount += 1

        elif not tile.isNumber :
            tile.isFound = True
            self.bombFound += 1
            tile.imageFlag()
            if tile.isBomb:
                self.bombCount -= 1

        if self.bombCount == 0:
            self.gameLost = False
            self.gameLoopOngoing = False

    def showAllZeros(self, x,y): 
        neighbors = self.listTheNeighbors(x, y)
        for coordonnee in neighbors:
            if self.grid[coordonnee[0]][coordonnee[1]].isNumber:
                continue
            bombNumber = self.checkNeighborhood(coordonnee[0], coordonnee[1])
            self.grid[coordonnee[0]][coordonnee[1]].drawNumber(bombNumber)
            if bombNumber == 0 :
                self.showAllZeros(coordonnee[0],coordonnee[1])
        

# Game loop
    #game
    def run(self):
        while self.gameLoopOngoing:
            # Event handling     
            for event in pygame.event.get():              
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if not self.gameStarted:
                        self.startGame(pos)
                        self.gameStarted = True
                    for line in self.grid:
                        for tile in line:
                            if tile.rect.collidepoint(pos):
                                if event.button == 1 :
                                    self.leftClick( tile)
                                if event.button == 3 :
                                    self.rightClick(tile)

            # Display of game self.grid      
            for line in self.grid:
                for tile in line:
                    DISPLAYSURF.blit(tile.image, tile.getPos())

            infoBulle = FONT.render( "Nombre de bombes marquées " + str(self.bombFound), True, BLACK, WHITE )
            DISPLAYSURF.blit(infoBulle, (280,25))

            # Next Frame
            pygame.display.update()
            FramePerSec.tick(FPS)

    def posGame(self):
        while self.postGameLoopOngoing:
            # Event handling     
            for event in pygame.event.get():              
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.restartButton.rect.collidepoint(pos):
                        self.postGameLoopOngoing = False
            if self.gameLost:
                infoBulleOne = FONT.render( "Une bombe a explosée ! ", True, BLACK, WHITE )
                infoBulleTwo = FONT.render( "La partie est perdue !", True, BLACK, WHITE )
                
                DISPLAYSURF.blit(infoBulleOne, (280,55))
                DISPLAYSURF.blit(infoBulleTwo, (280,85))
            else :
                infoBulleOne = FONT.render( "La grille est déminée !", True, BLACK, WHITE )
                infoBulleTwo = FONT.render( "La partie est gagnée !", True, BLACK, WHITE )
                
                DISPLAYSURF.blit(infoBulleOne, (280,55))
                DISPLAYSURF.blit(infoBulleTwo, (280,85))
            
            self.restartButton.rect.topleft = (280,115)
            DISPLAYSURF.blit(self.restartButton.image, (280,115))

            # Next Frame
            pygame.display.update()
            FramePerSec.tick(FPS)
        
while True :
    testGame = GameLoop()
    testGame.run()
    testGame.posGame()
    DISPLAYSURF.fill(WHITE)

# Hopefully never needed
pygame.quit()