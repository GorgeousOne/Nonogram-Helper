from typing import Set, List
from typing_extensions import Self


class BlockNode:
	def __init__(self, layer_idx, start, length):
		self.layer_idx = layer_idx
		self.start = start
		self.end = start + length - 1
		self.children: Set[Self] = set()
		self.parents: Set[Self] = set()

	def contains(self, pos):
		return self.start <= pos <= self.end

	def __str__(self) -> str:
		return f'#{self.layer_idx}:[{self.start}-{self.end}]'

class Layer:
	def __init__(self, block_idx):
		self.block_idx = block_idx
		self.nodes: Set[BlockNode] = set()


class PlacementTree:
	def __init__(self, line_id, clue, line_len):
		self.line_id = line_id
		self._layers: List[Layer] = [Layer(i) for i in range(len(clue))]
		self._node_count = 0
		self._build(clue, line_len)

	def _build(self, clue, line_len):
		# precompute possible blocks with varying start positions
		next_min_start = 0
		for i, block_len in enumerate(clue):
			rem = sum(clue[i:]) + (len(clue) - i - 1)
			max_start = line_len - rem
			layer = self._layers[i]

			for s in range(next_min_start, max_start + 1):
				node = BlockNode(i, s, block_len)
				layer.nodes.add(node)
				self._node_count += 1

			next_min_start += block_len + 1

		# link possible permutations of neighboring blocks
		for i in range(len(clue) - 1):
			for parent in self._layers[i].nodes:
				for child in self._layers[i + 1].nodes:
					# keep gap between blocks
					if child.start > parent.end + 1:
						parent.children.add(child)
						child.parents.add(parent)

	def set_pos_axed(self, pos):
		# check if AXED cell/position intersects any permutations
		for l in list(self._layers):
			for n in list(l.nodes):
				if n.contains(pos):
					self._remove_node(n)

	def set_pos_full(self, pos):
		# check if FULL cell/position lies in a gap (node edge) of two blocks
		for l in self._layers[:-1]:
			for parent in list(l.nodes):
				if parent.end >= pos:
					continue
				for child in list(parent.children):
					if child.start > pos:
						self._unlink(parent, child)
		for n in list(self._layers[0].nodes):
			if n.start > pos:
				self._remove_node(n)
		# invalidate paths where last block ends before FULL pos
		for n in list(self._layers[-1].nodes):
			if n.end < pos:
				self._remove_node(n)

	def do_all_paths_cover(self, pos):
		# check if all nodes of exactly one layer cover the position
		# this relies on the fact that if two layers (moving blocks) would be able to cover a position,
		# then it would also be possible to have a gap exactly at said position
		layers_covering = set()
		nodes_covering = []
		for l in self._layers:
			for n in l.nodes:
				if n.contains(pos):
					layers_covering.add(n.layer_idx)
					nodes_covering.append(n)
		if len(layers_covering) != 1:
			return False
		# i hate sets xD
		for idx in layers_covering:
			return len(nodes_covering) == len(self._layers[idx].nodes)

	def do_all_paths_avoid(self, pos):
		for l in list(self._layers):
			for n in list(l.nodes):
				if n.contains(pos):
					return False
		return True

	def _unlink(self, parent, child):
		parent.children.discard(child)
		child.parents.discard(parent)
		if not child.parents:
			self._remove_node(child)
		if not parent.children:
			self._remove_node(parent)

	def _remove_node(self, node):
		# remove node and (recursively) remove connected permutations
		dirty = set()
		# unlink node from its parents and children
		for p in list(node.parents):
			p.children.discard(node)
			dirty.add(p)
		for c in list(node.children):
			c.parents.discard(node)
			dirty.add(c)
		# remove node from its layer
		self._layers[node.layer_idx].nodes.discard(node)
		self._node_count -= 1

		if self._node_count == 0:
			raise ValueError(f'No possible paths left in line {self.line_id} after removing {node}')

		# prune orphans upward and downward
		self._cleanup(dirty)

	def _cleanup(self, dirty_nodes):
		dead = [
			n for n in dirty_nodes if
				(n.layer_idx > 0 and not n.parents) or
				(n.layer_idx < len(self._layers)-1 and not n.children)
		]
		for n in dead:
			self._remove_node(n)
