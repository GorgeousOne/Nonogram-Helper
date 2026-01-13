from typing import Set, List, Collection
from typing_extensions import Self


class SegmentPlacementNode:
	'''A node representing one possible placement of a clue segment in its line'''
	def __init__(self, segment_idx, start, length):
		self.segment_idx = segment_idx
		self.start = start
		self.end = start + length - 1
		self.children: Set[Self] = set()
		self.parents: Set[Self] = set()

	def contains(self, cell):
		'''Returns true if a cell position intersects with this segment placement'''
		return self.start <= cell <= self.end

	def __str__(self) -> str:
		return f'#{self.segment_idx}:[{self.start}-{self.end}]'

class SegmentSet:
	'''Container for all possible placements (nodes) of a clue segment'''
	def __init__(self, segment_idx):
		self.segment_idx = segment_idx
		self.nodes: Set[SegmentPlacementNode] = set()


class PatternTree:
	'''Container for all clue segment patterns of a line using a tree.
	Each node holds one possible placement of a segment.
	Child nodes are placements of the subsequent clue segment.
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
		self._levels: List[SegmentSet] = [SegmentSet(i) for i in range(len(clue))]
		self._node_count = 0
		self._build(clue, line_len)
		if line_id == ('R', 3):
			edges = 0
			for l in self._levels:
				for n in l.nodes:
					edges += len(n.children)
			print(line_id, 'nodes', self._node_count, 'edges', edges)

	def _build(self, clue, line_len):
		# precompute possible blocks with varying start positions
		next_min_start = 0
		for i, block_len in enumerate(clue):
			rem = sum(clue[i:]) + (len(clue) - i - 1)
			max_start = line_len - rem
			level = self._levels[i]

			for l in range(next_min_start, max_start + 1):
				node = SegmentPlacementNode(i, l, block_len)
				level.nodes.add(node)
				self._node_count += 1

			next_min_start += block_len + 1

		# link possible permutations of neighboring blocks
		for i in range(len(clue) - 1):
			for parent in self._levels[i].nodes:
				for child in self._levels[i + 1].nodes:
					# keep gap between blocks
					if child.start > parent.end + 1:
						parent.children.add(child)
						child.parents.add(parent)

	def set_cell_axed(self, cell):
		'''Remove all patterns if given position is AXED'''
		# remove patterns if AXED cell/position intersects any segment
		for l in list(self._levels):
			for n in list(l.nodes):
				if n.contains(cell):
					self._remove_node(n)

	def set_cell_full(self, cell):
		'''Removes all patterns that are invalid if given cell is FULL'''
		# remove patterns where FULL cell lies in the gap (node edge) between two segments
		for l in self._levels[:-1]:
			for parent in list(l.nodes):
				if parent.end >= cell:
					continue
				for child in list(parent.children):
					if child.start > cell:
						self._unlink(parent, child)
		# remove patterns with first segment starting after FULL cell
		for n in list(self._levels[0].nodes):
			if n.start > cell:
				self._remove_node(n)
		# remove patterns with last segment ending before FULL cell
		for n in list(self._levels[-1].nodes):
			if n.end < cell:
				self._remove_node(n)

	def do_all_patterns_cover(self, cell):
		'''Returns true if all remaining possible patterns of this line are FULL at a given cell'''
		# check if all nodes of exactly one segment cover the position
		# => if multiple (moving) segments were able to cover a position, then at least one other pattern
		# would exist where the gap between said blocks is placed on the cell in question
		levels_covering = set()
		nodes_covering = []
		for l in self._levels:
			for n in l.nodes:
				if n.contains(cell):
					levels_covering.add(n.segment_idx)
					nodes_covering.append(n)
		if len(levels_covering) != 1:
			return False
		return len(nodes_covering) == len(self._levels[levels_covering.pop()].nodes)

	def do_all_patterns_avoid(self, cell):
		'''Returns true if all remaining possible patterns of this line have a gap at the given cell (aka AXED)'''
		for l in list(self._levels):
			for n in list(l.nodes):
				if n.contains(cell):
					return False
		return True

	def _unlink(self, parent, child):
		'''Removes patterns where two adjacent segment positions (parent child) are invalid
		(due to a FULL cell in the gap between them)'''
		parent.children.discard(child)
		child.parents.discard(parent)
		if not child.parents:
			self._remove_node(child)
		if not parent.children:
			self._remove_node(parent)

	def _remove_node(self, node):
		'''Remove a segment node, including recursively removing patterns connected to it'''
		dirty = set()
		# unlink node from its parents and children
		for p in list(node.parents):
			p.children.discard(node)
			dirty.add(p)
		for c in list(node.children):
			c.parents.discard(node)
			dirty.add(c)
		# remove node from its level
		self._levels[node.segment_idx].nodes.discard(node)
		self._node_count -= 1

		if self._node_count == 0:
			raise ValueError(f'No possible paths left in line {self.line_id} after removing {node}')

		# prune orphans upward and downward
		self._cleanup(dirty)

	def _cleanup(self, dirty_nodes:Collection[SegmentPlacementNode]):
		dead = [
			n for n in dirty_nodes if
				(n.segment_idx > 0 and not n.parents) or
				(n.segment_idx < len(self._levels)-1 and not n.children)
		]
		for n in dead:
			self._remove_node(n)
