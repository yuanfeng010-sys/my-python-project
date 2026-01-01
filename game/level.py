from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from .constants import TILE_SIZE
from .entities import Collectible, Enemy, Goal

LEVEL_PATH = Path(__file__).resolve().parent / "levels" / "level1.txt"


@dataclass
class LevelData:
    solids: list[pygame.Rect]
    enemies: list[Enemy]
    collectibles: list[Collectible]
    goal: Goal
    player_spawn: tuple[int, int]
    size_px: tuple[int, int]


def load_level() -> LevelData:
    lines = LEVEL_PATH.read_text(encoding="utf-8").splitlines()
    width = max(len(line) for line in lines)
    height = len(lines)

    solids: list[pygame.Rect] = []
    enemies: list[Enemy] = []
    collectibles: list[Collectible] = []
    goal_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE * 2)
    player_spawn = (TILE_SIZE, TILE_SIZE)

    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE
            if char == "#":
                solids.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif char == "P":
                player_spawn = (x, y - TILE_SIZE)
            elif char == "E":
                enemies.append(Enemy((x, y)))
            elif char == "C":
                collectibles.append(Collectible(pygame.Rect(x + 8, y + 8, 16, 16)))
            elif char == "G":
                goal_rect = pygame.Rect(x, y - TILE_SIZE, TILE_SIZE, TILE_SIZE * 2)

    size_px = (width * TILE_SIZE, height * TILE_SIZE)
    return LevelData(solids, enemies, collectibles, Goal(goal_rect), player_spawn, size_px)
