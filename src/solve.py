# monochrome nonogram

from state import State, Mark
import numpy as np

def solve(gram:State):
	fill_initial(gram)


def fill_initial(gram:State):
	for row in range(gram.height):
		fill_initial_line(gram.clues_row[row], gram[row, :])
	for col in range(gram.width):
		fill_initial_line(gram.clues_col[col], gram[:, col])


def gen_perms(clue, line_len):
	# mark a block
    def place_block(start, size):
        arr = np.zeros(line_len, dtype=np.byte)
        arr[start:start + size] = Mark.FULL.value
        return arr

	# recursively yields permutations
    def dfs(idx, pos, acc):
		# return array if no more clue blocks
        if idx == len(clue):
            yield acc
            return
        block = clue[idx]
		# calc range of possible block placements
        max_start = line_len - sum(clue[idx:]) - (len(clue) - idx - 1)
		# create variants with new block in all possible places
        for s in range(pos, max_start + 1):
            placed = place_block(s, block)
			# merge existing perm part with new block
            merged = acc | placed
            yield from dfs(idx + 1, s + block + 1, merged)

	# collect yielded permutations as list
    return list(dfs(0, 0, np.zeros(line_len, dtype=np.byte)))


def splits_len(splits):
	return np.sum(splits[:, 1] - splits[:, 0])


def get_clue_len(clue):
	return sum(clue) + len(clue) - 1


def fill_initial_line(clue, line):
	# get mimimum length of clues combined
	clue_len = get_clue_len(clue)
	# get possible offset
	diff = len(line) - clue_len
	i = 0
	# fill possible space and 
	for num in clue:
		for j in range(i, i + num + diff):
			if line[j] == Mark.FREE.value:
				line[j] = Mark.PERHAPS.value
		for j in range(i + diff, i + num):
			line[j] = Mark.FULL.value
		i += num
		if i < len(line) and diff == 0:
			line[i] = Mark.AXED.value
		i += 1


def split_line(line):
	idx = np.where(line == Mark.AXED.value)[0]
	prev = 0
	chunks = []
	for i in idx:
		if i > prev:
			chunks.append((prev, i))
		prev = i+1
	last = len(line)
	if last > prev:
		chunks.append((prev, last))
	return np.array(chunks)


perms = gen_perms([16, 3, 2], 25)
for arr in perms:
    print(''.join('#' if x else '-' for x in arr))
