import numpy as np
import random
import matplotlib.pyplot as plt
from nono_math import calc_clue_len
FULL = 1
AXED = 0


def gen_line_patterns(clue, line_len) -> np.ndarray:
	def dfs(idx, pos, acc):
		if idx == len(clue):
			yield acc
			return
		block = clue[idx]
		max_start = line_len - sum(clue[idx:]) - (len(clue) - idx - 1)
		for start in range(pos, max_start + 1):
			new_acc = acc.copy()
			new_acc[start:start + block] = FULL
			yield from dfs(idx + 1, start + block + 1, new_acc)

	return np.vstack(list(dfs(0, 0, np.full(line_len, AXED, dtype=np.byte))))


def random_clue(target_len, max_block_len):
	'''generate a clue with random '''
	clue = [max_block_len]
	remaining = target_len - max_block_len - 1
	while remaining > 0:
		block = random.randint(1, min(max_block_len, remaining))
		remaining -= 1
		remaining -= block
		clue.append(block)

	random.shuffle(clue)

	# try to fix 1 off clues (not always possible e.g. filling line 2 with 1s)
	if calc_clue_len(clue) == target_len - 1:
		for i in range(1, len(clue)):
			if clue[i] < max_block_len:
				clue[i] += 1
				return clue
		return None
	return clue


def strongest_non_certain_fill_prob(patterns):
	# calc the mean of each column
	fill_freq = patterns.mean(axis=0)
	# mask out 0%s and 100%s
	mask = fill_freq < 1.0
	return max(fill_freq[mask].max(), 1 - fill_freq[mask].min())


def collect_data(
	line_len,
	samples_per_block_len
):
	points = []

	from tqdm import tqdm
	# x-axis: total length of a clue
	for clue_len in tqdm(range(1, line_len)):
		# y-axis: max block length in a given clue (limited by total length of course)
		for max_block_len in range(1, clue_len + 1):
			if max_block_len == 1 and clue_len % 2 == 0:
				continue
			# create n samples
			for _ in range(samples_per_block_len):
				clue = random_clue(clue_len, max_block_len)
				if clue is None:
					continue
				patterns = gen_line_patterns(clue, line_len)
				p = strongest_non_certain_fill_prob(patterns)
				if p is not None:
					points.append((clue_len, max_block_len, p))

	return np.array(points)


def plot_grid(points, line_len):
	# integer grid extents
	x_vals = points[:, 0].astype(int)
	y_vals = points[:, 1].astype(int)
	c_vals = points[:, 2]

	x_max = x_vals.max()
	y_max = y_vals.max()

	# grid for averaging
	grid = np.full((y_max + 1, x_max + 1), np.nan)
	count = np.zeros_like(grid)

	for x, y, c in zip(x_vals, y_vals, c_vals):
		if np.isnan(grid[y, x]):
			grid[y, x] = 0.0
		grid[y, x] += c
		count[y, x] += 1

	grid /= np.where(count == 0, np.nan, count)

	plt.figure()
	plt.imshow(
		grid,
		origin="lower",
		aspect=1.,
		cmap="viridis",
		vmin=0.5,
		vmax=1.
	)

	from matplotlib.ticker import MaxNLocator

	ax = plt.gca()
	ax.xaxis.set_major_locator(MaxNLocator(integer=True))
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))

	plt.colorbar(label="max non-certain FULLorAXED probability")
	plt.xlabel("total clue length")
	plt.ylabel("largest clue block")
	plt.title(f"Highest probability pixel (line length: {line_len})")
	plt.tight_layout()
	plt.show()


if __name__ == "__main__":
	line_len = 30
	samples = 2
	points = collect_data(line_len, samples)
	# plot(points)
	plot_grid(points, line_len)