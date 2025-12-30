import numpy as np
from copy import deepcopy
from enum import Enum

class Mark(Enum):
	FREE = 0
	FULL = 1
	AXED = 2
	PERHAPS = 3

class State:
	def __init__(self, height, width, rules_row=None, rules_col=None) -> None:
		self._field = np.zeros((height, width), np.byte)
		self.width = width
		self.height = height
		self.rules_row = rules_row if rules_row else [[] for _ in range(height)]
		self.rules_col = rules_col if rules_col else [[] for _ in range(width)]

		if len(self.rules_row) != self.height:
			raise ValueError(f'len row rules ({len(self.rules_row)}) does not match height ({self.height})')
		if len(self.rules_col) != self.width:
			raise ValueError(f'len col rules ({len(self.rules_col)}) does not match width ({self.width})')

	def __getitem__(self, key):
		return self._field[key]

	def __setitem__(self, key, newvalue):
		self._field[key] = newvalue

	def set_field(self, field:np.ndarray):
		if field.shape != (self.height, self.width):
			raise ValueError(f'new field shape {field.shape} does not match w/h ({self.width, self.height})')
		self._field = field

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'field': self._field.tolist(),
			'rules_row': self.rules_row,
			'rules_col': self.rules_col,
		}

	@classmethod
	def from_dict(cls, data):
		state = cls(
			height=data['height'],
			width=data['width'],
			rules_row=data['rules_row'],
			rules_col=data['rules_col'],
		)
		if 'field' in data:
			field = np.array(data['field'], dtype=np.byte)
			state.set_field(field)
		return state

	def copy(self):
		new = State(self.width, self.height, deepcopy(self.rules_row), deepcopy(self.rules_col))
		new._field = self._field.copy()
		return new

	def __str__(self) -> str:
		#determine padding around nonogram depending on max length of rules
		pad_x = max(len(rule) for rule in self.rules_row) * 3 + 1
		pad_y = max(len(rule) for rule in self.rules_col)
		vis = ['   ', '███', ' X ', ' * ']
		lines = []

		# write down column rules
		for y in range(pad_y):
			line = ' ' * pad_x
			# wirte down column numbers bottom aligned
			for rule in self.rules_col:
				off_y = pad_y - len(rule)
				if off_y <= y:
					line += f'{rule[y - off_y]:>2} '
				else:
					line += '   '

			lines.append(line)

		# hline
		sep = ' ' * pad_x + '-' * (self.width * 3)
		lines.append(sep)

		# write down row rules and rows
		for y in range(self.height):
			rule_str = ''.join([f'{num:>3}' for num in self.rules_row[y]])
			field_str = ''.join([vis[i] for i in self[y,:]])
			# field_str = ''.join([f'{i:>2} ' for i in self[y,:]])
			line = ' '*(pad_x - len(rule_str) - 1) + rule_str + ' |' + field_str + '|'
			lines.append(line)

		# hline
		lines.append(sep)
		return '\n'.join(lines)


			


