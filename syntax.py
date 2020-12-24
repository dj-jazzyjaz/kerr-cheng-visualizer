'''
File defining base types
'''
from state import State
from ode import *
import pdb
import numpy as np
def matchParen(s,i):
	l=s[i]
	if l=='(':
		r=")"
	elif l=="{":
		r="}"
	elif l=="[":
		r="]"
	elif l=="<":
		r=">"
	else: 
		raise Exception()
	cnt=0
	for j in range(i,len(s)):
		if s[j]==l:
			cnt+=1
		elif s[j]==r:
			cnt-=1
		if cnt==0:return j
	return None
findend = lambda st,w: st.find(w)+len(w)
def strideq(s,w,i):
	if(i+len(w)>len(s)):return False
	return s[i:i+len(w)]==w
class HP:
	pass
	'''
	expand(self, state) returns a list with (choices, e) elements,
	where choices is a list of top to bottom choices to take to get from state to e,
	where e is the end state.

	eval(self, state, choices) returns a list of states, where states are appended
	for ODE runs
	'''

class Form:
	def __init__(self, arg):
		self.arg = arg.strip().replace("\n"," ")
		#strip out parens ((like this))
		while self.arg[0]=='(' and matchParen(self.arg,0)==len(self.arg)-1:
			self.arg=self.arg[1:-1].strip()
		#replace = with ==
		i=1
		while i<len(self.arg)-1:
			if self.arg[i]=='=' and (self.arg[i-1] not in ['<',">","="]) and (self.arg[i+1] not in ['<',">","="]):
				#insert another =
				self.arg=self.arg[:i]+'='+self.arg[i:]
			i+=1
		self.arg=self.arg.replace("true","True").replace("false","False")
	def eval(self, state):
		i=0
		while(i<len(self.arg)):
			if self.arg[i]=='(':
				i=matchParen(self.arg,i)
			else:
				if strideq(self.arg,"<->",i):
					#split the string at the <-> and recurse
					lhs=Form(self.arg[:i])
					rhs=Form(self.arg[i+3:])
					lv=lhs.eval(state)
					rv=rhs.eval(state)
					return (lv and rv) or (not lv and not rv)
				elif strideq(self.arg,'->',i):
					lhs=Form(self.arg[:i])
					rhs=Form(self.arg[i+2:])
					lv=lhs.eval(state)
					rv=rhs.eval(state)
					return (not lv) or rv
				elif strideq(self.arg,'<-',i):
					lhs=Form(self.arg[:i])
					rhs=Form(self.arg[i+2:])
					lv=lhs.eval(state)
					rv=rhs.eval(state)
					return (not rv) or lv
			i+=1
		#if we didn't find any special chars just evaluate it
		val=eval(self.arg, state.vars())
		if val is None:
			print(state.vars())
			raise Exception("Called eval on formula with undefined variables")
		return val

	def get_heuristic(self,state,arg=None):
		#returns the "distance" from the truth boundary
		if arg is None:
			arg=self.arg.replace("not ","").strip()
			if '->' in arg or '<->' in arg or '<-' in arg:
				raise Exception("Sorry, implies are not implemented in auto heuristic evaluation")
		#might be parens around whole thing
		while arg[0]=='(' and matchParen(arg,0)==len(arg)-1:
			arg=arg[1:-1].strip()
		if 'and' not in arg and 'or' not in arg:
			#basecase: no conjunctions
			#return a big number since we don't want 
			#==/!= to factor into our heuristic
			if '==' in arg:return None
			#if <,>,<=,>= then return difference of the sides to each other
			separators = ['<',">","<=",">="]
			i=0
			sep=None
			run=True
			while i<len(arg) and run:
				i+=1
				for s in range(len(separators)):
					if strideq(arg,separators[s],i):
						if(arg[i+1]=="=" and s<2):continue
						sep=s
						run=False
						break
			lhs=arg[:i].strip()
			rhs=arg[i+len(separators[sep]):].strip()
			return abs(Term(lhs).eval(state)-Term(rhs).eval(state))
		else:
			#for or: return max of both sides
			#for and: return min
			#find the top level conjunction
			op_rank=[' or ',' and ']
			bestid=0
			i=0
			bestop=len(op_rank)+1
			while i<len(arg) and bestop!=0:
				if arg[i]=='(':
					i=matchParen(arg,i)
					continue
				for r in range(len(op_rank)):
					if strideq(arg,op_rank[r],i):
						if r<bestop:
							bestid=i
							bestop=r
						break
				i+=1
			
			lhs=arg[:bestid].strip()
			rhs=arg[bestid+len(op_rank[bestop]):].strip()
			if bestop==0:
				lval=self.get_heuristic(state,lhs)
				rval=self.get_heuristic(state,rhs)
				if lval is None and rval is None:return None
				elif lval is None: return rval
				elif rval is None: return lval
				return max(lval,rval)
			else:
				lval=self.get_heuristic(state,lhs)
				rval=self.get_heuristic(state,rhs)
				if lval is None and rval is None:return None
				elif lval is None: return rval
				elif rval is None: return lval
				return min(lval,rval)


	def print(self,level=0):
		print(" "*level+"Form:",self.arg,end='')
	def tostring(self, level=0):
		return self.arg

class Term:
	def __init__(self, arg):
		prohibited=["=","<",">","!","++","{","}",";"]
		for p in prohibited:
			if p in arg:
				raise Exception("Tried to construct a term with invalid string: %s"%arg)
		self.arg = arg.strip().replace("\n"," ")

	def eval(self, state):
		val=eval(self.arg, state.vars())
		if val is None:
			print(state.vars())
			raise Exception("Called eval on term with undefined variables")
		return val
	def print(self,level=0):
		print(" "*level+"Term:",self.arg,end='')
	def tostring(self, level=0):
		return self.arg
'''
Hybrid Programs
'''

class Choice(HP):
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	def print(self,level=0):
		print(" "*level+"Choice:")
		self.lhs.print(level+1)
		self.rhs.print(level+1)
	def expand(self, start_state):
		traceR = self.rhs.expand(start_state)
		traceL = self.lhs.expand(start_state)
		
		res= [(["L"] + c,e) for c,e in traceL]
		res.extend([(["R"] + c,e) for c,e in traceR])

		return res
	def eval(self, state, choices):
		choice = choices[0]
		if choice == "R":
			return self.rhs.eval(state, choices[1:])
		elif choice == "L":
			return self.lhs.eval(state, choices[1:])
		else:
			raise Exception("Invalid choice %s for eval Choice. Must be R or L", choice)
	def toString(self, choices=None, level=0):
		choice = choices[0]
		if choice == "R":
			rhs, choices = self.rhs.toString(choices[1:], level)
			ret = choice + rhs + "\n"
			return ret, choices
		elif choice == "L":
			lhs, choices = self.lhs.toString(choices[1:], level)
			ret = choice + lhs + "\n"
			return ret, choices
		else:
			raise Exception("Invalid choice %s for eval Choice. Must be R or L", choice)

class Loop(HP):
	def __init__(self, arg):
		self.arg = arg
	def print(self,level=0):
		print(' '*level+"Loop:")
		self.arg.print(level+1)

class Assign(HP):
	def __init__(self, x, e):
		#x is passed in as a term because of recursion in parseHP so we convert
		# to the underlying string representation here
		self.x = x.arg#string
		#check whether this is a star assignment
		if e.arg[0]=="*":
			self.star=True
			entries=e.arg[e.arg.find("(")+1:e.arg.find(")")].split(",")
			self.range=(Term(entries[0]),Term(entries[1]))
			self.numsamples=int(entries[2])
		else:
			self.star=False
		self.e = e

	def print(self,level=0):
		print(' '*level+"Assign:",self.x,self.e.arg)

	def expand(self, start_state):
		if self.star:
			traces=[]
			for val in np.linspace(self.range[0].eval(start_state),
						self.range[1].eval(start_state),self.numsamples):
				state=start_state.copy()
				choice=f"*({val})"
				state.updateVar(self.x,val)
				traces.append(([choice],state))
			return traces
		else:
			state = start_state.copy()
			state.updateVar(self.x, self.e.eval(state))
			return [([], state)]

	def eval(self, state, choices):
		if self.star:
			assert(choices[0][0]=="*")
			state_c=state.copy()
			state_c.updateVar(self.x, float(choices[0][2:-1]))
			return [state_c],choices[1:]
		else:
			state_c=state.copy()
			state_c.updateVar(self.x, self.e.eval(state_c))
			return [state_c],choices

	def toString(self, choices=None, level=0):
		if self.star:
			return self.x+" := "+choices[0],choices[1:]
		else:
			return self.x+" := "+self.e.arg, choices
	
class Compose(HP):
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	def print(self,level=0):
		print(' '*level + "Compose:")
		self.lhs.print(level+1)
		self.rhs.print(level+1)
	def expand(self, start_state):
		TraceL = self.lhs.expand(start_state)
		res=[]
		for choices, end_state in TraceL:
			TraceR = self.rhs.expand(end_state)
			augmented_traces=[(choices+c,e) for c,e in TraceR]
			res.extend(augmented_traces)
		return res

	def eval(self, state, choices):
		state_list,new_choices = self.lhs.eval(state, choices)
		rhs_start = state_list[-1] if len(state_list)>0 else state
		rhs_states,rhs_choices=self.rhs.eval(rhs_start, new_choices)
		state_list.extend(rhs_states)
		return state_list,rhs_choices
	def toString(self, choices=None, level=0):
		lhs, new_choices = self.lhs.toString(choices, level)
		rhs, rhs_choices = self.rhs.toString(new_choices, level)
		return lhs+"; "+rhs, rhs_choices


class Test(HP):
	def __init__(self, arg):
		self.arg = arg
	def print(self,level=0):
		print(' '*level+"Test:",self.arg.arg)
	def expand(self, start_state):
		if self.arg.eval(start_state):
			return [([], start_state)]
		else:
			return []
	def eval(self, state, choices):
		if self.arg.eval(state):
			return [],choices
		else:
			raise Exception("Test failed in eval. All traces passed passed to eval should pass tests")
	def toString(self, choices=None, level=0):
		return "?"+self.arg.arg, choices

class ODE(HP):
	def __init__(self, stringarg):
		self.stringarg = stringarg#type string
		a=stringarg.find("and")
		if a<0:
			self.constraint=Form("True")
			ode_string=stringarg
		else:
			cons=stringarg[a+3:].strip()
			self.constraint=Form(cons)
			ode_string=stringarg[:a].strip()
		#now parse out the primes
		self.derivs=dict()
		while True:
			#find a prime
			i=ode_string.find("'")
			if i<0:break
			varname=ode_string[:i].strip()
			e=ode_string.find(",")
			if e<0:
				term=Term(ode_string[ode_string.find("=")+1:])
				self.derivs[varname]=term
				break;
			else:
				term=Term(ode_string[ode_string.find("=")+1:e])
				self.derivs[varname]=term
				ode_string=ode_string[ode_string.find(",")+1:]
		assert(len(self.derivs)>0)

	def expand(self,start_state):
		#see if contraint holds now, if it doesnt return no traces
		# pick times to expand for (including 0 time) [0,max]
		if(not self.constraint.eval(start_state)):
			return []
		time_candidates=[1,2,4]
		traces=[([0],start_state)]
		prev_end_t=0
		for t in time_candidates:
			end_time,end_state=integrate_ODE_runge_kutta(self,start_state,t)
			if end_time-prev_end_t<.01:
				break;
			prev_end_t=end_time
			traces.append(([end_time],end_state))
			if(abs(end_time-t)>dt):
				break#we reached a constraint so we shouldnt expand the next one
		return traces


	def eval(self, state, choices):
		choice = choices[0]
		# Strip off the first choice
		if not isinstance(choice, (int, float)):
			raise Exception("Invalid choice for ODE eval. Must be int or float")
		# Return list of states
		return integrate_ODE_runge_kutta(self, state, choice,withSteps=True),choices[1:]
	
		
	def print(self,level=0):
		print(" "*level+"ODE: Derivs: {", end='')
		for d in self.derivs:
			print(d,'=',self.derivs[d].arg,end=' ')
		print("} Constraint: ",self.constraint.arg)

	def toString(self, choices=None, level=0):
		string = '\n'
		
		string += '{'
		for d in self.derivs:
			string += d+'='+self.derivs[d].arg+','
		string += "& "+self.constraint.arg+"}"
		
		if choices is not None:
			choice = choices[0]
			if not isinstance(choice, (int, float)):
				raise Exception("Invalid choice for ODE eval. Must be int or float")
			choices = choices[1:]
			string += ' (Eval for ' + str(round(choice, 2)) + ') '
		return string, choices

if __name__=="__main__":
	form=Form("(x<=0 or x<2 or x<0)")
	state=State()
	state.addVar('x',0)
	print(form.get_heuristic(state))

	# state=State()
	# state.addVar('x', 0)
	# ode = ODE('x\' = 1 and x < 0.5')

	# t, end_state = integrate_ODE(ode, state, 1)
	# print(end_state.vars)
	
