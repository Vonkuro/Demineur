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
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900

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
        self.image = pygame.Surface([size, size])
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x*(size+1),y*(size+1))
        self.isBomb = False

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

# Preset of Game var
## The Game Grid
grid = [[]]
for i in range(9):
    grid.append([])
    for j in range(9):
        newTile = Tile(i,j,25)
        grid[i].append(newTile)

## States var
gameStarted = False

## Functions
def startGame(pos):
    tileSample = random.sample(list(chain.from_iterable(grid)),9)
    needToFindAnotherTile = False
    for bombTile in tileSample:
        if bombTile.rect.collidepoint(pos):
            needToFindAnotherTile = True
            continue
        bombTile.becomeBomb()
        while(needToFindAnotherTile):
            anotherTile = random.choice(list(chain.from_iterable(grid)))
            if anotherTile.rect.collidepoint(pos) or anotherTile.isBomb():
                continue
            anotherTile.becomeBomb()
            needToFindAnotherTile = False
    
def checkNeighborhood(x,y):
    bombCount = 0
    if x != 0:
        if grid[x-1][y].isBomb :
            bombCount += 1
        if y != 0 and grid[x-1][y-1].isBomb :
            bombCount += 1
        if y != 8 and grid[x-1][y+1].isBomb :
            bombCount += 1
    if y != 0 and grid[x][y-1].isBomb :
        bombCount += 1
    if y != 8 and grid[x][y+1].isBomb :
        bombCount += 1
    if x != 8:
        if grid[x+1][y].isBomb :
            bombCount += 1
        if y != 0 and grid[x+1][y-1].isBomb :
            bombCount += 1
        if y != 8 and grid[x+1][y+1].isBomb :
            bombCount += 1
    return bombCount

# Game loop
while True:
    # Event handling     
    for event in pygame.event.get():              
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            pos = pygame.mouse.get_pos()
            if not gameStarted:
                startGame(pos)
                gameStarted = True
            clicked_sprites = []
            for line in grid:
                for tile in line:
                    #Debug find bomb
                    if tile.isBomb:
                        tile.image.fill(RED)
                    if tile.rect.collidepoint(pos):
                        if tile.isBomb:
                            pass #endgame
                        else :
                            bombCount = checkNeighborhood(tile.x,tile.y)
                            tile.drawNumber(bombCount)
                        
                        

    # Display of game grid      
    for line in grid:
        for tile in line:
            DISPLAYSURF.blit(tile.image, tile.getPos())

    # Next Frame
    pygame.display.update()
    FramePerSec.tick(FPS)

# Hopefully never needed
pygame.quit()