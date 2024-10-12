# -*- coding:utf-8 -*-
# Murilo Montalvão Pereira - 2516985 
#  UTFPR Física Teorica A 
# Simulador de Colisões
import imgui
import OpenGL.GL as gl
from OpenGL.GLU import *
from imgui.integrations.pygame import PygameRenderer
import pygame, sys
from random import randint, uniform
from math import sqrt, cos, pi, sin

def draw_circle(x, y, radius, segments, color):
    gl.glColor3f(color[0], color[1], color[2])
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    for i in range(segments + 1):
        angle = 2 * pi * i / segments
        circle_x = x + radius * cos(angle)  # Adiciona o deslocamento x
        circle_y = y + radius * sin(angle)  # Adiciona o deslocamento y
        gl.glVertex2f(circle_x, circle_y)
    gl.glEnd()

class Ball:
    width = -1
    height = -1
    def __init__(self):
        self.size = randint(8, 16)
        self.mass = 3.14 * self.size * self.size * 0.001
        self.velocity_x = uniform(-3, 3)
        self.velocity_y = uniform(-3, 3)
        random = randint(0,100000)
        if random/100%10 < 5:
            self.color = (uniform(0.3,1), uniform(0.3,1), uniform(0.3,1))
        elif random%3 == 0:
            self.color = (1, 0, 0)
        elif random%3 == 1:
            self.color = (0, 1, 0)
        else:
            self.color = (0, 0, 1)
        self.x = 0
        self.y = 0
        pass
    def draw(self):
        draw_circle(self.x,self.y,self.size, 30, self.color)
    
    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
    def wallColision(self):
        #função para limitar as bolas ao tamanho da janela
        if self.x <= self.size or self.x >= Ball.width - self.size:
            self.velocity_x = -self.velocity_x
            if self.x > Ball.width - self.size: self.x = Ball.width - self.size
            elif self.x < self.size: self.x = self.size
        if self.y <= self.size or self.y >= Ball.height - self.size:
            self.velocity_y = -self.velocity_y
            if self.y > Ball.height - self.size: self.y = Ball.height - self.size
            elif self.y < self.size: self.y = self.size
            # se a bola estiver fora ou encostando nas bordas, a velocidade dela é simplesmente invertida (supondo que a massa das bordas sejam infinitas)
            

def ballSpawn(ball, balls): # função para impedir que as bolas começem enconstadas ou sobrepostas
    spawnoccupied = False
    x = randint(32, Ball.width - 32)
    y = randint(32, Ball.height - 32)
    for i in balls:
        if i != ball:
            xi = i.x
            yi = i.y
            
            distance = sqrt( ( x - xi )**2 + ( y - yi )**2 )
                
            if distance > ball.size + i.size:
                pass
            else: spawnoccupied = True
    if spawnoccupied == False:
        ball.x = x
        ball.y = y
        return 1
    return 0        


def sweepPrune(ball, llist, cont): # função que checa possiveis colisões e retorna uma lista com elas
    sortedList = []
    llen = len(llist)
    for i in range(cont, llen):
        if (abs(ball.x - llist[i].x) <= ball.size + llist[i].size) and (abs(ball.y - llist[i].y) <= ball.size + llist[i].size):
            sortedList.append(llist[i])
    return sortedList

def collisionDetection(ball, balls, cont): # função que detecta colisão e calcula a física envolvida caso haja colisão
        cols = 0
        nVTG_x = 0.0
        nVTG_y = 0.0
        nVector_x = 0.0
        nVector_y = 0.0
        sweep = sweepPrune(ball, balls, cont)
        for i in sweep:
            if ball == i: 
                continue
            distance = sqrt( (ball.x - i.x) * (ball.x - i.x) + (ball.y - i.y) * (ball.y - i.y) )
            if distance <= ball.size + i.size:
                nVector_x = (i.x - ball.x) / sqrt( (i.x - ball.x)**2 + (i.y - ball.y)**2 )
                nVector_y = (i.y - ball.y) / sqrt( (i.x - ball.x)**2 + (i.y - ball.y)**2 )

                nVTG_x = -nVector_y
                nVTG_y = nVector_x

                tgVelBall = (nVTG_x * ball.velocity_x) + (nVTG_y * ball.velocity_y)
                tgVelBalli = (nVTG_x * i.velocity_x) + (nVTG_y * i.velocity_y)

                nVelBall = (nVector_x * ball.velocity_x) + (nVector_y * ball.velocity_y)
                nVelBalli = (nVector_x * i.velocity_x) + (nVector_y * i.velocity_y)

                finalVel = ( ball.mass - i.mass ) / ( ball.mass + i.mass ) * nVelBall

                finalVel +=  ( 2 * i.mass ) / ( ball.mass + i.mass ) * nVelBalli

                finalVel1 = ( 2 * ball.mass ) / ( ball.mass + i.mass ) * nVelBall

                finalVel1 += ( i.mass - ball.mass ) / ( ball.mass + i.mass ) * nVelBalli 

                fVTG_x = tgVelBall * nVTG_x
                fVTG_y = tgVelBall * nVTG_y
                fVTGi_x = tgVelBalli * nVTG_x
                fVTGi_y = tgVelBalli * nVTG_y
                ball.velocity_x = finalVel * nVector_x + fVTG_x
                ball.velocity_y = finalVel * nVector_y + fVTG_y
                i.velocity_x = finalVel1 * nVector_x + fVTGi_x
                i.velocity_y = finalVel1 * nVector_y + fVTGi_y
                if distance < ball.size + i.size:
                    ball.x += (distance - i.size - ball.size) * nVector_x
                    ball.y += (distance - i.size - ball.size) * nVector_y
                cols += 1
        return cols

def updateCollisions(coll): # Imprime na tela quantas colisões até o momento
    collisions = str(int(coll))
    imgui.text("collisions: " + collisions)

def updateFPS(clock): # Imprime na tela quantos Frames Por Segundo
    fPS = str(int(clock.get_fps()))
    imgui.text("FPS: " + fPS)

def updateKinetics(kinectics): # Imprime na tela a energia cinética total do sistema
    kinetics = str(float( "%.2f" % kinectics))
    imgui.text("Kinetics(J): " + kinetics)

def updateMomentum(momentum, momentum1): # Imprime na tela o momento linear em x e y total do sistema
    momentum = str(float( "%.2f" % momentum))
    momentum1 = str(float( "%.2f" % momentum1))
    imgui.text("Momentum x: " + momentum)
    imgui.text("Momentum y: " + momentum1)
    
def SpawnXBalls(qt_Balls, balls):
    prv_last_ball = len(balls)
    for i in range(prv_last_ball, prv_last_ball + qt_Balls): # Coloca as bolas em lugares diferentes e randomizados
        spawnDone = 0
        attempts = 0
        balls.append(Ball())
        while spawnDone == 0 and attempts < 300:
            spawnDone = ballSpawn(balls[i], balls)
            attempts += 1
        if attempts >= 300:
            balls.pop()
            break

def main():
    kinetics = 0
    momentum_x = 0
    momentum_y = 0
    cont = 1
    collisions = 0
    input_Qt_Balls = 0
    pygame.init()

    screen_size = 800, 600
    width = screen_size[0]
    height = screen_size[1] - 20
    Ball.width = width
    Ball.height = height
    fps = 60
    balls = []
    clock = pygame.time.Clock()
    imgui.create_context()
    screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF  | pygame.OPENGL | pygame.RESIZABLE)
    impl = PygameRenderer()
    gl.glEnable(gl.GL_MULTISAMPLE)
    gluOrtho2D(0, screen_size[0], 0, screen_size[1])
    isRunning = True
    while isRunning:
        imgui.get_io().display_size = screen_size
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('collisions: ', collisions)
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen_size = event.dict['size']

            impl.process_event(event)
        impl.process_inputs()       
        imgui.new_frame()
        clock.tick(fps)
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        cont = 1
        kinetics = 0
        momentum_x = 0
        momentum_y = 0
        for ball in balls:
            momentum_x += ball.velocity_x * ball.mass
            momentum_y += ball.velocity_y * ball.mass 
            ball.wallColision()
            collisions += collisionDetection(ball, balls, cont)
            cont += 1
            
            kinetics += (((sqrt(ball.velocity_x**2 + ball.velocity_y**2))**2) * ball.mass) / 2 
            
            ball.draw()
            ball.move()
        imgui.set_window_size_named("Status Menu", 180, 185)
        imgui.begin_main_menu_bar()
        imgui.text("Collision Simulator Between Particles")
        imgui.end_main_menu_bar()
        imgui.begin("Status Menu", False, imgui.core.WINDOW_NO_RESIZE)
        imgui.text("Balls:")
        imgui.same_line()
        imgui.push_item_width(75)
        input_Qt_Balls = imgui.input_int("", input_Qt_Balls)[1]
        if input_Qt_Balls < 0: input_Qt_Balls = 0
        if input_Qt_Balls > 300: input_Qt_Balls = 300
        if imgui.button("Spawn Balls"):
            SpawnXBalls(input_Qt_Balls, balls)
        if imgui.button("Clear Balls"):
            balls.clear()
        updateFPS(clock)
        updateCollisions(collisions)
        updateMomentum(momentum_x, momentum_y)
        updateKinetics(kinetics)
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        pygame.display.flip()

if __name__ == "__main__": main()
