from __future__ import annotations

import sys

import pygame

from .constants import (
    BACKGROUND_COLOR,
    COLLECTIBLE_COLOR,
    ENEMY_COLOR,
    FPS,
    GOAL_COLOR,
    GROUND_COLOR,
    PLAYER_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_COLOR,
)
from .entities import Player
from .level import load_level


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scrolling Platformer MVP")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    level_data = load_level()
    player = Player(level_data.player_spawn)
    deaths = 0
    score = 0
    level_complete = False

    def reset_level() -> None:
        nonlocal level_data, player, score, level_complete
        level_data = load_level()
        player = Player(level_data.player_spawn)
        score = 0
        level_complete = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    reset_level()
                elif event.key == pygame.K_SPACE:
                    player.request_jump()

        keys = pygame.key.get_pressed()
        input_axis = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_axis -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_axis += 1.0

        if not level_complete:
            player.update(dt, level_data.solids, input_axis)
            for enemy in level_data.enemies:
                enemy.update(dt, level_data.solids)

        for collectible in level_data.collectibles:
            if not collectible.collected and player.rect.colliderect(collectible.rect):
                collectible.collected = True
                score += collectible.value

        for enemy in level_data.enemies:
            if player.rect.colliderect(enemy.rect):
                deaths += 1
                player = Player(level_data.player_spawn)
                break

        if player.rect.colliderect(level_data.goal.rect):
            level_complete = True

        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, level_data.size_px[0] - SCREEN_WIDTH))
        camera_y = max(0, min(player.rect.centery - SCREEN_HEIGHT // 2, level_data.size_px[1] - SCREEN_HEIGHT))

        screen.fill(BACKGROUND_COLOR)

        for block in level_data.solids:
            pygame.draw.rect(screen, GROUND_COLOR, block.move(-camera_x, -camera_y))

        for collectible in level_data.collectibles:
            if not collectible.collected:
                pygame.draw.circle(
                    screen,
                    COLLECTIBLE_COLOR,
                    (collectible.rect.centerx - camera_x, collectible.rect.centery - camera_y),
                    collectible.rect.width // 2,
                )

        for enemy in level_data.enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy.rect.move(-camera_x, -camera_y))

        pygame.draw.rect(screen, GOAL_COLOR, level_data.goal.rect.move(-camera_x, -camera_y))
        pygame.draw.rect(screen, PLAYER_COLOR, player.rect.move(-camera_x, -camera_y))

        ui_text = f"Score: {score}  Deaths: {deaths}"
        ui_surface = font.render(ui_text, True, UI_COLOR)
        screen.blit(ui_surface, (12, 10))

        if level_complete:
            win_text = font.render("Victory! Press R to restart", True, UI_COLOR)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
            screen.blit(win_text, win_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
