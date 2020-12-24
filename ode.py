import pdb
from state import *
dt=.02

def integrate_ODE_runge_kutta(ode, start_state, maxtime, withSteps=False):
	state = start_state.copy()
	t = 0
	states = [state]
	def f(x):
		#x is the state
		#its a dict
		deriv_state=State()
		for var in ode.derivs:
			varval=ode.derivs[var].eval(x)
			deriv_state.addVar(var,varval)
		return deriv_state

	while t < maxtime:
		# compute derivs by evaluating terms multiplied by time step
		# k1 = dict([(v, d.eval(state)) for v,d in ode.derivs.items()])
		k1 = f(state)
		k2 = f(state + k1.scale(dt*.5))
		k3 = f(state + k2.scale(dt*.5))
		k4 = f(state + k3.scale(dt))
		finalstate = state + (k1+k2.scale(2)+k3.scale(2)+k4).scale(dt/6)
		# check if within domain constraints
		if not ode.constraint.eval(finalstate):
			return (t, state)
		state = finalstate

		# Append State
		if withSteps:
			states.append(state)

		# increment time
		t += dt
	if withSteps:
		return states
	return (t, state)