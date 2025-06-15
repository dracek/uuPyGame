"""NPC module"""
import math
import pygame


from config import NPC_SPEED


class NPC:
   """NPC common class"""


   TYPES = {
       "easy": {"health": 50, "damage": 5, "color": (100, 255, 100), "score": 10},
       "medium": {"health": 100, "damage": 10, "color": (255, 255, 0), "score": 25},
       "hard": {"health": 150, "damage": 20, "color": (255, 100, 100), "score": 50},
   }


   def __init__(self, x, y,npc_type="medium"):
       self.rect = pygame.Rect(x, y, 20, 20)


       self.type = npc_type
       npc_config = self.TYPES[self.type]
       self.score = npc_config["score"]
       self.health = npc_config["health"]
       self.max_health = npc_config["health"]
       self.damage = npc_config["damage"]
       self.color = npc_config["color"]




   def update(self, **kwargs):
       """Updates self position according to players"""
       nearest_player = self.find_closest_player(self, kwargs["players"].values())




       if self.rect.x < nearest_player.rect.x:
           self.rect.x += NPC_SPEED
       elif self.rect.x > nearest_player.rect.x:
           self.rect.x -= NPC_SPEED
       if self.rect.y < nearest_player.rect.y:
           self.rect.y += NPC_SPEED
       elif self.rect.y > nearest_player.rect.y:
           self.rect.y -= NPC_SPEED


   def get_shot_target(self, players):
       return self.find_closest_player(self, players)


   def draw_lifebar(self, screen):
       bar_width = self.rect.width
       bar_heigth = 5
       fill = (self.health / self.max_health) * bar_width


       pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_heigth))
       pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 10, fill, bar_heigth))




   def draw(self, screen):
       """Draws itself"""
       pygame.draw.rect(screen, (255, 0, 0), self.rect)
       self.draw_lifebar(screen)




   def distance(self, rect1, rect2):
       """Helper function for distance computing"""
       return math.hypot(rect1.x - rect2.x, rect1.y - rect2.y)


   def find_closest_player(self, npc, players):
       """Function for NPC to find which player to chase, not optimized"""
       closest = None
       min_dist = float('inf')


       for player in players:
           dist = self.distance(npc.rect, player.rect)
           if dist < min_dist:
               min_dist = dist
               closest = player


       return closest

