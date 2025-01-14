from __future__ import division
import math
import random
import basicvirtual

def Idx(time, p , due_dates, wt):				# define the ordering index for ATC rule
	n = len(p)
	Idx_value = []
	average = sum(p)/n
	for j in xrange(n):
		Idx_value.append(wt[j]/p[j]*math.exp(-max(due_dates[j]-p[j]-time,0)/2/average))
	return Idx_value

def Idx_c(time, p, s , due_dates, wt,k_1,k_2):		# define the ordering index for ATCS rule
	n = len(p)
	Idx_value = []
	average_p = sum(p)/n
	average_s = sum(s)/n
	for j in xrange(n):
		Idx_value.append(wt[j]/p[j]*math.exp(-max(due_dates[j]-p[j]-time,0)/k_1/average_p - s[j]/k_2/average_s))
	return Idx_value

def estimate(m,items):					# estimate parameters for k_1 & k_2
	n = len(items)
	p = [items[j].process for j in xrange(n)]
	s = [items[j].setup for j in xrange(n)]
	d = [items[j].due for j in xrange(n)]
	c_max = (sum(p) + sum(s))/m
	tau = 1 - sum(d)/(n*c_max)
	eta = sum(s)/sum(p)
	R = (max(d) - min(d))/c_max
	if R <= 0.5:
		k_1 = 4.5 + R
	else:
		k_1 = 6-2*R
	k_2 = tau/(2*math.sqrt(eta))
	return k_1,k_2

def poisson(alpha):					# generate the poisson distribution var
	n = 0
	P = random.random()
	while P >= math.exp(-alpha):
		r = random.random()
		P = P*r
		n+=1
	N = n
	return N

def release(n,alpha):					# generate the item release time
	r = [poisson(alpha)]
	for j in xrange(1,n):
		a = poisson(alpha)
		temp = a + r[-1]
		r.append(temp)
	random.shuffle(r)
	return r

def process(n):						# generate the job process time
	q = [None]*n
	for i in xrange(n):
		q[i] = poisson(5)
	return q

def setup(n):						# generate the itme setup time
	s = [None]*n
	for j in xrange(n):
		s[j] = random.randrange(1,10)
	return s

def jobstep(n,a,b):					# generate the step of a job needs
	step = [random.randrange(a,b)]
	for j in xrange(1,n):
		step.append(random.randrange(a,b))
	return step

def TL_update(TL,from_same,from_diff,S):		# update the Tabu list in case of over-tabu
	Same = from_same[:]
	Diff = from_diff[:]
	if from_same:
		for s in from_same:
			job = list(s)
			a,b = job[0],job[1]
			if find_job(a,S) != find_job(b,S):
				Same.remove(s)
				TL[TL.index(s)] = None
	if from_diff:
		for s in from_diff:
			job = list(s)
			a,b = job[0],job[1]
			if find_job(a,S) == find_job(b,S):
				Diff.remove(s)
				TL[TL.index(s)] = None
	return TL,Same,Diff

def itemjobs(n,a,b):					# generate the number of jobs that a item needs
	n_job = [random.randrange(a,b)]
	for j in xrange(1,n):
		n_job.append(random.randrange(a,b))
	return n_job

def processtime(n,q):					# calculate the item process time
	m = len(q)
	c = [None]*n
	d= []
	for k in xrange(n):
		c[k] = (k+1)*q[0]
	for i in xrange(1,m-1):
		c[0] = c[0] + q[i]
		for k in xrange(1,n):
			c[k] = max(c[k],c[k-1])+q[i]
	return int(c[-1]/500)

def due_date_r(r,p):					# generate the job due dates with release time
	n = len(r)
	d = [None]*n
	for j in xrange(n):
		delta = int(p[j]/3)
		d[j] = r[j] + 2*p[j] + random.randrange(-delta,delta)
	return d

def weights(n,init):					# generate the weights for Tardiness and Completion, just input the initial value
	w  = [init]
	for j in xrange(1,n):
		w.append(random.randrange(1,2*init))
	random.shuffle(w)
	return w

def late(complete_time,items):				# define the Lateness
	n = len(complete_time)
	lateness = []
	for j in xrange(n):
		item = items[j]
		lateness.append(complete_time[j] - item.due)
	return lateness

def tard(lateness):					# define the Tardiness
	if type(lateness) == int:
		lateness = [lateness]
	n = len(lateness)
	tardiness = []
	for j in xrange(n):
		temp = max(lateness[j],0)
		tardiness.append(temp)
	return tardiness

def early(lateness):					# define the Earliness
	if type(lateness) == int:
		lateness = [lateness]
	n = len(lateness)
	earliness = []
	for j in xrange(n):
		temp = max(-lateness[j],0)
		earliness.append(temp)
	return earliness

def initialization(items,n,m):				# generate initial solution for model 1
	J = range(n)
	S = []
	a = []
	tl = []
	L = []
	c = [None]*n
	for l in xrange(m):
		S.append([])
		a.append(0)
		tl.append(0)
	t = 0
	while J:
		if 0 in a:
			l_star = a.index(0)
			p,d,wt = [],[],[]
			for j in J:				
				item = items[j]
				p.append(item.process)
				d.append(item.due)
				wt.append(item.wt)
			orderidx = Idx(t,p,d,wt)
			j_star = J[orderidx.index(max(orderidx))]
			S[l_star].append(j_star)
			J.remove(j_star)
			L.append(j_star)
			tl[l_star] = t + items[j_star].process
			c[j_star] = tl[l_star]
			a[l_star] = 1
		else:
			t_star = min(tl)
			for l in xrange(m):
				if tl[l] == t_star:
					a[l] = 0
			t = t_star
	return S,L,c

def initialization_c(items,n,m):				# generate initial solution for model 2
	J = range(n)
	S = []
	a = []
	tl = []
	L = []
	c = [None]*n
	f = [None]*n	
	k_1,k_2=estimate(m,items)
	for l in xrange(m):
		S.append([])
		a.append(0)
		tl.append(0)
	t = 0
	while J:
		if 0 in a:
			l_star = a.index(0)
			p,r,s,d,wt = [],[],[],[],[]
			for j in J:
				item = items[j]
				p.append(item.process)
				r.append(item.release)
				s.append(item.setup)
				d.append(item.due)
				wt.append(item.wt)
			orderidx = Idx_c(t, p, s, d, wt,k_1,k_2)
			j_star = J[orderidx.index(max(orderidx))]
			S[l_star].append(j_star)
			J.remove(j_star)
			L.append(j_star)
			if len(S[l_star]) == 1:
				f[j_star] = max(items[j_star].release - items[j_star].setup,0)
			else:
				f[j_star] = max(items[j_star].release - items[j_star].setup - c[S[l_star][S[l_star].index(j_star) -1]],0)
			tl[l_star] = t + items[j_star].process + items[j_star].setup + f[j_star]
			c[j_star] = tl[l_star]
			a[l_star] =1
		else:
			t_star = min(tl)
			for l in xrange(m):
				if tl[l] == t_star:
					a[l] = 0
			t = t_star
	return S,L,c,f

def H(item_values,S):					# define the line contribution value
	line_values = [item_values[j] for j in S]
	value = sum(line_values)
	return value

def Goal(completion,items,S,lambda1,lambda2):	# calculate the object function value
	lateness = late(completion,items)
	Rb,c_max = balance_rate(completion,S)
	Ru = idle_rate(items,completion,c_max,S)
	line_values = []
	l = 0
	for s in S:
		left = [math.fabs(items[j].wt*lateness[j]) for j in s]
		right = [items[j].wc*completion[j] for j in s]
		line_values.append(lambda1*sum(left)/Ru[l] + lambda2*math.exp(-Rb)*sum(right))
		l +=1
	return line_values,sum(line_values)

def reorder(items,S,line_values,item_values):		# find the lines to reorder its items
	l_p = line_values.index(max(line_values))
	l_m = line_values.index(min(line_values))
	s_p = S[l_p]
	s_m = S[l_m]
	temp_value = [item_values[j] for j in s_p]
	j_star = s_p[temp_value.index(max(temp_value))]
	s_p.remove(j_star)
	s_m.append(j_star)
	return l_p, l_m

def innerswap(S,id1,id2):				# swap items for inner line
	K = S[:]
	temp = K[id1]
	K[id1] = K[id2]
	K[id2] = temp
	return K

def pairsets(S):						# define the neighbot pair sets
	pair = []
	n = len(S)
	for i in xrange(n-1):
		pair.append(set([S[i],S[i+1]]))
	return pair

def changewise(set_1,set_2):				# set_1 is the changed set while set_2 is not
	newset = (set_1|set_2) - (set_1&set_2)
	return newset

def pairsets_update(pairs,change_set):			# renew the pair sets for prograssing
	idx = pairs.index(change_set)
	n = len(pairs)
	if n != 1:
		if idx == 0:
			pairs[1] = changewise(pairs[0],pairs[1])
		elif idx == n-1:
			pairs[-2] = changewise(pairs[-1],pairs[-2])
		else:
			pairs[idx-1] = changewise(pairs[idx],pairs[idx-1])
			pairs[idx+1] = changewise(pairs[idx],pairs[idx+1])

def find_job(job,S):					# to find the job scheduled line
	n = len(S)
	for l in xrange(n):
		if job in S[l]:
			l_star = l
	return l_star

def verify(S,items,lambda1,lambda2):			# this function is to verify if the algorithm is right, also can use it to generate value in a silly way ^_^
	n = len(items)
	completion = [None]*n
	for s in S:
		t = 0
		for j in s:
			t += items[j].process
			completion[j] = t
	lateness = late(completion,items)
	tardiness = tard(lateness)
	item_values = []
	for j in xrange(len(items)):
		item = items[j]
		wt,wc = item.wt,item.wc
		t,c = tardiness[j],completion[j]
		value = basicvirtual.h(t,c,wt,wc,lambda1,lambda2)
		item_values.append(value)
	return completion,tardiness,item_values

def balance_rate(completion,S):			# calculate the balance rate for model 2
	c_max = []
	for s in S:
		c_max.append(completion[s[-1]])
	m = len(c_max)
	Rb = sum(c_max)/(m*max(c_max))
	return Rb,c_max

def idle(items,completion,S):				# generate item free time
	n = len(items)
	item_free = [None]*n
	for s in S:
		k = 0
		for j in s:
			if k == 0:
				item_free[j] = max(items[j].release - items[j].setup,0)
			else:
				i = s[k-1]
				item_free[j] = max(items[j].release - items[j].setup - completion[i] ,0)
			k+=1
	return item_free

def idle_rate(items,completion,c_max,S):		# calculate the idle rate
	item_free = idle(items,completion,S)
	Ru = []
	l = 0
	for s in S:
		v = [item_free[j] for j in s]
		Ru.append(1 - sum(v)/c_max[l])
		l += 1
	return Ru