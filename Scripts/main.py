import pygame
from loader import Loader

LL = Loader()
S = LL.LoadSettings()
WINDOW = pygame.display.set_mode(S["resolution"])

curLevel = LL.GetLevel("level1.lvl")

scaledRes = (S["resolution"][0] * S["ifs"], S["resolution"][1] * S["ifs"])
centeredBlitPos = ((S["resolution"][0] * (1 - S["ifs"])) / 2, (S["resolution"][1] * (1 - S["ifs"])) / 2)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:   curLevel.ResetLevel()
            elif event.key == pygame.K_w: curLevel.MovePlayer(0)
            elif event.key == pygame.K_a: curLevel.MovePlayer(3)
            elif event.key == pygame.K_s: curLevel.MovePlayer(2)
            elif event.key == pygame.K_d: curLevel.MovePlayer(1)

    surf = curLevel.DrawFinalLevel(scaledRes, S["maxdrawdepth"])
    backround, drawpos = curLevel.DrawBackround(scaledRes, centeredBlitPos)

    if backround != None: WINDOW.blit(backround, drawpos)
    WINDOW.blit(surf, centeredBlitPos)

    pygame.display.update()
    clock.tick(60)