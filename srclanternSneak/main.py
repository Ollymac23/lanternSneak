import pygame
from pathlib import Path
import random as rand
import sys

# setup for assets access that is fault proof for compiling with pyinstaller #
def resource_path(relative):
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative
    return Path(__file__).resolve().parent.parent / relative


# pygame set up code #
pygame.init()
screen = pygame.display.set_mode((512, 512))
clock = pygame.time.Clock()
running = True
stuck = False
timeBegin = 0
highScore = None


# constants and other miscelanious variables #

ASSETS = resource_path("assets")
SCALE = 2
ZOMBIE_COUNT = 6
distMove = 32
TILE = 32
KEY_MOVES = {
    pygame.K_w: (0, -distMove), pygame.K_UP: (0, -distMove),
    pygame.K_a: (-distMove, 0), pygame.K_LEFT: (-distMove, 0),
    pygame.K_s: (0, distMove), pygame.K_DOWN: (0, distMove),
    pygame.K_d: (distMove, 0), pygame.K_RIGHT: (distMove, 0)
    
}
REPEAT_DELAY = 150
ROCK_COUNT = 72
WEB_COUNT = 8
MAX_HEALTH = 15
backgroundColor = (100, 100, 100)
moveTimer = 150
state = "mainMenu"



# essential functions for generating positions for randomised sprites #
def GenerateMove():
    direction = rand.randint(0, 3)
    match direction:
        case 0:
            move = (0, -distMove)
        case 1:
            move = (distMove, 0)
        case 2:
            move = (0, distMove)
        case 3:
            move = (-distMove, 0)
    return move

def GeneratePos():
    x = (rand.randint(0, 15))*TILE
    y = (rand.randint(0, 15))*TILE

    return ((x, y), (x//32, y//32))


# all classes for sprites and buttons. the backbone of all the codebase #
class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, image=None):
        super().__init__()
        self.health = MAX_HEALTH
        if image is None:
            image = pygame.Surface((TILE, TILE))
            image.fill((255, 255, 255))
            self.image = image
        self.rect = self.image.get_rect(center=(width, height))
        self.pos = pygame.Vector2(self.rect.center)
        self.pumpkins = 0


    def update(self):
        self.pos = pygame.Vector2(self.rect.center)
        self.rect = self.image.get_rect(center=self.pos)
        if pygame.sprite.spritecollide(player, exitGate, False):
            FinishGame()
        if self.health < 1:
            GameOver()

        if pygame.sprite.spritecollide(player, zombies, False):
            self.health -= 1



    def move(self, dx, dy):
        global stuck
        self.rect.x += dx
        self.rect.y += dy
        if pygame.sprite.spritecollide(player, obstacles, False):
            self.rect.x -= dx
            self.rect.y -= dy
        if pygame.sprite.spritecollide(player, webs, False):
            stuck = True
        if 0 > self.rect.x or self.rect.x > 510:
            self.rect.x -= dx
        if 0 > self.rect.y or self.rect.y > 510:
            self.rect.y -= dy

    def getWindow(self):
        length = self.pumpkins*2 + 3
        half = length//2
        darkness = pygame.Surface((512, 512), pygame.SRCALPHA)
        darkness.fill((0, 0, 0, 255))
        relativePos = (-(half)*TILE, -(half)*TILE)

        hole = pygame.Rect(
            self.rect.x - half * TILE,
            self.rect.y - half *TILE,
            length*TILE,
            length*TILE
        )


        pygame.draw.rect(darkness, (0, 0, 0, 0), hole)
        return darkness





class Web(pygame.sprite.Sprite):
    def __init__(self, tilex, tiley, image=None):
        super().__init__()
        if image is None:
            image = pygame.Surface((TILE, TILE))
            image.fill((200, 200, 200))
        self. image = image
        self.rect = self.image.get_rect(topleft=(tilex*TILE, tiley*TILE))


class Rock(pygame.sprite.Sprite):
    def __init__(self, tilex, tiley, image=None):
        super().__init__()
        if image is None:
            image = pygame.Surface((TILE, TILE))
            image.fill((60, 60, 60))
        self.image = image
        self.rect = self.image.get_rect(topleft=(tilex*TILE, tiley*TILE))


class Zombie(pygame.sprite.Sprite):
    def __init__(self, image=None):
        super().__init__()
        if image is None:
            image = pygame.Surface((TILE, TILE))
            image.fill((64, 150, 64))
        self.image = image
        self.rect = self.image.get_rect()
        pos, tilePos = GeneratePos()
        while tilePos in rocks:
            pos, tilePos = GeneratePos()
        self.rect.topleft = pos


    def move(self):

        dx, dy = GenerateMove()

        self.rect.x += dx
        self. rect.y += dy
        failed = 0

        while pygame.sprite.spritecollide(self, obstacles, False) or self.rect.x < 0 or self.rect.x > 510 or self.rect.y < 0 or self.rect.y > 510:
            self.rect.x -= dx
            self.rect.y -= dy
            
            if failed > 4:
                self.kill()
            failed += 1
            dx, dy = GenerateMove()

            self.rect.x += dx
            self.rect.y += dy


class Exit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        image = pygame.Surface((TILE, TILE))
        image.fill((0, 255, 0))
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (14*TILE, 14*TILE)


class Button:
    def __init__(self, text, rect, font, callback, color=(100, 100, 100), hoverColor=(125, 125, 125), textColor=(255, 255, 255)):
        self.label = font.render(text, False, textColor)
        self.rect = pygame.rect.Rect(rect)
        self.rect.center = rect[0]
        self.color = color
        self.hoverColor = hoverColor
        self.labelRect = self.label.get_rect(center=self.rect.center)
        self.callback = callback

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface, self.hoverColor if hovered else self.color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (20, 20, 20), self.rect, 2, border_radius=4)
        surface.blit(self.label, self.labelRect)


class Pumpkin(pygame.sprite.Sprite):
    def __init__(self, rocks, image=None):
        super().__init__()
        if image == None:
            image = pygame.Surface((TILE, TILE))
            image.fill((250, 230, 0))
        self.image = image
        self.rect = self.image.get_rect()
        pos, tilePos = GeneratePos()
        j, k = tilePos
        while j < 3 and k < 3:
            pos, tilePos = GeneratePos()
            j, k = tilePos
        while j > 12 and k > 12:
            pos, tilePos = GeneratePos()
            j, k = tilePos
        while tilePos in rocks:
            pos, tilePos = GeneratePos()
            j, k = tilePos
        self.rect.topleft = (j*32, k*32)
        self.collected = False
    def update(self):
        if pygame.sprite.spritecollide(player, pumpkins, False):
            for sprite in pumpkins:
                if sprite.rect.topleft == player.rect.topleft and sprite.collected == False:
                    player.pumpkins += 1
                    sprite.collected = True
                    pumpkins.remove(sprite)



# a very powerful selection of functions used for controlling the state of the game #
def StartGame():
    global state
    state = "playing"
    global timeBegin
    timeBegin = pygame.time.get_ticks()

def FinishGame():
    global timeStop
    timeStop = pygame.time.get_ticks()
    global state
    state = "finished"
    print(player.pumpkins)

def UpdateHighScore(score):
    global highScore
    if highScore is None or highScore > score:
        highScore = score

def ReturnMenu():
    global state
    state = "mainMenu"
    ResetGame()

def GameOver():
    global state
    state = "gameOver"
    ResetGame()

# a font used for drawing buttons #
buttonFont = pygame.font.Font(ASSETS / "Pixelta.ttf", 32)


# all buttons created #
startButton = Button("PLAY", ((256, 400), (85, 40)), buttonFont, StartGame)
restartButton = Button("MAIN MENU", ((256, 464), (140, 40)), buttonFont, ReturnMenu)

# all sprite groups apart from the player established #
obstacles = pygame.sprite.Group()
webs = pygame.sprite.Group()
zombies = pygame.sprite.Group()
exitGate = pygame.sprite.Group()
pumpkins = pygame.sprite.Group()

# exit gate sprite is added to its group #
exitGate.add(Exit())

# a rocks position array used solely to make sure other sprites arent drawn inside a rock #
rocks = []

# player stuff (all sprites is a sprite group with only the player) #
player = Player(16, 16)
all_sprites = pygame.sprite.Group(player)
dt = 0
held = []
queued = None

#title stuff #
titleFont = pygame.font.Font(ASSETS / "Pixelta.ttf", 64)
titleFont.align = pygame.FONT_CENTER
title = titleFont.render("Lantern Sneak", False, (255, 255, 255))
titleRect = title.get_rect(center=(256, 64))

#description stuff #
descriptionFont = pygame.font.Font(ASSETS / "Pixelta.ttf", 32)
descriptionFont.align = pygame.FONT_CENTER
description = descriptionFont.render("You find yourself in a pitch black graveyard. You must find all the pumpkins to keep your light alive and find the exit. Good luck!", False, (255, 255, 255), wraplength=512,)
descriptionRect = description.get_rect(center=(256, 200))

#other text for dying #
GameOverText = titleFont.render("GAME OVER", False, (255, 255, 255))
GameOverRect = GameOverText.get_rect(center=(256, 128))

#restart instructions #
instructionText = descriptionFont.render("Main menu to play again", False, (255, 255, 255))
instructionRect = instructionText.get_rect(center=(256, 256))

# a frame count used for declaring frequency of events such as zombie movement #
frameCount = 0

# a function that clears all game dependent variables and fills required arrays such as rocks and generates all sprites for the next game #
def ResetGame():
    global rocks, held, queued, stuck
    obstacles.empty()
    webs.empty()
    zombies.empty()
    rocks = []
    player.health = MAX_HEALTH
    player.pumpkins = 0

    for i in range(ROCK_COUNT):
        j = rand.randint(0, 15)
        k = rand.randint(0, 15)
        if j < 3 and k < 3:
            continue
        if j > 12 and k > 12:
            continue
        rocks.append((j, k))
        obstacles.add(Rock(j, k))
    for i in range(WEB_COUNT):
        j = rand.randint(0, 15)
        k = rand.randint(0, 15)
        if j < 3 and k < 3:
            continue
        if j > 12 and k > 12:
            continue

        if (j, k) not in rocks:
            webs.add(Web(j, k))

    for i in range(ZOMBIE_COUNT):
        zombies.add(Zombie())
    pumpkins.empty()
    for i in range(3):
        pumpkins.add(Pumpkin(rocks))

    player.rect.topleft = (0, 0)
    held = []
    queued = None
    stuck = None

# called once at boot to populate sprites #
ResetGame()

# game loop #
while running:

    frameCount += 1
    dt = clock.tick(60)
    moveTimer = max(0, moveTimer - dt)


    # event handler including player movement #
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key in KEY_MOVES:
            held.append(event.key)
            queued = event.key

        elif event.type == pygame.KEYUP and event.key in held:
            held.remove(event.key)
        else:
            startButton.handleEvent(event)
            restartButton.handleEvent(event)





    if state == "playing":

        # event handling limited to player movement to prevent the player being moved prior to start up #
        key = None
        if queued is not None:
            key = queued
            queued = None
            if stuck:
                moveTimer = 1000
                stuck = False
            else:
                moveTimer = REPEAT_DELAY
        elif held and moveTimer == 0:
            key = held[-1]
            if stuck:
                moveTimer = 1000
                stuck = False
            else:
                moveTimer = REPEAT_DELAY


        if key is not None:
            player.move(*KEY_MOVES[key])

        player.update()

        for sprite in pumpkins:
            sprite.update()

        # drawing stuff
        screen.fill((100, 100, 100))

        # stuff to be seen
        all_sprites.draw(screen)

        exitGate.draw(screen)

        if frameCount % 45 == 0:
            for zombie in zombies:
                zombie.move()


        obstacles.draw(screen)

        webs.draw(screen)

        pumpkins.draw(screen)

        screen.blit(player.getWindow())

        zombies.draw(screen)


        for i in range(17):
            pygame.draw.line(screen, (20, 20, 20), (i*32 - 1, 0), (i*32 - 1, 512), 2)
            pygame.draw.line(screen, (20, 20, 20), (0, i*32 - 1), (512, i*32 - 1), 2)


    elif state == "finished":


        time = (timeStop - timeBegin)/1000
        UpdateHighScore(time)
        if player.pumpkins > 2:
            screen.fill((255, 130, 0))
        else:
            screen.fill((100, 100, 100))
        highScoreText = titleFont.render(f"Best time: {highScore}s", False, (255, 255, 255))
        highScoreRect = highScoreText.get_rect()
        highScoreRect.center = (256, 128)
        screen.blit(highScoreText, highScoreRect)



        score = titleFont.render(f"Your time: {time}s", False, (255, 255, 255))
        scoreRect = score.get_rect()
        scoreRect.center = (256, 256)
        screen.blit(score, scoreRect)
        restartButton.draw(screen)


    elif state == "mainMenu":

        screen.fill((100, 100, 100))
        screen.blit(title, titleRect)
        screen.blit(description, descriptionRect)
        startButton.draw(screen)


    elif state == "gameOver":
        screen.fill((100, 10, 10))
        screen.blit(GameOverText, GameOverRect)
        screen.blit(instructionText, instructionRect)
        restartButton.draw(screen)



    pygame.display.flip()


pygame.quit()

