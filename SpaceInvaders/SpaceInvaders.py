import pygame
import os
from pygame.locals import *
from random import randint
from sys import exit

def CenterMessage(screen,surface):
    return (screen.get_width() - surface.get_width())/2


def PrepareSound(filename):
    sound = pygame.mixer.Sound(filename)
    return sound

class Craft(object):
    def __init__(self,imagefiles,coord):
        self.shape = [pygame.image.load(imagefile) for imagefile in imagefiles]
        self.ship_width = self.shape[0].get_width()
        self.ship_height = self.shape[0].get_height()
        self.rect = pygame.Rect(coord,(self.ship_width, self.ship_height))
        self.ship_midwidth = self.ship_width/2
        self.firecolor=(255,0,0)
        self.firespeed = -800
        self.shotlength = 20

    def Show(self, surface,imageindex):
        surface.blit(self.shape[imageindex],(self.rect[0],self.rect[1]))

    def Move(self,speed_x,speed_y,time):
        distance_x = time *speed_x
        distance_y = time *speed_y
        self.rect.move_ip(distance_x,distance_y)

    def Fire(self):
        shot = Laser((self.rect[0]+self.ship_midwidth,self.rect[1]),self.firecolor,self.shotlength,self.firespeed,self.rect[1],15)
        return shot



class SpaceCraft(Craft):
    def __init__(self, imagefile,coord,min_coord,max_coord,lasersound):
        super(SpaceCraft,self).__init__(imagefile,coord)
        self.min_coord = min_coord
        self.max_coord = (max_coord[0] - self.ship_width,max_coord[1]-self.ship_height)
        self.lasersound = lasersound
    def Move(self,speed_x,speed_y,time):
        super(SpaceCraft,self).Move(speed_x,speed_y,time)
        for i in (0,1):
            if self.rect[i]< self.min_coord[i]:
                self.rect[i] = self.min_coord[i]
            if self.rect[i] > self.max_coord[i]:
                self.rect[i]= self.max_coord[i]

    def Fire(self):
        self.lasersound.play()
        return super(SpaceCraft,self).Fire()


class SpaceBackground:
    def __init__(self,screenheight,imagefile):
        self.shape = pygame.image.load(imagefile)
        self.coord = [0,0]
        self.coord2 = [0, - screenheight]
        self.y_original = self.coord[1]
        self.y2_original = self.coord2[1]

    def Show(self, surface):
        surface.blit(self.shape,self.coord)
        surface.blit(self.shape,self.coord2)

    def Scroll(self, speed_y, time):
        distance_y = speed_y *time
        self.coord[1]+= distance_y
        self.coord2[1]+=distance_y
        if self.coord2[1]>=0:
            self.coord[1] = self.y_original
            self.coord2[1] = self.y2_original

class Alien(Craft):
    def __init__(self, imagefile,coord, speed_x,speed_y):
        imagefiles = (imagefile,)
        super(Alien,self).__init__(imagefiles,coord)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.shot_height = 10
        self.firebaseline = self.ship_height
        self.firecolor=(255,255,0)
        self.firespeed = 200

    def Move(self, time):
        super(Alien, self).Move(self.speed_x,self.speed_x,time)
        if self.rect[0]>= 440 or self.rect[0] <=10:
            self.speed_x = -self.speed_x
        if self.rect[1] <= 10 or self.rect[1]>=440:
            self.speed_y = -self.speed_y
    def Show(self, surface):
        imageindex = 0
        super(Alien,self).Show(surface,imageindex)

    def Fire(self):
        theshot = Laser((self.rect[0]+self.ship_midwidth,self.rect[1]+self.firebaseline),self.firecolor,self.shot_height, self.firespeed,self.rect[1]+self.firebaseline,0)
        return theshot


class Laser:
    def __init__(self, coord, color, size, speed,refline,voffset):
        self.x1 = coord[0]
        self.y1 = coord[1]+voffset
        self.size = size
        self.color= color
        self.speed = speed
        self.refline = refline


    def DistanceTravelled(self):
        return abs(self.refline-self.y1)

    def Show(self, surface):
        pygame.draw.line(surface,self.color,(self.x1, self.y1),(self.x1, self.y1-self.size),3)

    def Move(self,time):
        distance = self.speed * time
        self.y1 += distance

    def GoneAbove(self,y):
        if self.y1<=y:
            return True
        else:
            return False
    def GoneBelow(self,y):
        pass


    def GetXY(self):
        return (self.x1 ,self.y1)


class ScoreBoard:
    def __init__(self, x, y, font, fontsize):
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(font,fontsize)
        self.score = 0

    def Change(self, amount):
        self.score += amount

    def Show(self, surface):
        scoretext = self.font.render("Score: "+str(self.score), True,(0,0,255))
        surface.blit(scoretext,(self.x, self.y))

    def GetValue(self):
        return self.score

    def SetValue(self, score):
        self.score = score


class ShieldMeter:
    def __init__(self, x, y, maxvalue, warnvalue):
        self.x = x
        self.y = y
        self.maxvalue = maxvalue
        self.warnvalue = warnvalue
        self.currentvalue = maxvalue
        self.shieldcolor = (0,255,0)


    def Show(self, surface):
        if self.currentvalue < self.warnvalue:
            self.shieldcolor = (255,0,0)
        else:
            self.shieldcolor = (0,255,0)
        pygame.draw.rect(surface,self.shieldcolor,(self.x, self.y, self.currentvalue,25))

    def Increase(self, amount):
        self.currentvalue += amount
        if self.currentvalue > self.maxvalue:
            self.currentvalue = self.maxvalue

    def Decrease(self, amount):
        self.currentvalue -= amount
        if self.currentvalue < 0:
            self.currentvalue = 0

    def GetValue(self):
        return self.currentvalue

    def SetValue(self,value):
        self.currentvalue = value
        if self.currentvalue > self.maxvalue:
            self.currentvalue = maxvalue
            if self.currentvalue < 0:
                self.currentvalue = 0

def GameOverShow(screen):
    font = pygame.font.SysFont("impact",32)
    gameovertext1 = font.render("Game Over!",True,(255,255,255))
    text_x = CenterMessage(screen, gameovertext1)
    screen.blit(gameovertext1,(text_x,280))
    gameovertext2 = font.render("Press R to Restart", True,(255,255,255))
    text_x = CenterMessage(screen, gameovertext2)
    screen.blit(gameovertext2,(text_x,320))
    return

def PlayMusic(soundfile):
    pygame.mixer.music.load(soundfile)
    pygame.mixer.music.play(-1)


def main():
    pygame.init()
    backspeed = 100
    laser = PrepareSound("shoot.wav")
    explosion = PrepareSound("invaderkilled.wav")
    spaceship_low = (0,0)
    screenwidth,screenheight=(480,640)
    spaceship_high = (screenwidth,screenheight)
    destroyed = PrepareSound("explosion.wav")
    shield = ShieldMeter(200,10,250,75)
    spaceship_pos = (240,540)
    screen = pygame.display.set_mode((screenwidth,screenheight),DOUBLEBUF,32)
    pygame.display.set_caption("Pygame Invaders")
    pygame.key.set_repeat(1,1)
    StarField = SpaceBackground(screenheight,"stars.jpg")
    shipimages = ('spaceship2.png', 'spaceship3.png')
    SpaceShip = SpaceCraft(shipimages,spaceship_pos,spaceship_low,spaceship_high,laser)
    clock = pygame.time.Clock()
    framerate = 60
    PlayMusic("spaceinvaders.ogg")
    firelist = []
    alienimage = ('alien1.png','alien2.png','alien3.png','alien4.png','alien5.png')
    numofaliens=8
    AlienShips = []
    alienfirelist = []
    laserdownlimit = screenheight - 40
    score = ScoreBoard(0,0,"impact",32)
    GameOver = False
    imageindex = 0
    flashcount = 0
    while True:

        time = clock.tick(framerate)/1000.0
        if not AlienShips:
            AlienShips = [Alien(alienimage[randint(0,len(alienimage)-1)],[randint(20,screenwidth-80),randint(20,screenheight-140)],randint(100,150),randint(100,150)) for i in range(0,numofaliens)]
        StarField.Scroll(backspeed,time)
        shipspeed_x = 0
        shipspeed_y = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                key = pygame.key.get_pressed()
                if key[K_q] :
                    pygame.quit()
                    exit()
                if key[K_r] and GameOver:
                    GameOver = False
                    shield.SetValue(250)
                    score.SetValue(0)
                if key[K_LEFT]:
                    shipspeed_x= -300
                if key[K_RIGHT]:
                    shipspeed_x = 300
                if key[K_UP]:
                    shipspeed_y= -300
                if key[K_DOWN]:
                    shipspeed_y= 300
                if key[K_SPACE] and not GameOver:
                    if firelist:
                        if firelist[-1].DistanceTravelled() >= 150 :
                            firelist.append(SpaceShip.Fire())
                    else:
                        firelist.append(SpaceShip.Fire())

            if event.type == USEREVENT+1:
                if flashcount < 10:
                    flashcount +=1
                if imageindex == 1:
                    imageindex = 0
                else:
                    imageindex = 1
            else:
                  imageindex = 0
                  flashcount = 0
                  pygame.time.set_timer(USEREVENT+1,0)




        SpaceShip.Move(shipspeed_x,shipspeed_y,time)
        StarField.Show(screen)
        SpaceShip.Show(screen,imageindex)
        score.Show(screen)
        shield.Show(screen)
        for AlienShip in AlienShips:
            AlienShip.Show(screen)
            AlienShip.Move(time)
            if randint(0,10)==9:
                if alienfirelist:
                    if alienfirelist[-1].DistanceTravelled()>=100:
                        alienfirelist.append(AlienShip.Fire())
                else:
                    alienfirelist.append(AlienShip.Fire())
        for theshot in alienfirelist:
            theshot.Move(time)
            theshot.Show(screen)
            if theshot.GoneBelow(laserdownlimit):
                alienfirelist.remove(theshot)
            else:
                if  SpaceShip.rect.collidepoint(theshot.GetXY()) and not GameOver:
                    destroyed.play()
                    shield.Decrease(25)
                    pygame.time.set_timer(USEREVENT+1,25)
                    if theshot in alienfirelist:
                        alienfirelist.remove(theshot)
        for theshot in firelist:
            theshot.Move(time)
            theshot.Show(screen)
            if theshot.GoneAbove(0):
                firelist.remove(theshot)
            else:
                for AlienShip in AlienShips:
                    if AlienShip.rect.collidepoint(theshot.GetXY()):
                        score.Change(10)
                        explosion.play()
                        if score.GetValue()%100 == 0:
                            shield.Increase(25)
                        if theshot in firelist:
                            firelist.remove(theshot)
                        AlienShips.remove(AlienShip)
        if shield.GetValue() ==0:
            GameOverShow(screen)
            GameOver = True

        pygame.display.update()

if __name__=='__main__':
    main()
