import numpy as np
from copy import deepcopy
from enum import Enum

FREE = 0
FULL = 1
AXED = 2

class State:
	def __init__(self, height, width, clues_row=None, clues_col=None) -> None:
		self._field = np.zeros((height, width), np.byte)
		self.width = width
		self.height = height
		self.clues_row = clues_row if clues_row else [[] for _ in range(height)]
		self.clues_col = clues_col if clues_col else [[] for _ in range(width)]

		if len(self.clues_row) != self.height:
			raise ValueError(f'len row clues ({len(self.clues_row)}) does not match height ({self.height})')
		if len(self.clues_col) != self.width:
			raise ValueError(f'len col clues ({len(self.clues_col)}) does not match width ({self.width})')

		self.line_ids = {}
		for i in range(self.width):
			self.line_ids[f'C{i}'] = (slice(None), i)
		for i in range(self.height):
			self.line_ids[f'R{i}'] = (i, slice(None))

	def __getitem__(self, key):
		return self._field[key]

	def __setitem__(self, key, newvalue):
		self._field[key] = newvalue

	def get_line(self, line_id):
		return self._field[self.line_ids[line_id]]

	def get_clue(self, line_id: str):
		idx = int(line_id[1:])
		return self.clues_col[idx] if 'C' in line_id else self.clues_row[idx]

	def set_field(self, field:np.ndarray):
		if field.shape != (self.height, self.width):
			raise ValueError(f'new field shape {field.shape} does not match w/h ({self.width, self.height})')
		self._field = field

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'field': self._field.tolist(),
			'clues_row': self.clues_row,
			'clues_col': self.clues_col,
		}

	@classmethod
	def from_dict(cls, data):
		state = cls(
			height=data['height'],
			width=data['width'],
			clues_row=data['clues_row'],
			clues_col=data['clues_col'],
		)
		if 'field' in data:
			field = np.array(data['field'], dtype=np.byte)
			state.set_field(field)
		return state

	def copy(self):
		new = State(self.width, self.height, deepcopy(self.clues_row), deepcopy(self.clues_col))
		new._field = self._field.copy()
		return new

	def __str__(self) -> str:
		#determine padding around nonogram depending on max length of clues
		pad_x = max(len(clue) for clue in self.clues_row) * 3 + 1
		pad_y = max(len(clue) for clue in self.clues_col)
		vis = ['   ', '███', ' X ', ' ?3', ' ?4', ' ?5', ' ?6', ' ?7']
		lines = []

		# write down column clues
		for y in range(pad_y):
			line = ' ' * (pad_x + 1)
			# wirte down column numbers bottom aligned
			for clue in self.clues_col:
				off_y = pad_y - len(clue)
				if off_y <= y:
					line += f'{clue[y - off_y]:>2} '
				else:
					line += '   '

			lines.append(line)

		# hline
		sep = ' ' * pad_x + '-' * (self.width * 3 + 2)
		lines.append(sep)

		# write down row clues and rows
		for y in range(self.height):
			clue_str = ''.join([f'{num:>3}' for num in self.clues_row[y]])
			field_str = ''.join([vis[i] for i in self[y,:]])
			# field_str = ''.join([f'{i:>2} ' for i in self[y,:]])
			line = ' '*(pad_x - len(clue_str) - 1) + clue_str + ' |' + field_str + '|'
			lines.append(line)

		# hline
		lines.append(sep)
		return '\n'.join(lines)
