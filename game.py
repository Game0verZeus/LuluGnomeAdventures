import pygame
import sys
import random
import math
import os
import json

# --- Constantes globales ---
LARGEUR = 800
HAUTEUR = 400

VITESSE_OBSTACLE = 5
GRAVITE = 0.5
SAUT_FORCE = 10

best_score = 0
victory_messages = []  # On lira depuis un fichier externe

def load_victory_messages(filepath):
    """
    Tente de charger un tableau JSON du style ["msg1","msg2","msg3",...]
    en provenance du fichier `filepath`.
    S'il y a un problème, on renvoie 3 messages par défaut.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as e:
        print("Impossible de charger victory_messages depuis le fichier : ", e)
    return [
        "You did it, little Lulu! A polar secret awaits you...",
        "Victory is yours! Legends speak of a buried temple under the sea.",
        "Glorious triumph! A mysterious runic stone stands in Antarctica."
    ]

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def load_random_sounds(folder, exts=(".wav",".mp3")):
    """
    Charge tous les sons d’un dossier donné (extensions .wav, .mp3…).
    Retourne une liste de pygame.mixer.Sound.
    """
    res = []
    if not os.path.isdir(folder):
        return res
    for fn in os.listdir(folder):
        if fn.lower().endswith(exts):
            s = pygame.mixer.Sound(os.path.join(folder, fn))
            res.append(s)
    return res

def menu_initial(screen, clock, font_title, font_small):
    """
    Écran d’accueil
    """
    # Musique de menu
    menu_music_path = r"C:\Users\aunsu\Desktop\pythongame\sounds\start_menu.mp3"
    if os.path.isfile(menu_music_path):
        pygame.mixer.music.load(menu_music_path)
        pygame.mixer.music.play(-1)

    # Son “start game”
    start_game_sound_path = r"C:\Users\aunsu\Desktop\pythongame\sounds\Start_Game.mp3"
    start_game_sound = None
    if os.path.isfile(start_game_sound_path):
        start_game_sound = pygame.mixer.Sound(start_game_sound_path)

    try:
        bg_menu = pygame.image.load("Images/SS_Background.png").convert_alpha()
        bg_menu = pygame.transform.scale(bg_menu, (LARGEUR, HAUTEUR))
    except:
        bg_menu = None

    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))

    frame_count = 0
    running = True
    has_pressed = False  # Pour gérer le clic/espace

    while running:
        frame_count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Si le joueur appuie sur Espace ou clique
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if not has_pressed:
                    # On joue le son de start
                    if start_game_sound:
                        start_game_sound.play()
                    has_pressed = True
                    pressed_time = pygame.time.get_ticks()

        if bg_menu:
            screen.blit(bg_menu, (0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill((20, 20, 20))

        title_text = font_title.render("Lulu's Gnome Adventures", True, (255, 180, 0))
        title_rect = title_text.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 50))
        screen.blit(title_text, title_rect)

        # Affichage du texte “Press SPACE to Start”
        if not has_pressed:
            if (frame_count // 30) % 2 == 0:
                press_color = (200, 200, 200)
            else:
                press_color = (130, 130, 130)
            press_text = font_small.render("Press SPACE to Start", True, press_color)
            press_rect = press_text.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 20))
            screen.blit(press_text, press_rect)
        else:
            elapsed_since_press = pygame.time.get_ticks() - pressed_time
            if elapsed_since_press < 1000:
                # Clignotement rapide en blanc
                if (frame_count // 10) % 2 == 0:
                    press_text = font_small.render("Press SPACE to Start", True, (255, 255, 255))
                    press_rect = press_text.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 20))
                    screen.blit(press_text, press_rect)
            else:
                # Après 1 sec, on quitte le menu
                pygame.mixer.music.stop()
                return

        pygame.display.flip()
        clock.tick(60)

class BackgroundScroller:
    def __init__(self, image):
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x1 = 0
        self.x2 = self.width
        self.scroll_speed = VITESSE_OBSTACLE * 0.5

    def update(self):
        dx = self.scroll_speed
        self.x1 -= dx
        self.x2 -= dx
        if self.x1 <= -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 <= -self.width:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.image, (self.x1, 0))
        screen.blit(self.image, (self.x2, 0))

class GrassScroller:
    def __init__(self, image, sol_y):
        self.image_full = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.sol_y = sol_y

        self.cime_height = 30
        if self.cime_height > self.height:
            self.cime_height = self.height // 2

        self.image_bas = self.image_full.subsurface((0, 0, self.width, self.height - self.cime_height))
        self.image_cime = self.image_full.subsurface(
            (0, self.height - self.cime_height, self.width, self.cime_height)
        ).copy()

        cime_array = pygame.surfarray.pixels_alpha(self.image_cime)
        hc = self.image_cime.get_height()
        for y in range(hc):
            ratio = y / float(hc)
            alpha_val = int(255 * (0.7 + 0.3 * ratio))
            for x in range(self.image_cime.get_width()):
                current_alpha = cime_array[x, y]
                new_alpha = min(current_alpha, alpha_val)
                cime_array[x, y] = new_alpha
        del cime_array

        self.vertical_offset = 15
        self.image_cime.set_alpha(230)

        self.x1 = 0
        self.x2 = self.width
        self.scroll_speed = VITESSE_OBSTACLE
        self.wind_amplitude = 1

    def update(self):
        dx = self.scroll_speed
        self.x1 -= dx
        self.x2 -= dx
        if self.x1 <= -self.width:
            self.x1 = self.x2 + self.width
        if self.x2 <= -self.width:
            self.x2 = self.x1 + self.width

    def draw_bas(self, screen):
        t = pygame.time.get_ticks() / 1000.0
        offset = int(math.sin(t * 2.0) * self.wind_amplitude)
        base_y = self.sol_y - (self.height - self.cime_height) + self.vertical_offset
        screen.blit(self.image_bas, (self.x1, base_y + offset))
        screen.blit(self.image_bas, (self.x2, base_y + offset))

    def draw_cime(self, screen):
        t = pygame.time.get_ticks() / 1000.0
        offset = int(math.sin(t * 2.0) * self.wind_amplitude)
        base_y = self.sol_y - self.height + self.vertical_offset
        y_cime = base_y + offset + (self.height - self.cime_height)
        screen.blit(self.image_cime, (self.x1, y_cime))
        screen.blit(self.image_cime, (self.x2, y_cime))

class Projectile:
    def __init__(self, x, y, target_x, target_y, weapon_img, throw_sounds, touch_sounds, speed=5.0):
        self.image = weapon_img
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = pygame.Rect(x, y, 48, 48)
        self.rect.center = (x, y)

        self.throw_sounds = throw_sounds if throw_sounds else []
        self.touch_sounds = touch_sounds if touch_sounds else []
        self.has_exploded = False

        if self.throw_sounds:
            random.choice(self.throw_sounds).play()

        path_img = str(weapon_img).__str__().lower()
        self.is_poop = "poop" in path_img
        self.is_sock = "sock" in path_img

        dx = target_x - x
        dy = target_y - y

        if self.is_poop:
            speed *= 0.7
            dy -= 100
        elif self.is_sock:
            speed *= 1.2
            dy += 30

        length = math.hypot(dx, dy)
        if length == 0:
            length = 1

        self.vel_x = (dx / length) * speed
        self.vel_y = (dy / length) * speed

        if abs(self.vel_x) < 0.1:
            if dx < 0:
                self.vel_x = -2.0
            else:
                self.vel_x = 2.0

        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.is_poop:
            self.vel_y += 0.2
            if abs(self.vel_y) < 0.1:
                self.vel_y = 0.1

        if (self.rect.right < 0 or self.rect.left > LARGEUR
            or self.rect.top > HAUTEUR or self.rect.bottom < 0):
            self.has_exploded = True

    def check_collision(self, player, sol_y):
        if self.rect.colliderect(player.get_collision_rect()):
            if not player.is_hit:
                player.prendre_degats()
            self.play_impact_sound()
            self.has_exploded = True
        elif self.rect.bottom >= sol_y:
            self.play_impact_sound()
            self.has_exploded = True

    def play_impact_sound(self):
        if self.touch_sounds:
            random.choice(self.touch_sounds).play()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class HacheProjectile:
    def __init__(self, x, y, tx, ty, hammer_throw_sounds=None, enemy_touched_sound=None):
        self.hammer_throw_sounds = hammer_throw_sounds
        self.enemy_touched_sound = enemy_touched_sound

        try:
            hammer_img = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Images\hammer.png").convert_alpha()
            self.image = pygame.transform.scale(hammer_img, (32, 32))
        except:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((180,180,180,200))

        self.rect = pygame.Rect(x, y, 32, 32)
        self.rect.center = (x, y)
        self.has_exploded = False
        self.damage = 1

        dx = tx - x
        dy = ty - y
        speed = 8.0
        length = math.hypot(dx, dy)
        if length == 0:
            length = 1
        self.vel_x = (dx / length) * speed
        self.vel_y = (dy / length) * speed

        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)

        # On joue les sons de tir
        if self.hammer_throw_sounds and len(self.hammer_throw_sounds) >= 2:
            channel = pygame.mixer.Channel(7)
            channel.play(self.hammer_throw_sounds[0])
            channel.queue(self.hammer_throw_sounds[1])
        elif self.hammer_throw_sounds:
            self.hammer_throw_sounds[0].play()

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if (self.rect.right < 0 or self.rect.left > LARGEUR
            or self.rect.top > HAUTEUR or self.rect.bottom < 0):
            self.has_exploded = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def on_enemy_hit(self):
        if self.enemy_touched_sound:
            self.enemy_touched_sound.play()

class Joueur:
    def __init__(self, x, y, image_normal, hit_sounds, heart_img, jump_sounds, jump_effects):
        self.image_normal = image_normal
        self.image_hit = pygame.image.load("Characters/Gnome/hitted_gnome.png").convert_alpha()
        self.image_hit = pygame.transform.scale(self.image_hit, (64, 64))

        self.image = self.image_normal
        self.rect = self.image.get_rect(x=x, y=y - self.image.get_height())

        self.vx = 0
        self.speed_run = 4
        self.vy = 0
        self.lives = 3
        self.nb_sauts = 0
        self.can_throw_axes = False  # On aura le hammer bonus

        self.hit_sounds = hit_sounds
        self.jump_sounds = jump_sounds
        self.jump_effects = jump_effects

        self.heart_img_full = heart_img
        self.heart_img_lost = heart_img.copy()
        self.heart_img_lost.fill((100,100,100,100), special_flags=pygame.BLEND_RGBA_MULT)

        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 30

    def handle_keydown(self, key):
        if key == pygame.K_LEFT:
            self.vx = -self.speed_run
        elif key == pygame.K_RIGHT:
            self.vx = self.speed_run
        elif key == pygame.K_SPACE:
            self.sauter()
        elif key == pygame.K_e:
            # On ne crée pas la hache ici directement;
            # on laisse la boucle d'événement dans jeu() décider.
            pass

    def handle_keyup(self, key):
        if key == pygame.K_LEFT and self.vx < 0:
            self.vx = 0
        elif key == pygame.K_RIGHT and self.vx > 0:
            self.vx = 0

    def sauter(self):
        if self.nb_sauts < 3:
            self.vy = -SAUT_FORCE
            self.nb_sauts += 1
            if self.jump_sounds:
                random.choice(self.jump_sounds).play()
            if self.jump_effects and random.random() < 0.5:
                random.choice(self.jump_effects).play()

    def appliquer_gravite(self, sol_y):
        self.vy += GRAVITE
        self.rect.y += self.vy
        self.rect.x += self.vx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGEUR:
            self.rect.right = LARGEUR
        if self.rect.top < 0:
            self.rect.top = 0
            self.vy = 0
        if self.rect.bottom > sol_y:
            self.rect.bottom = sol_y
            self.vy = 0
            self.nb_sauts = 0

        if self.is_hit:
            self.hit_timer += 1
            if self.hit_timer > self.hit_duration:
                self.is_hit = False
                self.hit_timer = 0
                self.image = self.image_normal

    def prendre_degats(self):
        self.lives -= 1
        if self.hit_sounds:
            random.choice(self.hit_sounds).play()
        self.is_hit = True
        self.hit_timer = 0
        self.image = self.image_hit

    def dessiner(self, screen):
        if self.is_hit:
            if (self.hit_timer // 5) % 2 == 0:
                return
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def get_collision_rect(self):
        c = self.rect.copy()
        c.width = int(c.width * 0.5)
        c.height = int(c.height * 0.7)
        c.center = self.rect.center
        return c

    def dessiner_coeurs(self, screen):
        x_heart = 10
        y_heart = 50
        spacing = self.heart_img_full.get_width() + 5
        for i in range(3):
            if i < self.lives:
                screen.blit(self.heart_img_full, (x_heart + i * spacing, y_heart))
            else:
                screen.blit(self.heart_img_lost, (x_heart + i * spacing, y_heart))

class Obstacle:
    def __init__(self, x, sol_y, image_shroom, image_bird, obstacle_type="shroom"):
        self.is_bird = (obstacle_type == "bird")
        self.hp = 1
        self.is_dead = False
        self.dead_timer = 0
        self.dead_blink_duration = 15

        if self.is_bird:
            self.image = image_bird
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.y_base = random.randint(50, sol_y - 150)
            self.rect.y = self.y_base
            self.bird_time = 0
            self.bird_speed = 0.08
            self.bird_amplitude = 40
        else:
            self.image = image_shroom
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = sol_y

    def get_rect(self):
        return self.rect

    def dessiner(self, screen):
        if self.is_dead:
            if (self.dead_timer // 3) % 2 == 0:
                return
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def mise_a_jour(self):
        if self.is_dead:
            self.dead_timer += 1
            return
        self.rect.x -= VITESSE_OBSTACLE
        if self.is_bird:
            self.bird_time += 1
            offset = int(math.sin(self.bird_time * self.bird_speed) * self.bird_amplitude)
            self.rect.y = self.y_base + offset

    def take_damage(self, dmg, enemy_touched_sound=None):
        if self.is_dead:
            return
        self.hp -= dmg
        if enemy_touched_sound:
            enemy_touched_sound.play()
        if self.hp <= 0:
            self.is_dead = True

class BadLu:
    def __init__(self, sol_y):
        self.hp = 2
        self.is_dead = False
        self.dead_timer = 0
        self.dead_blink_duration = 25

        try:
            self.image = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Characters\Bad_Lu\bad_lu.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (64,64))

            self.sock_img = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Characters\Bad_Lu\Weapons\sock.png").convert_alpha()
            self.sock_img = pygame.transform.scale(self.sock_img, (48,48))

            self.sock_img_mirror = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Characters\Bad_Lu\Weapons\sock_mirror.png").convert_alpha()
            self.sock_img_mirror = pygame.transform.scale(self.sock_img_mirror, (48,48))

            self.poop_img = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Characters\Bad_Lu\Weapons\poop.png").convert_alpha()
            self.poop_img = pygame.transform.scale(self.poop_img, (48,48))

            self.poop_img_mirror = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Characters\Bad_Lu\Weapons\poop_mirror.png").convert_alpha()
            self.poop_img_mirror = pygame.transform.scale(self.poop_img_mirror, (48,48))
        except:
            print("Error loading images for BadLu")
            self.image = pygame.Surface((64,64), pygame.SRCALPHA)
            self.image.fill((255,0,0,200))

            self.sock_img = pygame.Surface((48,48), pygame.SRCALPHA)
            self.sock_img.fill((0,255,0,200))
            self.sock_img_mirror = pygame.Surface((48,48), pygame.SRCALPHA)
            self.sock_img_mirror.fill((0,255,0,120))

            self.poop_img = pygame.Surface((48,48), pygame.SRCALPHA)
            self.poop_img.fill((0,0,255,200))
            self.poop_img_mirror = pygame.Surface((48,48), pygame.SRCALPHA)
            self.poop_img_mirror.fill((0,0,255,120))

        self.rect = self.image.get_rect()
        self.rect.x = LARGEUR + 50
        self.rect.y = random.randint(50, 200)

        self.bird_time = 0
        self.fly_amplitude = 60
        self.fly_speed = 0.07

        self.shot_timer = 0.0
        self.shot_cooldown = random.uniform(2,4)

        self.laugh_sounds = load_random_sounds("Characters/Bad_Lu/laugh", (".wav",))
        self.throw_sounds = load_random_sounds("Characters/Bad_Lu/Weapons_Sound/Throwing_All", (".mp3", ".wav"))
        self.touch_sounds = load_random_sounds("Characters/Bad_Lu/Weapons_Sound/Touch_Target", (".mp3", ".wav"))

        self.speed_x = 2
        self.projectiles = []
        self.active = True
        self.sol_y = sol_y

        self.x_origin = self.rect.x
        self.y_origin = self.rect.y

    def update(self, dt, player):
        if not self.active:
            return

        if self.is_dead:
            self.dead_timer += 1
            if self.dead_timer > self.dead_blink_duration:
                self.active = False
                print("BadLu deactivated (killed by hache).")
            return

        self.bird_time += dt
        offset_x = int(30*math.sin(self.bird_time*2))
        offset_y = int(self.fly_amplitude*math.sin(self.bird_time*self.fly_speed))

        self.rect.x = self.x_origin - int(self.speed_x*(self.bird_time*60)) + offset_x
        self.rect.y = self.y_origin + offset_y

        self.shot_timer += dt
        if self.shot_timer >= self.shot_cooldown:
            self.shoot(player)
            self.shot_timer = 0.0
            self.shot_cooldown = random.uniform(2,4)

        for p in self.projectiles:
            p.update()
            p.check_collision(player, self.sol_y)
        self.projectiles = [pp for pp in self.projectiles if not pp.has_exploded]

        if self.rect.right < 0:
            self.active = False
            print("BadLu deactivated (out of screen).")

    def shoot(self, player):
        if self.laugh_sounds:
            random.choice(self.laugh_sounds).play()

        x0 = self.rect.centerx
        y0 = self.rect.centery
        px = player.rect.centerx
        py = player.rect.centery

        if self.rect.centerx < px:
            py -= 50
            direction = "left"
        else:
            direction = "right"

        chosen_weapon = random.choice(["sock", "poop"])
        if chosen_weapon == "sock":
            if direction == "left":
                weapon_img = self.sock_img
            else:
                weapon_img = self.sock_img_mirror
        else:
            if direction == "left":
                weapon_img = self.poop_img
            else:
                weapon_img = self.poop_img_mirror

        print(f"Shooting {chosen_weapon} ({direction}) from ({x0},{y0}) to ({px},{py})")
        new_proj = Projectile(x0, y0, px, py, weapon_img, self.throw_sounds, self.touch_sounds, speed=5.0)
        self.projectiles.append(new_proj)

    def draw(self, screen):
        if not self.active:
            return
        if self.is_dead:
            if (self.dead_timer // 3) % 2 == 0:
                return
        screen.blit(self.image, self.rect)
        for p in self.projectiles:
            p.draw(screen)

    def take_damage(self, dmg, enemy_touched_sound=None):
        if self.is_dead:
            return
        self.hp -= dmg
        if enemy_touched_sound:
            enemy_touched_sound.play()
        if self.hp <= 0:
            self.is_dead = True
            self.dead_timer = 0
            print("BadLu is killed by hache.")

class HeartBonus:
    def __init__(self):
        self.image = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Texture\Score_Heart\06.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(32,32))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, LARGEUR-100)
        self.rect.y = random.randint(50, HAUTEUR-100)

        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-2,2)

        self.change_dir_timer=0.0
        self.change_dir_cooldown=random.uniform(1.0,3.0)
        self.collected=False
        self.collect_blink_timer=0
        self.collect_blink_duration=20

        self.sound_path=r"C:\Users\aunsu\Desktop\pythongame\sounds\Plus_Life\extra_life.wav"
        if os.path.isfile(self.sound_path):
            self.sound_extra_life=pygame.mixer.Sound(self.sound_path)
        else:
            self.sound_extra_life=None

    def update(self, dt):
        if self.collected:
            self.collect_blink_timer+=1
            if self.collect_blink_timer> self.collect_blink_duration:
                self.rect.y=999999
            return

        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.left<0 or self.rect.right> LARGEUR:
            self.vx=-self.vx
        if self.rect.top<0 or self.rect.bottom> HAUTEUR:
            self.vy=-self.vy

        self.change_dir_timer+=dt
        if self.change_dir_timer>=self.change_dir_cooldown:
            self.vx=random.uniform(-2,2)
            self.vy=random.uniform(-2,2)
            self.change_dir_timer=0.0
            self.change_dir_cooldown=random.uniform(1.0,3.0)

    def check_collision(self, player):
        if self.collected:
            return
        if self.rect.colliderect(player.get_collision_rect()):
            if player.lives<3:
                player.lives+=1
                if self.sound_extra_life:
                    self.sound_extra_life.play()
            self.collected=True
            self.collect_blink_timer=0

    def draw(self, screen):
        if self.collected:
            if (self.collect_blink_timer//3)%2==0:
                return
        screen.blit(self.image, self.rect)

class HammerBonus:
    def __init__(self):
        try:
            self.image = pygame.image.load(r"C:\Users\aunsu\Desktop\pythongame\Images\hammer.png").convert_alpha()
            self.image = pygame.transform.scale(self.image,(32,32))
        except:
            self.image=pygame.Surface((32,32), pygame.SRCALPHA)
            self.image.fill((200,180,0,180))

        self.rect=self.image.get_rect()
        self.rect.x=random.randint(100,LARGEUR-100)
        self.rect.y=random.randint(50,HAUTEUR-100)
        self.collected=False
        self.collect_blink_timer=0
        self.collect_blink_duration=20

        self.vx=random.uniform(-3,3)
        self.vy=random.uniform(-3,3)

        self.change_dir_timer=0
        self.change_dir_cooldown=1.0

        # Musique d'obtention
        self.hammer_obtention_music_path = r"C:\Users\aunsu\Desktop\pythongame\sounds\Tool_Obtention\Win_Music\obtention.wav"
        self.hammer_obtention_music = None
        if os.path.isfile(self.hammer_obtention_music_path):
            self.hammer_obtention_music = pygame.mixer.Sound(self.hammer_obtention_music_path)

    def update(self, dt, player):
        if self.collected:
            self.collect_blink_timer+=1
            if self.collect_blink_timer> self.collect_blink_duration:
                self.rect.y=999999
            return

        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        dist=math.hypot(dx,dy)
        if dist<50:
            if dist!=0:
                self.vx=(dx/dist)*1
                self.vy=(dy/dist)*1
        else:
            self.change_dir_timer+=dt
            if self.change_dir_timer>=self.change_dir_cooldown:
                self.vx=random.uniform(-3,3)
                self.vy=random.uniform(-3,3)
                self.change_dir_timer=0
                self.change_dir_cooldown=random.uniform(1,3)

        self.rect.x+=self.vx
        self.rect.y+=self.vy

        if self.rect.left<0 or self.rect.right> LARGEUR:
            self.vx=-self.vx
        if self.rect.top<0 or self.rect.bottom>HAUTEUR:
            self.vy=-self.vy

    def check_collision(self, player):
        if self.collected:
            return
        if self.rect.colliderect(player.get_collision_rect()):
            player.can_throw_axes=True
            self.collected=True
            self.collect_blink_timer=0
            if self.hammer_obtention_music:
                self.hammer_obtention_music.play()

    def draw(self, screen):
        if self.collected:
            if (self.collect_blink_timer//3)%2==0:
                return
        screen.blit(self.image,self.rect)

def show_hammer_obtention_screen(screen, clock, font_text, hammer_obtention_voice):
    # On pause la musique
    pygame.mixer.music.pause()

    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))

    message = [
        "You have just obtained Lulu's Ax!",
        "Press [E] on the ground to attack Shrooms,",
        "and Press [E] while jumping to attack Birds or BadLu!"
    ]
    if hammer_obtention_voice:
        hammer_obtention_voice.play()

    block_start_time = pygame.time.get_ticks()
    block_duration = 3000  # 3 secondes
    blocked = True

    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not blocked:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    # On unpause la musique
                    pygame.mixer.music.unpause()
                    return

        if blocked:
            if current_time - block_start_time >= block_duration:
                blocked = False

        screen.blit(overlay, (0, 0))

        y_offset = 80
        for line in message:
            surf = font_text.render(line, True, (255, 255, 0))
            rect = surf.get_rect(center=(LARGEUR // 2, y_offset))
            screen.blit(surf, rect)
            y_offset += 40

        if not blocked:
            hint = "Press any key or click to continue..."
            hint_surf = font_text.render(hint, True, (255,255,255))
            hint_rect = hint_surf.get_rect(center=(LARGEUR//2, y_offset+30))
            screen.blit(hint_surf, hint_rect)

        pygame.display.flip()
        clock.tick(60)

def jeu(screen, clock, font_title, font_score, font_text):
    global best_score
    global victory_messages

    # Musique de fond
    if os.path.isfile("sounds/main.mp3"):
        pygame.mixer.music.load("sounds/main.mp3")
        pygame.mixer.music.play(-1)

    # Sons gameover
    gameover_sounds = load_random_sounds("sounds/GameOver", (".wav",".mp3"))

    # Voix "Cartoon Old Man Voice Pack 2.wav"
    hammer_obtention_voice_path = r"C:\Users\aunsu\Desktop\pythongame\sounds\Tool_Obtention\Cartoon Old Man Voice Pack 2.wav"
    hammer_obtention_voice = None
    if os.path.isfile(hammer_obtention_voice_path):
        hammer_obtention_voice = pygame.mixer.Sound(hammer_obtention_voice_path)

    # Sons de tir du marteau
    hammer_throw_sounds = []
    path_throwA = r"C:\Users\aunsu\Desktop\pythongame\sounds\Throwing_Hammer,Throwing_A.wav"
    path_throwA2 = r"C:\Users\aunsu\Desktop\pythongame\sounds\Throwing_Hammer,Throwing_A2.wav"
    if os.path.isfile(path_throwA) and os.path.isfile(path_throwA2):
        hammer_throw_sounds = [
            pygame.mixer.Sound(path_throwA),
            pygame.mixer.Sound(path_throwA2)
        ]

    # Son ennemis touchés
    enemy_touched_sound_path = r"C:\Users\aunsu\Desktop\pythongame\sounds\Ennemies_Touched\Plop.wav"
    enemy_touched_sound = None
    if os.path.isfile(enemy_touched_sound_path):
        enemy_touched_sound = pygame.mixer.Sound(enemy_touched_sound_path)

    sol_y = HAUTEUR

    bg_img = pygame.image.load("Texture/Background/background1.png").convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (LARGEUR, HAUTEUR))
    background_scroller = BackgroundScroller(bg_img)

    grass_img = pygame.image.load("Texture/Floor/grass.png").convert_alpha()
    grass_img = pygame.transform.scale(grass_img, (800, 130))
    grass_scroller = GrassScroller(grass_img, sol_y)

    gnome_img = pygame.image.load("Characters/Gnome/gnome.png").convert_alpha()
    gnome_img = pygame.transform.scale(gnome_img, (64, 64))

    heart_img = pygame.image.load("Texture/Score_Heart/04.png").convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (24,24))

    hit_sounds = load_random_sounds("sounds/Hit", (".wav",))
    jump_sounds = load_random_sounds("sounds/Jumps", (".wav",))
    jump_effects = load_random_sounds("sounds/Jumps/Jump_Effect", (".wav",".mp3"))

    joueur = Joueur(50, sol_y, gnome_img, hit_sounds, heart_img, jump_sounds, jump_effects)

    shroom_img = pygame.image.load("Characters/Shroom/shroom.png").convert_alpha()
    shroom_img = pygame.transform.scale(shroom_img, (64, 64))

    bird_img = pygame.image.load("Characters/Bird/bird.png").convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (64, 64))

    obstacles = []
    bad_lu = None
    bad_lu_spawned = False

    hearts_bonus = []
    hammer_bonus = []
    next_heart_time = 0
    next_hammer_time = 0
    hammer_obtention_screen_shown = False

    # Liste locale de haches
    haches = []

    start_time = pygame.time.get_ticks()
    score = 0
    game_over = False
    new_record = False
    victory_message = ""
    frame_count = 0
    next_obstacle_time = 0

    # Pour augmenter le nombre d’ennemis au fil du temps
    # Toutes les 20s, on monte d'un niveau => plus d'ennemis
    spawn_level = 0

    def spawn_mushrooms(level=0):
        # level=0 => 1-3
        # level=1 => 2-4
        # level=2 => 3-5
        # etc.
        base_min = 1 + level
        base_max = 3 + level
        c = random.randint(base_min, base_max)
        for i in range(c):
            x_offset = i*80
            obs = Obstacle(LARGEUR + x_offset, sol_y, shroom_img, bird_img, "shroom")
            obstacles.append(obs)

    def spawn_birds(level=0):
        base_min = 2 + level
        base_max = 4 + level
        c = random.randint(base_min, base_max)
        for i in range(c):
            x_offset = i*60
            obs = Obstacle(LARGEUR + x_offset, sol_y, shroom_img, bird_img, "bird")
            obstacles.append(obs)

    def spawn_mix(level=0):
        base_min = 2 + level
        base_max = 4 + level
        c = random.randint(base_min, base_max)
        for i in range(c):
            x_offset = i*60
            if random.random()<0.5:
                obs_type = "shroom"
            else:
                obs_type = "bird"
            obs = Obstacle(LARGEUR + x_offset, sol_y, shroom_img, bird_img, obs_type)
            obstacles.append(obs)

    while True:
        dt = clock.tick(60)/1000.0
        frame_count += 1
        current_time = pygame.time.get_ticks()
        elapsed_sec = (current_time - start_time)//1000

        # On calcule un nouveau spawn_level
        new_level = elapsed_sec // 20  # change tous les 20s
        if new_level > spawn_level:
            spawn_level = new_level
            print(f"[DEBUG] spawn_level = {spawn_level}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if not game_over:
                if event.type == pygame.KEYDOWN:
                    joueur.handle_keydown(event.key)

                    # Touche E => on tente de tirer une hache
                    if event.key == pygame.K_e:
                        # Debug
                        print("[DEBUG] E pressed. can_throw_axes=", joueur.can_throw_axes,
                              " nb_sauts=", joueur.nb_sauts)
                        if joueur.can_throw_axes:
                            hx = joueur.rect.centerx
                            hy = joueur.rect.centery

                            if joueur.nb_sauts == 0:
                                # on vise un champignon
                                possibles = [o for o in obstacles
                                             if (not o.is_dead)
                                             and (not o.is_bird)
                                             and (o.rect.x > joueur.rect.x)]
                                if possibles:
                                    # On prend le plus proche
                                    target = min(possibles, key=lambda ob: abs(ob.rect.centerx - hx))
                                    print("[DEBUG] Found ground target -> Throwing hache")
                                    h = HacheProjectile(hx, hy, target.rect.centerx, target.rect.centery,
                                                        hammer_throw_sounds, enemy_touched_sound)
                                    haches.append(h)
                                else:
                                    print("[DEBUG] No ground target -> no throw")
                            else:
                                # on vise oiseaux ou BadLu
                                air_targets = []
                                for o in obstacles:
                                    if o.is_bird and not o.is_dead and o.rect.x>joueur.rect.x:
                                        air_targets.append(o)
                                if bad_lu and bad_lu.active and not bad_lu.is_dead and bad_lu.rect.centerx>joueur.rect.centerx:
                                    air_targets.append(bad_lu)

                                if air_targets:
                                    target = min(air_targets,
                                                 key=lambda a: (a.rect.centerx - hx)**2 + (a.rect.centery - hy)**2)
                                    print("[DEBUG] Found air target -> Throwing hache")
                                    if isinstance(target, Obstacle):
                                        h = HacheProjectile(hx, hy, target.rect.centerx, target.rect.centery,
                                                            hammer_throw_sounds, enemy_touched_sound)
                                    else:
                                        # c'est un BadLu
                                        h = HacheProjectile(hx, hy, target.rect.centerx, target.rect.centery,
                                                            hammer_throw_sounds, enemy_touched_sound)
                                    haches.append(h)
                                else:
                                    print("[DEBUG] No air target -> no throw")

                elif event.type==pygame.KEYUP:
                    joueur.handle_keyup(event.key)
            else:
                # Si game_over, on attend un clic/touche pour quitter
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

        if not game_over:
            background_scroller.update()
            grass_scroller.update()

            joueur.appliquer_gravite(sol_y)

            if current_time>=next_obstacle_time:
                # On spawn en fonction du temps + spawn_level
                if elapsed_sec<15:
                    spawn_mushrooms(spawn_level)
                elif elapsed_sec<30:
                    spawn_mix(spawn_level)
                else:
                    spawn_birds(spawn_level)
                next_obstacle_time=current_time+random.randint(1000,2000)

            for o in obstacles:
                o.mise_a_jour()
            obstacles = [
                oo for oo in obstacles
                if ((not oo.is_dead) or (oo.is_dead and oo.dead_timer < oo.dead_blink_duration))
                and (oo.get_rect().right > 0)
            ]
            for o in obstacles:
                if (not o.is_dead) and o.get_rect().colliderect(joueur.get_collision_rect()):
                    if not joueur.is_hit:
                        joueur.prendre_degats()
                    if joueur.lives<=0:
                        game_over=True
                        pygame.mixer.music.stop()
                        if gameover_sounds:
                            random.choice(gameover_sounds).play()
                        if score>best_score:
                            best_score=score
                            new_record=True
                            victory_message=random.choice(victory_messages)
                        break

            if elapsed_sec>=15 and not bad_lu_spawned:
                bad_lu=BadLu(sol_y)
                bad_lu_spawned=True

            if bad_lu and bad_lu.active:
                bad_lu.update(dt, joueur)

            if elapsed_sec>=10 and current_time>=next_heart_time:
                hb=HeartBonus()
                hearts_bonus.append(hb)
                next_heart_time=current_time+random.randint(10000,20000)

            if elapsed_sec>=12 and not joueur.can_throw_axes and current_time>=next_hammer_time:
                hm=HammerBonus()
                hammer_bonus.append(hm)
                next_hammer_time=current_time+random.randint(10000,25000)

            for hb in hearts_bonus:
                hb.update(dt)
                hb.check_collision(joueur)
            hearts_bonus=[hbb for hbb in hearts_bonus if hbb.rect.y<999999]

            for hm in hammer_bonus:
                hm.update(dt,joueur)
                hm.check_collision(joueur)
                if hm.collected and not hammer_obtention_screen_shown:
                    hammer_obtention_screen_shown = True
                    show_hammer_obtention_screen(screen, clock, font_text, hammer_obtention_voice)
            hammer_bonus=[hmm for hmm in hammer_bonus if hmm.rect.y<999999]

            # Mise à jour des haches
            to_remove=[]
            for hx_obj in haches:
                hx_obj.update()
                if hx_obj.has_exploded:
                    to_remove.append(hx_obj)
                else:
                    # Collision hache / obstacles
                    for o in obstacles:
                        if (not o.is_dead) and hx_obj.rect.colliderect(o.get_rect()):
                            o.take_damage(hx_obj.damage, enemy_touched_sound)
                            hx_obj.on_enemy_hit()
                            hx_obj.has_exploded=True
                            to_remove.append(hx_obj)
                            break
                    # Collision hache / badLu
                    if bad_lu and bad_lu.active and not bad_lu.is_dead:
                        if hx_obj.rect.colliderect(bad_lu.rect):
                            bad_lu.take_damage(hx_obj.damage, enemy_touched_sound)
                            hx_obj.on_enemy_hit()
                            hx_obj.has_exploded=True
                            to_remove.append(hx_obj)

            haches = [hh for hh in haches if hh not in to_remove]

            if bad_lu and (not bad_lu.active or (bad_lu.is_dead and bad_lu.dead_timer>bad_lu.dead_blink_duration)):
                bad_lu=None

            if joueur.lives<=0 and not game_over:
                game_over=True
                pygame.mixer.music.stop()
                if gameover_sounds:
                    random.choice(gameover_sounds).play()
                if score>best_score:
                    best_score=score
                    new_record=True
                    victory_message=random.choice(victory_messages)

            if not game_over:
                score+=1

        # Rendu
        background_scroller.draw(screen)
        grass_scroller.draw_bas(screen)

        for o in obstacles:
            o.dessiner(screen)

        joueur.dessiner(screen)

        grass_scroller.draw_cime(screen)

        if bad_lu and bad_lu.active:
            bad_lu.draw(screen)

        for hb in hearts_bonus:
            hb.draw(screen)

        for hm in hammer_bonus:
            hm.draw(screen)

        for hx_obj in haches:
            hx_obj.draw(screen)

        score_surf=font_score.render(f"Score: {score}", True, (0,0,0))
        screen.blit(score_surf, (10,10))
        joueur.dessiner_coeurs(screen)

        if game_over:
            over_surf=font_title.render("GAME OVER", True, (255,0,0))
            over_rect=over_surf.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 60))
            screen.blit(over_surf, over_rect)

            if new_record:
                lines=wrap_text(victory_message, font_text, 500)
                lh=font_text.get_linesize()
                total_h=len(lines)*lh+10
                top_y=(HAUTEUR//2)-(total_h//2)+10
                widest=max(lines, key=lambda l: font_text.size(l)[0]) if lines else ""
                w_line=font_text.size(widest)[0] if widest else 100
                pad=10
                box_w=w_line+pad*2
                box_h=total_h+pad*2
                box_x=(LARGEUR-box_w)//2
                box_y=top_y-pad
                s=pygame.Surface((box_w,box_h), pygame.SRCALPHA)
                s.fill((0,0,0,120))
                screen.blit(s,(box_x,box_y))

                y_pos=top_y
                for line in lines:
                    surf_line=font_text.render(line, True, (0,255,0))
                    line_rect=surf_line.get_rect(center=(LARGEUR//2, y_pos))
                    screen.blit(surf_line,line_rect)
                    y_pos+=lh
            else:
                best_surf=font_text.render(f"Best score: {best_score}", True, (255,255,255))
                best_rect=best_surf.get_rect(center=(LARGEUR//2,HAUTEUR//2))
                pad=10
                bw=best_rect.width+pad*2
                bh=best_rect.height+pad*2
                box_x=best_rect.x - pad
                box_y=best_rect.y - pad
                s=pygame.Surface((bw,bh), pygame.SRCALPHA)
                s.fill((0,0,0,120))
                screen.blit(s,(box_x,box_y))
                screen.blit(best_surf,best_rect)

            if (frame_count//15)%2==0:
                blink_color=(0,0,0)
            else:
                blink_color=(255,0,0)

            restart_surf=font_text.render("Click or Key to Restart", True, blink_color)
            restart_rect=restart_surf.get_rect(center=(LARGEUR//2, HAUTEUR//2+100))
            screen.blit(restart_surf, restart_rect)

        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Lulu’s Gnome Adventures")

    clock = pygame.time.Clock()

    global victory_messages
    victory_messages = load_victory_messages(
        r"C:\Users\aunsu\Desktop\pythongame\victory_messages.txt"
    )

    try:
        font_title = pygame.font.Font("Fonts/SuperPixel-m2L8j.ttf", 40)
        font_score = pygame.font.Font("Fonts/PixeloidSansBold-PkNyd.ttf", 24)
        font_text  = pygame.font.Font("Fonts/PixeloidMono-d94EV.ttf", 20)
    except:
        font_title = pygame.font.SysFont("arial", 40, bold=True)
        font_score = pygame.font.SysFont("arial", 24)
        font_text  = pygame.font.SysFont("arial", 20, italic=True)

    menu_initial(screen, clock, font_title, font_text)

    while True:
        jeu(screen, clock, font_title, font_score, font_text)

if __name__=="__main__":
    main()
