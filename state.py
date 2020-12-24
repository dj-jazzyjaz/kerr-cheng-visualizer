import numpy as np

class State:
	'''
	Contains current info about the state. Defined class variables are valid
	program variables, and are either assigned a value or are None
	'''
	def __init__(self):
		self.var_names={}
		self.x=[]
	def vars(self):
		return {k:self.x[self.var_names[k]] for k in self.var_names}
	def vars_round(self):
		string = ""
		for k in self.var_names:
			val = self.x[self.var_names[k]]
			if val is not None:
				string += k + ":" + str(round(val, 2)) +  "; "
		return string

	def get(self,varname,default=None):
		if varname not in self.var_names:return default
		return self.x[self.var_names[varname]]
	def addVar(self,name,val=None):
		self.var_names[name]=len(self.x)
		self.x.append(val)
	def updateVar(self,name,val):
		self.x[self.var_names[name]]=val
	def __add__(self,other):
		new = other.copy()
		for k in self.var_names:
			if k in other.var_names:
				new.updateVar(k,self.get(k)+other.get(k))
			else:
				new.addVar(k,self.get(k))
		return new
	def scale(self,c):
		new = self.copy()
		f = lambda v:None if v is None else c*v
		for i in range(len(new.x)):
			new.x[i]=f(new.x[i])
		return new
	def copy(self):
		new = State()
		new.var_names=self.var_names.copy()
		new.x=self.x.copy()
		return new
	
# class State:
# 	'''
# 	Contains current info about the state. Defined class variables are valid
# 	program variables, and are either assigned a value or are None
# 	'''
# 	def __init__(self):
# 		self.var_names={}
# 		self.x=[]
# 	def vars(self):
# 		return {k:self.x[self.var_names[k]] for k in self.var_names}
# 	def get(self,varname,default=None):
# 		if varname not in self.var_names:return default
# 		return self.x[self.var_names[varname]]
# 	def addVar(self,name,val=None):
# 		self.var_names[name]=len(self.x)
# 		self.x.append(val)
# 	def updateVar(self,name,val):
# 		self.x[self.var_names[name]]=val
# 	def __add__(self,other):
# 		new = copy.deepcopy(other)
# 		for k in self.var_names:
# 			if k in other.var_names:
# 				new.updateVar(k,self.get(k)+other.get(k))
# 			else:
# 				new.addVar(k,self.get(k))
# 		return new
# 	def scale(self,c):
# 		new = copy.deepcopy(self)
# 		f = lambda v:None if v is None else c*v
# 		for i in range(len(new.x)):
# 			new.x[i]=f(new.x[i])
# 		return new

# class State:
# 	'''
# 	Contains current info about the state. Defined class variables are valid
# 	program variables, and are either assigned a value or are None
# 	'''
# 	def __init__(self):
# 		self.vars_dict=dict()
# 	def vars(self):
# 		return copy.deepcopy(self.vars_dict)
# 	def get(self,varname,default=None):
# 		return self.vars_dict.get(varname,default)
# 	def addVar(self,name,val=None):
# 		self.vars_dict[name]=val
# 	def updateVar(self,name,val):
# 		self.vars_dict[name]=val
# 	def __add__(self,other):
# 		new = copy.deepcopy(other)
# 		for k in self.vars_dict:
# 			if k in other.vars_dict:
# 				new.vars_dict[k]=self.vars_dict[k]+other.vars_dict[k]
# 			else:
# 				new.vars_dict[k]=self.vars_dict[k]
# 		return new
# 	def scale(self,c):
# 		new = copy.deepcopy(self)
# 		for k in self.vars_dict:
# 			if self.vars_dict[k] is not None:
# 				new.vars_dict[k]*=c
# 		return new
