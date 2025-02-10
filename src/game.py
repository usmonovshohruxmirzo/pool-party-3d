from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

Sky()

sunlight = DirectionalLight(shadows=True, color=color.white)

player = FirstPersonController()
player.speed = 5
player.x = 4
player.z = 12

ground = Entity(model="plane", scale=(200, 1, 200), color=color.gray, collider="mesh")

room = Entity(
    model="./assets/models/fnaf_sb_vip_party_room.glb",
    scale=1,
    position=(3, 0, -20),
    shader=lit_with_shadows_shader  
)

table_height = 1.2
pool_table = Entity(
    model="cube",
    scale=(6, 0.3, 3),
    color=color.gray,
    position=(0, table_height, 0),
    texture="./assets/textures/table.png",
    collider="box"
)

borders = [
    Entity(model="cube", scale=(6.5, 0.3, 0.3), position=(0, table_height + 0.15, -1.5), color=color.dark_gray, collider="box",   texture="./assets/textures/border.png",),
    Entity(model="cube", scale=(6.5, 0.3, 0.3), position=(0, table_height + 0.15, 1.5), color=color.dark_gray, collider="box",   texture="./assets/textures/border.png",),
    Entity(model="cube", scale=(0.3, 0.3, 3.3), position=(-3, table_height + 0.15, 0), color=color.dark_gray, collider="box",   texture="./assets/textures/border.png",),
    Entity(model="cube", scale=(0.3, 0.3, 3.3), position=(3, table_height + 0.15, 0), color=color.dark_gray, collider="box",   texture="./assets/textures/border.png",),
]

pocket_positions = [(-2.8, table_height + 0.1, -1.3), (2.8, table_height + 0.1, -1.3),
                    (-2.8, table_height + 0.1, 1.3), (2.8, table_height + 0.1, 1.3),
                    (0, table_height + 0.1, -1.4), (0, table_height + 0.1, 1.4)]
pockets = [Entity(model="sphere", scale=0.3, position=pos, color=color.black, collider="sphere") for pos in pocket_positions]

ball_positions = [
    (0, table_height + 0.25, 0),
    (1, table_height + 0.25, 0),
    (1.2, table_height + 0.25, -0.3), (1.2, table_height + 0.25, 0.3),
    (1.4, table_height + 0.25, -0.6), (1.4, table_height + 0.25, 0), (1.4, table_height + 0.25, 0.6),
    (1.6, table_height + 0.25, -0.9), (1.6, table_height + 0.25, -0.3), (1.6, table_height + 0.25, 0.3), (1.6, table_height + 0.25, 0.9),
    (1.8, table_height + 0.25, -1.2), (1.8, table_height + 0.25, -0.6), (1.8, table_height + 0.25, 0), (1.8, table_height + 0.25, 0.6), (1.8, table_height + 0.25, 1.2)
]

ball_colors = [
    color.white,
    color.red, color.red, color.red, color.red, color.red, color.red, color.red,
    color.red,
    color.red, color.red, color.red,
    color.red, color.red, color.red, color.red
]

balls = []
for i, pos in enumerate(ball_positions):
    ball = Entity(model="sphere", scale=0.2, position=pos, color=ball_colors[i], collider="sphere")
    ball.velocity = Vec3(0, 0, 0)
    balls.append(ball)

cue_ball = balls[0]

cue = Entity(
    model="./assets/models/cue.glb",
    scale=(0.5, 0.5, 0.5),
    position=(0, -0.2, 0.5),
    parent=camera,
    visible=False,
    rotation=(0,90,0)
)

power_bar = Entity(
    model="cube",
    scale=(1, 0.05, 0.1),
    color=color.red,
    position=(0.5, -0.4, 1.5),  
    parent=camera, 
    visible=False,
    rotation=(0,90,0)
)
power = 0
charging = False


def hit_cue_ball():
    global power
    direction = Vec3(player.forward.x, 0, player.forward.z).normalized()
    cue_ball.velocity = direction * power * 10
    power = 0
    power_bar.visible = False
    cue.visible = False

def input(key):
    global power, charging
    if key == "left mouse down":
        charging = True
        power = 0
        power_bar.visible = True
        cue.visible = True
    if key == "left mouse up":
        charging = False
        hit_cue_ball()

def update():
    global power, charging
    if charging:
        power += time.dt * 2
        power = min(power, 1)
        power_bar.scale_x = 0.2 + power
    
    for ball in balls:
        ball.position += ball.velocity * time.dt
        ball.velocity *= 0.98

        if ball.position.x <= -2.85 or ball.position.x >= 2.85:
            ball.velocity.x *= -1
            ball.position.x = max(min(ball.position.x, 2.84), -2.84)

        if ball.position.z <= -1.35 or ball.position.z >= 1.35:
            ball.velocity.z *= -1
            ball.position.z = max(min(ball.position.z, 1.34), -1.34)

        for other_ball in balls:
            if ball != other_ball and distance(ball.position, other_ball.position) < 0.3:
                direction = (ball.position - other_ball.position).normalized()
                ball.velocity += direction * 0.5
                other_ball.velocity -= direction * 0.5

        for pocket in pockets:
            if distance(ball.position, pocket.position) < 0.3:
                if ball == cue_ball:
                    ball.position = (0, table_height + 0.25, 0)
                    ball.velocity = Vec3(0, 0, 0)
                else:
                    ball.visible = False
                    ball.collider = None
                    ball.velocity = Vec3(0, 0, 0)

app.run()
