from __future__ import annotations

from dataclasses import dataclass

import pygame

from .constants import COYOTE_TIME, GRAVITY, JUMP_SPEED, MOVE_SPEED, TILE_SIZE


@dataclass
class Collectible:
    rect: pygame.Rect
    value: int = 1
    collected: bool = False


@dataclass
class Goal:
    rect: pygame.Rect


class Player:
    def __init__(self, position: tuple[int, int]) -> None:
        self.rect = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE * 2)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.coyote_timer = 0.0
        self.jump_requested = False

    def request_jump(self) -> None:
        self.jump_requested = True

    def update(self, dt: float, solids: list[pygame.Rect], input_axis: float) -> None:
        self.velocity.x = input_axis * MOVE_SPEED
        self.velocity.y += GRAVITY * dt

        self.rect.x += int(self.velocity.x * dt)
        self._resolve_horizontal(solids)

        self.rect.y += int(self.velocity.y * dt)
        self._resolve_vertical(solids)

        if self.on_ground:
            self.coyote_timer = 0.0
        else:
            self.coyote_timer += dt

        if self.jump_requested:
            self._try_jump()
        self.jump_requested = False

    def _try_jump(self) -> None:
        if self.on_ground or self.coyote_timer <= COYOTE_TIME:
            self.velocity.y = -JUMP_SPEED
            self.on_ground = False
            self.coyote_timer = COYOTE_TIME + 1

    def _resolve_horizontal(self, solids: list[pygame.Rect]) -> None:
        for block in solids:
            if self.rect.colliderect(block):
                if self.velocity.x > 0:
                    self.rect.right = block.left
                elif self.velocity.x < 0:
                    self.rect.left = block.right

    def _resolve_vertical(self, solids: list[pygame.Rect]) -> None:
        self.on_ground = False
        for block in solids:
            if self.rect.colliderect(block):
                if self.velocity.y > 0:
                    self.rect.bottom = block.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = block.bottom
                    self.velocity.y = 0


class Enemy:
    def __init__(self, position: tuple[int, int]) -> None:
        self.rect = pygame.Rect(position[0], position[1], TILE_SIZE, TILE_SIZE)
        self.velocity = pygame.Vector2(140, 0)

    def update(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.velocity.y += GRAVITY * dt

        self.rect.x += int(self.velocity.x * dt)
        collided = False
        for block in solids:
            if self.rect.colliderect(block):
                collided = True
                if self.velocity.x > 0:
                    self.rect.right = block.left
                else:
                    self.rect.left = block.right
        if collided:
            self.velocity.x *= -1

        self.rect.y += int(self.velocity.y * dt)
        for block in solids:
            if self.rect.colliderect(block):
                if self.velocity.y > 0:
                    self.rect.bottom = block.top
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = block.bottom
                    self.velocity.y = 0


