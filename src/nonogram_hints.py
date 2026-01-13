import pygame
from state import State, FREE, FULL, AXED
import numpy as np
import json

# json_path = 'json/bird_solved.json'
# json_path = 'json/night_solved.json'
import sys
json_path = sys.argv[1]

with open(json_path, 'r', encoding='utf-8') as f:
	json_val = json.load(f)
state = State.from_dict(json_val)


pygame.init()

W = state.width
H = state.height

# screen height dependent*
CELL = 750 // state.height
MARGIN = 20

visible = np.zeros((H, W), dtype=bool)

screen = pygame.display.set_mode((W * CELL + 2 * MARGIN, H * CELL + 2 * MARGIN))
clock = pygame.time.Clock()

def draw_grid():
	# draw cells
	for y in range(H):
		for x in range(W):
			rect = pygame.Rect(MARGIN + x * CELL, MARGIN + y * CELL, CELL+1, CELL+1)

			if not visible[y, x]:
				pygame.draw.rect(screen, (180, 180, 180), rect)
			else:
				v = state._field[y, x]
				if v == FULL:
					pygame.draw.rect(screen, (0, 0, 0), rect)
				elif v == FREE:
					pygame.draw.rect(screen, (255, 255, 255), rect)
				elif v == AXED:
					pygame.draw.rect(screen, (255, 255, 255), rect)
					pygame.draw.circle(screen, (0, 0, 0), rect.center, CELL // 6)

			pygame.draw.rect(screen, (100, 100, 100), rect, 1)

	# draw grid
	for i in range(W + 1):
		w = 3 if i % 5 == 0 else 1
		x = MARGIN + i * CELL
		pygame.draw.line(screen, (0, 0, 0), (x, MARGIN), (x, MARGIN + H * CELL), w)

	for i in range(H + 1):
		w = 3 if i % 5 == 0 else 1
		y = MARGIN + i * CELL
		pygame.draw.line(screen, (0, 0, 0), (MARGIN, y), (MARGIN + W * CELL, y), w)

# get clicked cell
def cell_from_pos(pos):
	px, py = pos
	if px < MARGIN or py < MARGIN:
		return None
	x = (px - MARGIN) // CELL
	y = (py - MARGIN) // CELL
	if 0 <= x < W and 0 <= y < H:
		return x, y
	return None

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.MOUSEBUTTONDOWN:
			c = cell_from_pos(event.pos)
			if c:
				x, y = c
				visible[y, x] = True

	screen.fill((240, 240, 240))
	draw_grid()
	pygame.display.flip()
	clock.tick(30)

pygame.quit()