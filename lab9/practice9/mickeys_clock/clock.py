import pygame
import datetime

class MickeyClock:
    def __init__(self, screen, body_img, right_img, left_img, center):
        self.screen = screen
        self.body = pygame.image.load(body_img).convert_alpha()
        self.right_hand = pygame.image.load(right_img).convert_alpha()
        self.left_hand = pygame.image.load(left_img).convert_alpha()
        self.center = center

    def draw(self):
        # текущее время
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        # углы
        angle_min = -6 * minutes
        angle_sec = -6 * seconds

        # вращаем руки
        hand_min = pygame.transform.rotate(self.right_hand, angle_min)
        hand_sec = pygame.transform.rotate(self.left_hand, angle_sec)

        # очищаем экран
        self.screen.fill((4, 34, 63))

        # тело
        rect_body = self.body.get_rect(center=self.center)
        self.screen.blit(self.body, rect_body)

        # руки
        rect_min = hand_min.get_rect(center=self.center)
        rect_sec = hand_sec.get_rect(center=self.center)
        self.screen.blit(hand_min, rect_min)
        self.screen.blit(hand_sec, rect_sec)