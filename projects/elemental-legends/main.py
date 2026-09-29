import pygame, random, math, sys
from pathlib import Path

pygame.init()
WIDTH, HEIGHT, FPS = 1280, 720, 60
WORLD_WIDTH, GROUND_Y = 5200, 570
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elemental Legends")
clock = pygame.time.Clock()

WHITE=(245,250,255); BLACK=(5,7,10); RED=(235,55,45)
FIRE=(255,75,15); FIRE_LIGHT=(255,205,65)
WATER=(45,155,245); WATER_LIGHT=(145,225,255)
EARTH=(145,100,55); EARTH_LIGHT=(205,160,90)
AIR=(220,245,255); AIR_BLUE=(105,205,255)
LIGHTNING=(185,225,255)

FONT_TITLE=pygame.font.SysFont("arial",28,True)
FONT_BIG=pygame.font.SysFont("arial",52,True)
FONT_MED=pygame.font.SysFont("arial",20,True)
FONT_SMALL=pygame.font.SysFont("arial",15)

ELEMENTS={
 "fire":{"color":FIRE,"damage":15,"speed":12,"radius":9},
 "water":{"color":WATER,"damage":13,"speed":11,"radius":10},
 "earth":{"color":EARTH,"damage":21,"speed":8,"radius":14},
 "air":{"color":AIR,"damage":11,"speed":15,"radius":8},
}

# Cached world background: avoids rebuilding a 1280x720 gradient every frame.
background=pygame.Surface((WORLD_WIDTH,HEIGHT))
for y in range(0,480,8):
    t=y/480
    c=(int(15+28*t),int(27+32*t),int(48+35*t))
    pygame.draw.rect(background,c,(0,y,WORLD_WIDTH,8))
pygame.draw.circle(background,(235,235,215),(WORLD_WIDTH-550,110),48)

for x in range(-100,WORLD_WIDTH+300,180):
    peak=350+int(math.sin(x*.011)*65)+random.randint(-25,25)
    pygame.draw.polygon(background,(28,42,55),[(x,570),(x+90,peak),(x+180,570)])

for x in range(-100,WORLD_WIDTH+300,260):
    peak=430+int(math.sin(x*.018)*40)
    pygame.draw.polygon(background,(34,54,50),[(x,570),(x+130,peak),(x+260,570)])

pygame.draw.rect(background,(24,92,125),(1650,505,900,65))
for x in range(1660,2550,45):
    pygame.draw.line(background,(70,170,195),(x,520),(x+25,520),2)

for bx in range(2850,3350,95):
    bh=random.randint(55,100)
    pygame.draw.rect(background,(82,63,48),(bx,570-bh,65,bh))
    pygame.draw.polygon(background,(120,48,40),[(bx-8,570-bh),(bx+32,570-bh-35),(bx+73,570-bh)])
    pygame.draw.rect(background,(215,185,100),(bx+25,538,15,32))

for rx in range(3900,4350,90):
    h=random.randint(60,150)
    pygame.draw.rect(background,(75,75,70),(rx,570-h,35,h))
    pygame.draw.rect(background,(105,105,95),(rx+38,570-h//2,25,h//2))

for tx in range(600,WORLD_WIDTH,180):
    if 1600<tx<2550: continue
    th=random.randint(50,80)
    pygame.draw.rect(background,(70,48,30),(tx,GROUND_Y-th,18,th))
    pygame.draw.circle(background,(38,95,62),(tx+9,GROUND_Y-th-25),35)

pygame.draw.rect(background,(30,31,30),(0,GROUND_Y,WORLD_WIDTH,HEIGHT-GROUND_Y))
pygame.draw.rect(background,(70,68,55),(0,GROUND_Y,WORLD_WIDTH,8))

particles=[]; projectiles=[]; enemies=[]; lightning=[]
score=combo=combo_timer=spawn_timer=0
camera_x=0

class Particle:
    def __init__(self,x,y,color,vx=None,vy=None,life=35,size=5):
        self.x=x; self.y=y
        self.vx=random.uniform(-4,4) if vx is None else vx
        self.vy=random.uniform(-4,4) if vy is None else vy
        self.life=life; self.max_life=life; self.color=color; self.size=size
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=.05; self.life-=1
    def draw(self,cam):
        if self.life>0:
            s=max(1,int(self.size*self.life/self.max_life))
            pygame.draw.circle(screen,self.color,(int(self.x-cam),int(self.y)),s)

def burst(x,y,color,amount=12,speed=4):
    for _ in range(amount):
        a=random.random()*math.tau; s=random.uniform(1,speed)
        particles.append(Particle(x,y,color,math.cos(a)*s,math.sin(a)*s,random.randint(20,45),random.randint(3,7)))

def ring(x,y,color,amount=35,speed=5):
    for i in range(amount):
        a=math.tau*i/amount
        particles.append(Particle(x,y,color,math.cos(a)*speed,math.sin(a)*speed,35,4))

class LightningBolt:
    def __init__(self,x):
        self.life=12; self.points=[(x,35)]; y=35
        while y<GROUND_Y:
            y+=random.randint(25,45)
            self.points.append((x+random.randint(-35,35),min(y,GROUND_Y)))
    def update(self): self.life-=1
    def draw(self,cam):
        if self.life>0:
            p=[(int(x-cam),int(y)) for x,y in self.points]
            pygame.draw.lines(screen,WHITE,False,p,8)
            pygame.draw.lines(screen,LIGHTNING,False,p,4)

class Projectile:
    def __init__(self,x,y,direction,element,damage=None,radius=None):
        d=ELEMENTS[element]
        self.x=x; self.y=y; self.direction=direction; self.element=element
        self.color=d["color"]; self.speed=d["speed"]
        self.damage=d["damage"] if damage is None else damage
        self.radius=d["radius"] if radius is None else radius
        self.knockback=5; self.life=100
    def update(self): self.x+=self.speed*self.direction; self.life-=1
    def dead(self): return self.life<=0 or self.x<-200 or self.x>WORLD_WIDTH+200
    def draw(self,cam):
        p=(int(self.x-cam),int(self.y))
        pygame.draw.circle(screen,self.color,p,self.radius+4,2)
        pygame.draw.circle(screen,self.color,p,self.radius)
        pygame.draw.circle(screen,WHITE,p,max(2,self.radius//3))

class Enemy:
    def __init__(self,x=None):
        self.x=WORLD_WIDTH-random.randint(50,500) if x is None else x
        self.y=GROUND_Y-50; self.health=50; self.max_health=50
        self.vx=0; self.speed=random.uniform(1,2); self.attack_timer=0
        self.burn_timer=0; self.burn_damage=0; self.burn_tick=0
    def ignite(self,damage=3,duration=180):
        self.burn_damage=damage; self.burn_timer=max(self.burn_timer,duration)
    def update(self):
        self.vx=-self.speed if self.x>player.x+45 else self.speed if self.x<player.x-45 else 0
        self.x=max(20,min(WORLD_WIDTH-60,self.x+self.vx))
        if self.burn_timer>0:
            self.burn_timer-=1; self.burn_tick-=1
            if self.burn_tick<=0:
                self.health-=self.burn_damage; self.burn_tick=30
                burst(self.x+random.randint(5,35),self.y+random.randint(5,35),FIRE,3,2)
        self.attack_timer-=1
        if abs(self.x-player.x)<55 and self.attack_timer<=0:
            player.health-=3 if player.avatar_state else 7
            player.hit_flash=8; self.attack_timer=50
    def draw(self,cam):
        x=int(self.x-cam); y=int(self.y)
        if self.burn_timer>0: pygame.draw.circle(screen,FIRE,(x+21,y+25),31,2)
        pygame.draw.rect(screen,(92,30,38),(x,y+15,42,35))
        pygame.draw.circle(screen,(145,72,65),(x+21,y+12),15)
        pygame.draw.rect(screen,BLACK,(x+13,y+10,4,4)); pygame.draw.rect(screen,BLACK,(x+26,y+10,4,4))
        pygame.draw.rect(screen,BLACK,(x,y-9,42,5))
        pygame.draw.rect(screen,RED,(x,y-9,int(42*max(0,self.health)/self.max_health),5))

def spawn_enemy():
    if len(enemies)<7:
        enemies.append(Enemy(min(WORLD_WIDTH-100,max(player.x+700,1000))))

class Player:
    def __init__(self):
        self.x=450; self.y=GROUND_Y-60; self.width=42; self.height=60
        self.vx=self.vy=0; self.grounded=True; self.facing=1
        self.health=100; self.energy=100; self.avatar_meter=100
        self.element="fire"; self.special_cd=0; self.attack_cd=0
        self.avatar_state=False; self.avatar_timer=0; self.cutscene=False
        self.hit_flash=0
    def update(self,keys):
        speed=11 if self.avatar_state else 6; accel=1.15 if self.avatar_state else .8
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.vx-=accel; self.facing=-1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vx+=accel; self.facing=1
        self.vx*=.84; self.vx=max(-speed,min(speed,self.vx))
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.grounded:
            self.vy=-20 if self.avatar_state else -15; self.grounded=False
        self.vy+=.72; self.x+=self.vx; self.y+=self.vy
        self.x=max(20,min(WORLD_WIDTH-self.width-20,self.x))
        if self.y+self.height>=GROUND_Y:
            self.y=GROUND_Y-self.height; self.vy=0; self.grounded=True
        self.energy=min(100,self.energy+(.65 if self.avatar_state else .18))
        self.special_cd=max(0,self.special_cd-1); self.attack_cd=max(0,self.attack_cd-1)
        if self.avatar_state:
            self.avatar_timer-=1; self.avatar_meter=max(0,self.avatar_timer/900*100)
            if self.avatar_timer<=0: self.exit_avatar()
        else: self.avatar_meter=min(100,self.avatar_meter+.06)
        self.hit_flash=max(0,self.hit_flash-1)
    def attack(self):
        if self.attack_cd>0 or self.energy<8: return
        self.attack_cd=6 if self.avatar_state else 10; self.energy-=8
        p=Projectile(self.x+21+self.facing*10,self.y+25,self.facing,self.element,28 if self.avatar_state else None,13 if self.avatar_state else None)
        p.knockback=10 if self.avatar_state else 5; projectiles.append(p)
        burst(self.x+self.facing*35,self.y+25,ELEMENTS[self.element]["color"],10 if self.avatar_state else 5)
    def special(self):
        if self.special_cd>0 or self.energy<25: return
        self.energy-=25; self.special_cd=55 if self.avatar_state else 90
        if self.avatar_state: self.avatar_special(); return
        if self.element=="fire": self.fire_special()
        elif self.element=="water": self.water_special()
        elif self.element=="earth": self.earth_special()
        else: self.air_special()
    def fire_special(self):
        for i in range(7):
            p=Projectile(self.x+20,self.y+25,self.facing,"fire",20,12); p.speed=9+i*.6; p.knockback=9; projectiles.append(p)
        burst(self.x+self.facing*40,self.y+25,FIRE,30,5)
    def water_special(self):
        self.health=min(100,self.health+20); ring(self.x+20,self.y+30,WATER_LIGHT,40,5)
    def earth_special(self):
        for _ in range(5):
            p=Projectile(self.x+20,self.y+35,self.facing,"earth",28,random.randint(13,20)); p.speed=7; p.knockback=12; projectiles.append(p)
        burst(self.x+self.facing*35,GROUND_Y,EARTH,30,5)
    def air_special(self):
        if self.grounded:
            for e in enemies:
                if (e.x-self.x)*self.facing>0 and abs(e.x-self.x)<320:
                    e.health-=18; e.x+=self.facing*120
            ring(self.x+20,self.y+30,AIR,45,7)
        else:
            self.vx=self.facing*18; self.vy=-5; burst(self.x+20,self.y+30,AIR_BLUE,30,4)
    def activate_avatar(self):
        if not self.avatar_state and self.avatar_meter>=100:
            self.cutscene=True; start_cinematic()
    def finish_avatar(self):
        self.cutscene=False; self.avatar_state=True; self.avatar_timer=900
        self.avatar_meter=100; self.energy=100; self.health=min(100,self.health+25)
        burst(self.x+20,self.y+30,WHITE,100,10); ring(self.x+20,self.y+30,AIR_BLUE,60,9)
    def exit_avatar(self):
        self.avatar_state=False; self.avatar_timer=0; burst(self.x+20,self.y+30,WHITE,25,5)
    def avatar_special(self):
        # Boosted element move
        if self.element=="fire":
            for i in range(5):
                p=Projectile(self.x+20,self.y+20+i*9,self.facing,"fire",48,22); p.speed=12; p.knockback=18; projectiles.append(p)
            burst(self.x+self.facing*50,self.y+25,FIRE,55,7)
        elif self.element=="water":
            self.health=min(100,self.health+30)
            for i in range(4):
                p=Projectile(self.x+20,self.y+15+i*12,self.facing,"water",42,20); p.speed=11; p.knockback=16; projectiles.append(p)
            burst(self.x+self.facing*50,self.y+25,WATER_LIGHT,55,7)
        elif self.element=="earth":
            for i in range(3):
                p=Projectile(self.x+20,self.y+20,self.facing,"earth",65,30); p.speed=7+i; p.knockback=22; projectiles.append(p)
            burst(self.x+self.facing*40,GROUND_Y,EARTH_LIGHT,70,8)
        else:
            # Tornado represented by huge, fast air projectiles + vortex particles
            for i in range(4):
                p=Projectile(self.x+20,self.y+20,self.facing,"air",40,24); p.speed=10+i; p.knockback=25; projectiles.append(p)
            ring(self.x+self.facing*80,self.y+20,AIR,80,8)
        self.lightning()
    def lightning(self):
        targets=[e for e in enemies if abs(e.x-self.x)<650 and (e.x-self.x)*self.facing>0]
        if targets:
            e=min(targets,key=lambda q:abs(q.x-self.x)); e.health-=75; e.x+=self.facing*25
            lightning.append(LightningBolt(e.x+20)); burst(e.x+20,e.y+25,LIGHTNING,35,7)
        else: lightning.append(LightningBolt(self.x+self.facing*300))
    def draw(self,cam):
        sx=int(self.x-cam); sy=int(self.y); color=ELEMENTS[self.element]["color"]
        if self.avatar_state:
            t=pygame.time.get_ticks()/90
            r=int(42+math.sin(t)*6)
            pygame.draw.circle(screen,AIR_BLUE,(sx+21,sy+30),r+12,3)
            pygame.draw.circle(screen,WHITE,(sx+21,sy+30),r+5,3)
            for i in range(4):
                a=t+i*math.pi/2
                pygame.draw.circle(screen,WHITE,(sx+21+int(math.cos(a)*42),sy+30+int(math.sin(a)*42)),5)
        pygame.draw.ellipse(screen,(10,10,10),(sx-5,GROUND_Y-7,52,11))
        pygame.draw.rect(screen,WHITE if self.avatar_state else (22,22,25),(sx,sy+20,42,40))
        pygame.draw.rect(screen,color,(sx,sy+34,42,7))
        pygame.draw.circle(screen,(210,155,110),(sx+21,sy+12),15)
        eye=WHITE if self.avatar_state else BLACK
        pygame.draw.rect(screen,eye,(sx+14,sy+10,4,4)); pygame.draw.rect(screen,eye,(sx+25,sy+10,4,4))
        if self.hit_flash: pygame.draw.circle(screen,RED,(sx+21,sy+30),35,3)

player=Player()

# Optional user-supplied MP4/MOV. We deliberately don't require a video
# dependency: the original in-game cinematic always works.
cinematic_timer=0
try:
    from ffpyplayer.player import MediaPlayer
    FFPY_AVAILABLE=True
except ImportError:
    FFPY_AVAILABLE=False
video_player=None
video_surface=None

def find_cutscene():
    base=Path(__file__).resolve().parent/"assets"
    for name in ("avatar_state.mp4","avatar_state.mov"):
        p=base/name
        if p.exists(): return p
    return None

def start_cinematic():
    global cinematic_timer,video_player,video_surface
    cinematic_timer=0; video_surface=None; video_player=None
    if FFPY_AVAILABLE:
        p=find_cutscene()
        if p:
            try: video_player=MediaPlayer(str(p))
            except Exception: video_player=None

def update_cinematic():
    global cinematic_timer,video_surface
    cinematic_timer+=1
    if video_player:
        frame,val=video_player.get_frame()
        if val=="eof":
            player.finish_avatar(); return
        if frame:
            img,_=frame
            w,h=img.get_size()
            video_surface=pygame.image.frombuffer(img.to_bytearray()[0],(w,h),"RGB").convert()
    elif cinematic_timer>=225:
        player.finish_avatar()

def draw_cinematic():
    if video_surface:
        screen.blit(pygame.transform.smoothscale(video_surface,(WIDTH,HEIGHT)),(0,0))
        return
    screen.fill((3,5,10))
    t=cinematic_timer
    if t<55:
        text=FONT_BIG.render("THE ELEMENTS AWAKEN",True,WHITE)
        screen.blit(text,(WIDTH//2-text.get_width()//2,120))
        pygame.draw.circle(screen,AIR_BLUE,(WIDTH//2,HEIGHT//2),min(250,20+t*4),4)
    elif t<110:
        y=HEIGHT//2+int(math.sin(t*.08)*8)
        pygame.draw.circle(screen,(210,155,110),(WIDTH//2,y-45),25)
        pygame.draw.rect(screen,WHITE,(WIDTH//2-32,y-20,64,85))
        for i,c in enumerate((FIRE,WATER,EARTH_LIGHT,AIR)):
            a=t*.06+i*math.pi/2
            pygame.draw.circle(screen,c,(WIDTH//2+int(math.cos(a)*110),y+int(math.sin(a)*110)),18)
    elif t<165:
        r=min(320,80+(t-110)*5)
        pygame.draw.circle(screen,WHITE,(WIDTH//2,HEIGHT//2),r,5)
        pygame.draw.circle(screen,AIR_BLUE,(WIDTH//2,HEIGHT//2),max(10,r-25),3)
    else:
        text=FONT_BIG.render("AVATAR STATE",True,WHITE)
        screen.blit(text,(WIDTH//2-text.get_width()//2,HEIGHT//2-35))
        sub=FONT_MED.render("THE FOUR ELEMENTS ANSWER THE CALL",True,AIR_BLUE)
        screen.blit(sub,(WIDTH//2-sub.get_width()//2,HEIGHT//2+35))

def hit(p,e):
    dx=p.x-(e.x+21); dy=p.y-(e.y+25)
    return dx*dx+dy*dy<(p.radius+25)**2

def update_camera():
    global camera_x
    camera_x+=(player.x-WIDTH*.42-camera_x)*.12
    camera_x=max(0,min(WORLD_WIDTH-WIDTH,camera_x))

def bar(x,y,w,h,value,color):
    pygame.draw.rect(screen,(20,20,20),(x,y,w,h))
    pygame.draw.rect(screen,color,(x,y,int(w*max(0,min(100,value))/100),h))
    pygame.draw.rect(screen,WHITE,(x,y,w,h),1)

def draw_hud():
    panel=pygame.Surface((370,235),pygame.SRCALPHA); panel.fill((5,7,10,220)); screen.blit(panel,(15,15))
    screen.blit(FONT_TITLE.render("ELEMENTAL LEGENDS",True,WHITE),(30,28))
    screen.blit(FONT_SMALL.render("HEALTH",True,WHITE),(30,70)); bar(95,71,235,14,player.health,RED)
    screen.blit(FONT_SMALL.render("ENERGY",True,WHITE),(30,98)); bar(95,99,235,14,player.energy,WATER)
    screen.blit(FONT_SMALL.render("AVATAR STATE",True,WHITE),(30,126)); bar(125,127,205,14,player.avatar_meter,AIR_BLUE)
    screen.blit(FONT_MED.render("ELEMENT: "+player.element.upper(),True,ELEMENTS[player.element]["color"]),(30,153))
    if player.avatar_state:
        screen.blit(FONT_MED.render(f"AVATAR STATE: {player.avatar_timer//FPS}s",True,WHITE),(30,181))
    screen.blit(FONT_SMALL.render(f"DEFEATED: {score}",True,WHITE),(30,208))
    if combo>1: screen.blit(FONT_MED.render(f"COMBO x{combo}",True,FIRE_LIGHT),(WIDTH-190,25))

def draw_controls():
    lines=["WASD / ARROWS  Move","SPACE  Jump","1 Fire  2 Water  3 Earth  4 Air","CLICK  Bend","E  Special","Q  Avatar State","R  Restart"]
    for i,line in enumerate(lines):
        screen.blit(FONT_SMALL.render(line,True,WHITE),(20,HEIGHT-140+i*18))

def restart():
    global score,combo,combo_timer,spawn_timer,camera_x,video_player
    player.x=450; player.y=GROUND_Y-60; player.vx=player.vy=0
    player.health=100; player.energy=100; player.avatar_meter=100
    player.avatar_state=False; player.avatar_timer=0; player.cutscene=False
    player.special_cd=player.attack_cd=0
    projectiles.clear(); enemies.clear(); particles.clear(); lightning.clear()
    score=combo=combo_timer=spawn_timer=camera_x=0
    if video_player:
        try: video_player.close_player()
        except Exception: pass
        video_player=None

def game_over():
    o=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); o.fill((0,0,0,185)); screen.blit(o,(0,0))
    t=FONT_BIG.render("YOU FELL",True,WHITE); screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-50))
    t=FONT_MED.render("Press R to restart",True,WHITE); screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2+20))

def main():
    global score,combo,combo_timer,spawn_timer
    running=True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_r: restart()
                if not player.cutscene and player.health>0:
                    if event.key==pygame.K_1: player.element="fire"
                    elif event.key==pygame.K_2: player.element="water"
                    elif event.key==pygame.K_3: player.element="earth"
                    elif event.key==pygame.K_4: player.element="air"
                    elif event.key==pygame.K_e: player.special()
                    elif event.key==pygame.K_q: player.activate_avatar()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and not player.cutscene and player.health>0:
                player.attack()

        if player.cutscene:
            update_cinematic(); draw_cinematic(); pygame.display.flip(); continue

        if player.health>0:
            keys=pygame.key.get_pressed(); player.update(keys); update_camera()
            spawn_timer+=1
            if spawn_timer>=100: spawn_enemy(); spawn_timer=0
            for e in enemies: e.update()
            for p in projectiles: p.update()
            for b in lightning: b.update()

            for p in projectiles:
                if p.dead(): continue
                for e in enemies:
                    if hit(p,e):
                        e.health-=p.damage
                        if p.element=="fire": e.ignite(4 if player.avatar_state else 3,210 if player.avatar_state else 180)
                        e.x+=p.direction*p.knockback
                        burst(e.x+20,e.y+25,p.color,15,4)
                        combo+=1; combo_timer=90; p.life=0
                        if e.health<=0:
                            score+=1; combo+=1; burst(e.x+20,e.y+25,p.color,35,7)
                        break

            projectiles[:]=[p for p in projectiles if not p.dead()]
            enemies[:]=[e for e in enemies if e.health>0]
            lightning[:]=[b for b in lightning if b.life>0]
            combo_timer=max(0,combo_timer-1)
            if combo_timer==0: combo=0

        for p in particles: p.update()
        particles[:]=[p for p in particles if p.life>0]

        view=pygame.Rect(int(camera_x),0,WIDTH,HEIGHT)
        screen.blit(background,(0,0),view)
        for p in projectiles: p.draw(camera_x)
        for e in enemies: e.draw(camera_x)
        player.draw(camera_x)
        for p in particles: p.draw(camera_x)
        for b in lightning: b.draw(camera_x)
        draw_hud(); draw_controls()
        if player.health<=0: game_over()
        pygame.display.flip()

    if video_player:
        try: video_player.close_player()
        except Exception: pass
    pygame.quit()

if __name__=="__main__":
    main()