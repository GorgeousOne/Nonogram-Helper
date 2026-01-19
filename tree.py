from typing import Set, List, Collection
from typing_extensions import Self
from nono_math import calc_num_patterns

class BlockPlacement:
	'''A node representing one possible placement of a clue block in its line'''
	def __init__(self, block_idx, start, length):
		self.block_idx = block_idx
		self.start = start
		self.end = start + length - 1
		self.children: Set[Self] = set()
		self.parents: Set[Self] = set()

	def contains(self, cell):
		'''Returns true if a cell position intersects with this block placement'''
		return self.start <= cell <= self.end

	def __hash__(self) -> int:
		return hash((self.block_idx, self.start))

	def __repr__(self) -> str:
		return f'#{self.block_idx}[{self.start}-{self.end}]'


class BlockSet:
	'''Container for all possible placements (nodes) of a clue block'''
	def __init__(self, block_idx):
		self.block_idx = block_idx
		self.nodes: Set[BlockPlacement] = set()

	def __repr__(self) -> str:
		return str(self.nodes)

class PatternTree:
	'''Container for all clue block patterns of a line using a tree.
	Each node holds one possible placement of a block.
	Child nodes are placements of the subsequent clue block.
	A full pattern is encoded in a path from one root node to one leaf node.
	This way partial clue patterns repeating across multiple patterns can be reused
	simply by creating new edges instead of generating millions of matrix rows.

	Finding invalid patterns and cells with fixed values has probably become algorithmically
	more complex, but the speed of generating and traversing a small tree speaks for itself,
	compared to crunching numbers in matrix columns with millions of entries.

	I want to give a stupid example with a big nonogram:
	In the 'wolves' nonogram there is a row of length 75, with clues [1 1 4 3 3 1 2 2 2 1 1 4 3 4 5 3]
	That allows for 300_540_195 patterns, which can be represented as tree with merely 256 nodes + 2040 edges.
	'''
	def __init__(self, line_id, clue, line_len):
		self.line_id = line_id
		self._num_blocks = len(clue)
		self._levels: List[BlockSet] = [BlockSet(i) for i in range(self._num_blocks)]
		self._node_count = 0
		self._num_patterns = calc_num_patterns(clue, line_len)
		self._build(clue, line_len)

	def _build(self, clue, line_len):
		# precompute possible blocks with varying start positions
		next_min_start = 0
		for i, block_len in enumerate(clue):
			rem = sum(clue[i:]) + (self._num_blocks - i - 1)
			max_start = line_len - rem
			level = self._levels[i]

			for start in range(next_min_start, max_start + 1):
				node = BlockPlacement(i, start, block_len)
				level.nodes.add(node)
				self._node_count += 1

			next_min_start += block_len + 1

		# link possible permutations of neighboring blocks
		for i in range(self._num_blocks - 1):
			for parent in self._levels[i].nodes:
				for child in self._levels[i + 1].nodes:
					# keep gap between blocks
					if child.start > parent.end + 1:
						parent.children.add(child)
						child.parents.add(parent)

	def set_cell_axed(self, cell):
		'''Remove all patterns if given position is AXED'''
		# remove patterns if AXED cell/position intersects any block
		for level in list(self._levels):
			for node in list(level.nodes):
				if node.contains(cell):
					self._remove_node(node)

	def set_cell_full(self, cell):
		'''Removes all patterns that are invalid if given cell is FULL'''
		# remove patterns where FULL cell lies in the gap (node edge) between two blocks
		for level in self._levels[:-1]:
			for parent in list(level.nodes):
				if parent.end >= cell:
					continue
				for child in list(parent.children):
					if child.start > cell:
						self._unlink(parent, child)
		# remove patterns with first block starting after FULL cell
		for node in list(self._levels[0].nodes):
			if node.start > cell:
				self._remove_node(node)
		# remove patterns with last block ending before FULL cell
		for node in list(self._levels[-1].nodes):
			if node.end < cell:
				self._remove_node(node)

	def do_all_patterns_cover(self, cell):
		'''Returns true if all remaining possible patterns of this line are FULL at a given cell'''
		# check if all nodes of exactly one block cover the position
		# => if multiple (moving) blocks were able to cover a position, then at least one other pattern
		# would exist where the gap between said blocks is placed on the cell in question
		levels_covering = set()
		nodes_covering = []
		for level in self._levels:
			for node in level.nodes:
				if node.contains(cell):
					levels_covering.add(node.block_idx)
					nodes_covering.append(node)
		if len(levels_covering) != 1:
			return False
		return len(nodes_covering) == len(self._levels[levels_covering.pop()].nodes)

	def do_all_patterns_avoid(self, cell):
		'''Returns true if all remaining possible patterns of this line have a gap at the given cell (aka AXED)'''
		for level in list(self._levels):
			for node in list(level.nodes):
				if node.contains(cell):
					return False
		return True

	def _unlink(self, parent, child):
		'''Removes patterns where two adjacent block positions (parent child) are invalid
		(due to a FULL cell in the gap between them)'''
		# reduce total number of patterns by number of disconnected paths
		self._num_patterns -= self._count_parent_patterns(parent) * self._count_child_patterns(child)
		# print('unlink', self._count_parent_patterns(parent) * self._count_child_patterns(child))
		parent.children.discard(child)
		child.parents.discard(parent)
		# TODO find out if this only happens under very specific conditions
		if not child.parents:
			self._remove_node(child, False)
		if not parent.children:
			self._remove_node(parent, False)

	def _remove_node(self, node:BlockPlacement, reduce_num_patterns=True):
		'''Remove a block node, including recursively removing patterns connected to it'''
		# update number of patterns if node is still fully connected
		if reduce_num_patterns:
			self._num_patterns -= self.count_patterns(node)

		dirty = set()
		# unlink node from its parents and children
		for parent in list(node.parents):
			parent.children.discard(node)
			dirty.add(parent)
		for child in list(node.children):
			child.parents.discard(node)
			dirty.add(child)
		# remove node from its level
		self._levels[node.block_idx].nodes.discard(node)
		self._node_count -= 1

		if self._node_count == 0:
			raise ValueError(f'No possible paths left in line {self.line_id} after removing {node}')

		# prune orphans upward and downward
		self._cleanup(dirty, False)

	def _cleanup(self, dirty_nodes:Collection[BlockPlacement], reduce_num_patterns=True):
		dead = [
			node for node in dirty_nodes if
				(node.block_idx > 0 and not node.parents) or
				(node.block_idx < len(self._levels)-1 and not node.children)
		]
		for node in dead:
			self._remove_node(node, reduce_num_patterns)

	def get_cell_probability(self, cell):
		num_patterns = 0
		for level in self._levels:
			for node in level.nodes:
				if not node.contains(cell):
					continue
				num_patterns += self.count_patterns(node)
		return num_patterns

	def _count_tree_size(self):
		# return sum((self._count_child_patterns(n) for n in self._levels[0].nodes))
		roots = self._levels[0].nodes
		num_node_visits = {n: 1 for n in roots}
		to_visit = set(roots)
		# walk tree paths reachable from given node downwards
		for _ in range(self._num_blocks-1):
			next_to_visit = set()
			for node in to_visit:
				# accumulate node visits by parent node visits
				for child in node.children:
					next_to_visit.add(child)
					num_node_visits[child] = num_node_visits.get(child, 0) + num_node_visits[node]
			to_visit = next_to_visit
		# sum total paths at leaf node level
		total_patterns = sum((num_node_visits[c] for c in to_visit))
		return total_patterns

	# TODO test if updating number of total patterns only when used is faster
	def count_patterns(self, node:BlockPlacement) -> int:
		return self._count_parent_patterns(node) * self._count_child_patterns(node)

	def _count_parent_patterns(self, node:BlockPlacement) -> int:
		if len(node.parents) == 0:
			return 1
		num_node_visits = {p: 1 for p in node.parents}
		to_visit = set(node.parents)
		total_patterns = 0
		# walk tree paths reachable from given node upwards
		for _ in range(0, node.block_idx-1):
			next_to_visit = set()
			for parent in to_visit:
				# accumulate node visits by child node visits
				for grandparent in parent.parents:
					num_node_visits[grandparent] = num_node_visits.get(grandparent, 0) + num_node_visits[parent]
					next_to_visit.add(grandparent)
			to_visit = next_to_visit
		# sum total paths at leaf node level
		total_patterns = sum((num_node_visits[p] for p in to_visit))
		return total_patterns

	def _count_child_patterns(self, node:BlockPlacement) -> int:
		if len(node.children) == 0:
			return 1
		num_node_visits = {c: 1 for c in node.children}
		to_visit = set(node.children)
		# walk tree paths reachable from given node downwards
		for _ in range(node.block_idx+1, self._num_blocks-1):
			next_to_visit = set()
			for child in to_visit:
				# accumulate node visits by parent node visits
				for grand_child in child.children:
					next_to_visit.add(grand_child)
					num_node_visits[grand_child] = num_node_visits.get(grand_child, 0) + num_node_visits[child]
			to_visit = next_to_visit
		# sum total paths at leaf node level
		total_patterns = sum((num_node_visits[c] for c in to_visit))
		return total_patterns


	def __repr__(self) -> str:
		return '\n'.join([str(l) for l in self._levels])