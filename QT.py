import numpy as _np
import save as _save
import random as _rnd

class QT:
	def __init__(self, actions_space, path=None, epsilon=0.3, epsilon_dec=0.9998, start_dec=[-10,10], learningR=0.1, discount=0.95, complex_mode=False) -> None:
		self.qt = {"gen":0}
		if path != None:
			self.load(path)
		self.actions_space = actions_space
		self.learningR = learningR
		self.discount = discount
		self.start_dec = start_dec
		self.epsilon = epsilon
		self.eps_dec = epsilon_dec
		self.is_complex = complex_mode

	def load(self, path):
		self.qt = _save.load(path)
	
	def save(self, path):
		_save.save(path, self.qt)
	
	def new_gen(self):
		self.qt["gen"] += 1

	def get_action(self, obs, doable_actions=[]):
		if not obs in self.qt:
			if not self.is_complex:
				self.qt[obs] = [_rnd.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space)]
			else:
				self.qt[obs] = {action:-_rnd.random() for action in doable_actions}
		if _rnd.random() > self.epsilon:
			if not self.is_complex:
				action = _np.argmax(self.qt[obs])
			else:
				action = list(self.qt[obs].keys())[_np.argmax(list(self.qt[obs].values()))]
		else:
			if not self.is_complex:
				action = _rnd.randint(0, self.actions_space)
			else:
				action = _rnd.choice(list(self.qt[obs].keys()))
		return action

	def set_reward(self, old_state, action, new_state, reward, doable_actions=[]):
		obs = old_state
		new_obs = new_state

		if not new_obs in self.qt:
			if not self.is_complex:
				self.qt[new_obs] = [_rnd.uniform(self.start_dec[0], self.start_dec[1]) for _ in range(self.actions_space)]
			else:
				self.qt[new_obs] = {action:-_rnd.random() for action in doable_actions}

		if self.is_complex:
			max_fq = max(_np.array(self.qt[new_obs].values()).tolist())
		else:
			max_fq = max(self.qt[new_obs])

		curr_q = self.qt[obs][action]
		new_q = ( 1 - self.learningR ) * curr_q + self.learningR * ( reward + self.discount * max_fq )
		self.qt[obs][action] = new_q
		self.epsilon *= self.eps_dec
