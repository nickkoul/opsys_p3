import sys
import operator
import copy

def parse(fname):									#parses first input file and creates a list of Process objects
	arrivals = []									#list of arrival times
	exits = []										#list of exit times
	f = open(fname).read().strip()
	f = f.split("\n")
	for i in range(1, len(f)):
		process = f[i].strip().split(" ")
		times = process[2:]
		for t in times:
			t = t.split("-")						#format of lists is tuple: (arrival/exit time, process name, num frames)
			arrivals.append((int(t[0]), process[0], int(process[1])))
			exits.append((int(t[1]), process[0], int(process[1])))
	#sort both lists, first by arrival/exit times, then by process name	
	arrivals = sorted(arrivals, key=operator.itemgetter(0,1))		
	exits = sorted(exits, key=operator.itemgetter(0,1))
	return [arrivals, exits]						#return both lists		

def printM(memory, formatF):						#prints the memory for the first two parts of the assignment
	f = "="*formatF
	mem = f + "\n"
	count = 0
	for m in memory:
		if count < formatF:
			mem += m
		count += 1
		if count == formatF:
			mem += "\n"
			count = 0
	mem += f
	return mem

def deFragment(memory, time, t_memmove, formatF, arrivals, exits):							#moves all process memory up so that there are no spaces between
	count = 0
	move = False
	firstItem = 0													#record first empty spot
	lastItem = 0													#record last used memory space
	p = []															#list of all processes moved
	for i in range(1, len(memory)):									#fill gaps in memory
		if memory[i-1] == ".":
			if move == False:
				firstItem = i-1
			move = True
			space = i
			while (memory[space] == "."):
				if space == len(memory) - 1:
					break
				space += 1
			if space == len(memory) - 1:
					break
			if memory[space] not in p:
				p.append(memory[space])
			memory[i-1] = memory[space]
			memory[space] = "."
			lastItem = i
	time += t_memmove * (lastItem - firstItem)						#update time
	proc = ""
	for i in range(0, len(p)):
		if i != 0:
			proc += ", " + p[i] 
		else:
			proc += " " + p[i] 
	print "time %dms: Defragmentation complete (moved %d frames: %s)" %(time, lastItem - firstItem, proc)
	print printM(memory, formatF)

	#update all arrival and exit times
	for i in range(0, len(arrivals)):
		newT = arrivals[i][0] + (lastItem - firstItem)
		arrivals[i] = (newT, arrivals[i][1], arrivals[i][2])
	for i in range(0, len(exits)):
		newT = exits[i][0] + (lastItem - firstItem)
		exits[i] = (newT, exits[i][1], exits[i][2])

	return [memory, time, lastItem, arrivals, exits]				#return new memory 



def simulateFirstFit(l, frames, formatF, t_memmove):
	memory = ["."]*frames							#visual of the memory
	arrivals = l[0]
	exits = l[1]
	time = 0
	print "time %dms: Simulator started (Contiguous -- First-Fit)" %(time)
	while (len(exits) != 0):						#while there are still processes using memory
		if len(arrivals) > 0:
			if arrivals[0][0] <= exits[0][0]:
				p = arrivals.pop(0)
				time = p[0]								#update the time
				print "time %dms: Process %s arrived (requires %d frames of physical memory)" %(time, p[1], p[2])
				if (frames < p[2]):						#if there is not enough space for the process, skip
					print "time %dms: Cannot place process %s -- skipping process %s" %(time, p[1], p[1])
					print printM(memory, formatF)
					for i in range(0, len(exits)):		#remove its exit time from the exits list
						if exits[i][1] == p[1]:
							exits.pop(i)
							break
				else:										#add process to memory
					count = 0								#counts how many consecutive spaces there are
					fit = False
					for x in range(0, len(memory)):
						if memory[x] == ".":				#if the memory is free, add one to the count
							count += 1
						else:								#restart the count if it is not free
							count = 0
						if count == p[2]:					#if the process can fit, add it
							print str(x - p[2] + 1) + "-" + str(x + 1)
							for y in range(x-p[2]+1, x + 1):
								memory[y] = p[1]
							print "time %dms: Placed process %s in memory" %(time, p[1])
							print printM(memory, formatF)
							fit = True							#update variable to say that process fit
							frames -= p[2]						#update number of available frames
							break
					if fit == True:
						continue
					else:									#if process can't fit in given spaces, defragment
						print "time %dms: Cannot place process %s -- starting defragmentation" %(time, p[1])
						r = deFragment(memory, time, t_memmove, formatF, arrivals, exits)
						memory = r[0]
						time = r[1]
						index = r[2]
						arrivals = r[3]
						exits = r[4]
						for z in range(index, index + p[2]):
							memory[z] = p[1]
						frames -= p[2]
						print "time %dms: Placed process %s in memory:" %(time, p[1])
						print printM(memory, formatF)
			else:										#process needs to leave memory
				p = exits.pop(0)					#remove all process memory
				time = p[0]
				for i in range(0, len(memory)):
					if (memory[i] == p[1]):				
						memory[i] = "."
				frames += p[2]						#update number of frames
				print "time %dms: Process %s removed from physical memory" %(time, p[1])
				print printM(memory, formatF)
		else:
			p = exits.pop(0)					#remove all process memory
			time = p[0]
			for i in range(0, len(memory)):
				if (memory[i] == p[1]):				
					memory[i] = "."
			frames += p[2]						#update number of frames
			print "time %dms: Process %s removed from physical memory" %(time, p[1])
			print printM(memory, formatF)
	print "time %dms: Simulator ended (Contiguous -- First-Fit" %(time)

#scans for space in memory from most recently added partition
#I made the assumption that after defragmentation, it will not use searchIndex and will put it directly after the moved memory
def simulateNextFit(l, frames, formatF, t_memmove):
	memory = ["."]*frames							#visual of the memory
	arrivals = l[0]
	exits = l[1]
	time = 0
	searchIndex = 0									#index for last placed item
	print "time %dms: Simulator started (Contiguous -- Next-Fit)" %(time)
	while (len(exits) != 0):						#while there are still processes using memory
		if len(arrivals) > 0:
			if arrivals[0][0] <= exits[0][0]:
				p = arrivals.pop(0)
				time = p[0]								#update the time
				print "time %dms: Process %s arrived (requires %d frames of physical memory)" %(time, p[1], p[2])
				if (frames < p[2]):						#if there is not enough space for the process, skip
					print "time %dms: Cannot place process %s -- skipping process %s" %(time, p[1], p[1])
					print printM(memory, formatF)
					for i in range(0, len(exits)):			#remove its exit time from the exits list
						if exits[i][1] == p[1]:
							exits.pop(i)
							break
				else:										#add process to memory
					count = 0								#counts how many consecutive spaces there are
					fit = False
					x = searchIndex
					if searchIndex == len(memory):
						x = 0
					while (True):
						if memory[x] == ".":				#if the memory is free, add one to the count
							count += 1
						else:								#restart the count if it is not free
							count = 0
						if count == p[2]:					#if the process can fit, add it
							for y in range(x-p[2]+1, x + 1):
								memory[y] = p[1]
							searchIndex = x + 1
							print "time %dms: Placed process %s in memory" %(time, p[1])
							print printM(memory, formatF)
							fit = True							#update variable to say that process fit
							frames -= p[2]						#update number of available frames
							break
						x += 1
						if x == len(memory):
							x = 0
						if x == searchIndex:
							break
					if fit == True:
						continue
					else:									#if process can't fit in given spaces, defragment
						print "time %dms: Cannot place process %s -- starting defragmentation" %(time, p[1])
						r = deFragment(memory, time, t_memmove, formatF, arrivals, exits)
						memory = r[0]
						time = r[1]
						index = r[2]
						arrivals = r[3]
						exits = r[4]
						for z in range(index, index + p[2]):
							memory[z] = p[1]
						searchIndex = index + p[2]
						frames -= p[2]
						print "time %dms: Placed process %s in memory:" %(time, p[1])
						print printM(memory, formatF)
			else:										#process needs to leave memory
				p = exits.pop(0)					#remove all process memory
				time = p[0]
				for i in range(0, len(memory)):
					if (memory[i] == p[1]):				
						memory[i] = "."
				frames += p[2]						#update number of frames
				print "time %dms: Process %s removed from physical memory" %(time, p[1])
				print printM(memory, formatF)
		else:
			p = exits.pop(0)					#remove all process memory
			time = p[0]
			for i in range(0, len(memory)):
				if (memory[i] == p[1]):				
					memory[i] = "."
			frames += p[2]						#update number of frames
			print "time %dms: Process %s removed from physical memory" %(time, p[1])
			print printM(memory, formatF)
	print "time %dms: Simulator ended (Contiguous -- Next-Fit)" %(time)

def simulateBestFit(l, frames, formatF, t_memmove):
	memory = ["."]*frames		#visual of the memory
	arrivals = l[0]
	exits = l[1]
	time = 0				#list of spaces in memory where meory can be addec; list of tuples in form (num spaces, beginning index)
	print "time %dms: Simulator started (Contiguous -- Best-Fit)" %(time)
	while (len(exits) != 0):						#while there are still processes using memory
		if len(arrivals) > 0:
			if arrivals[0][0] <= exits[0][0]:
				begIndex = 0
				insert = []	
				p = arrivals.pop(0)
				time = p[0]								#update the time
				print "time %dms: Process %s arrived (requires %d frames of physical memory)" %(time, p[1], p[2])
				if (frames < p[2]):						#if there is not enough space for the process, skip
					print "time %dms: Cannot place process %s -- skipping process %s" %(time, p[1], p[1])
					print printM(memory, formatF)
					for i in range(0, len(exits)):		#remove its exit time from the exits list
						if exits[i][1] == p[1]:
							exits.pop(i)
							break
				else:										#add process to memory
					count = 0								#counts how many consecutive spaces there are
					for x in range(0, len(memory)):
						if memory[x] == ".":				#if the memory is free, add one to the count
							count += 1
						else:								#restart the count if it is not free
							if count >= p[2]:
								insert.append((count, begIndex))
							count = 0
							begIndex = x + 1
						if x == len(memory) - 1:
							if count >= p[2]:
								insert.append((count, begIndex))
					#if the insert list is not empty, add process
					if len(insert) > 0:					#if the process can fit, add it
						insert = sorted(insert, key=operator.itemgetter(0,1))	
						begIndex = insert[0][1]
						print str(begIndex) + "-" + str(begIndex + p[2])
						for y in range(begIndex, begIndex + p[2]):
							memory[y] = p[1]
						print "time %dms: Placed process %s in memory" %(time, p[1])
						print printM(memory, formatF)
						fit = True							#update variable to say that process fit
						frames -= p[2]						#update number of available frames
					else:									#if process can't fit in given spaces, defragment
						print "time %dms: Cannot place process %s -- starting defragmentation" %(time, p[1])
						r = deFragment(memory, time, t_memmove, formatF, arrivals, exits)
						memory = r[0]
						time = r[1]
						index = r[2]
						arrivals = r[3]
						exits = r[4]
						for z in range(index, index + p[2]):
							memory[z] = p[1]
						frames -= p[2]
						print "time %dms: Placed process %s in memory:" %(time, p[1])
						print printM(memory, formatF)
			else:										#process needs to leave memory
				p = exits.pop(0)					#remove all process memory
				time = p[0]
				for i in range(0, len(memory)):
					if (memory[i] == p[1]):				
						memory[i] = "."
				frames += p[2]						#update number of frames
				print "time %dms: Process %s removed from physical memory" %(time, p[1])
				print printM(memory, formatF)
		else:
			p = exits.pop(0)					#remove all process memory
			time = p[0]
			for i in range(0, len(memory)):
				if (memory[i] == p[1]):				
					memory[i] = "."
			frames += p[2]						#update number of frames
			print "time %dms: Process %s removed from physical memory" %(time, p[1])
			print printM(memory, formatF)
	print "time %dms: Simulator ended (Contiguous -- Best-Fit)" %(time)


#THIRD PORTION OF THE ASSIGNMENT
def vParse(vname):
	f = open(vname).read().strip()
	f = f.split(" ")
	return f

def printMem(memory):					#function to print out what is in memory
	mem = "[mem:"
	for p in memory:
		mem += " " + str(p)
	mem += "]"
	return mem

def OPT(pages, frames):
	memory = ["."] * frames
	count = 0
	pfaults = 0
	print "Simulating OPT with fixed frame size of %d" %(frames)
	for i in range(0, len(pages)):
		page = int(pages[i]) 			#current page we are looking at
		if (page in memory):			#if the page is in memory, do nothing
			print "referencing page %d %s" %(page, printMem(memory))
		elif (count != frames):			#if there is space in memory for it, add without victim
			memory[count] = page
			count += 1
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (no victim page)" %(page, printMem(memory))
		else:							#if there is no space for it, find victim	
			victim = [float("inf"), 0]	#[page number, time in future]
			steps = 0
			for m in memory:
				for j in range(i+1, len(pages)):
					steps += 1
					if m == int(pages[j]):
						break
				#if the page in memory will be used later in the future or it is a tie, but it is a lower number, it is the new victim
				if steps > victim[1] or (steps == victim[1] and m < victim[0]):	
					victim = [m, steps]
				steps = 0
			index = memory.index(victim[0])	
			memory[index] = page
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (victim page %d)" %(page, printMem(memory), victim[0])
	print "End of OPT simulation (%d page faults)" %(pfaults)


def LRU(pages, frames):
	memory = ["."] * frames
	count = 0
	pfaults = 0
	print "Simulating LRU with fixed frame size of %d" %(frames)
	for i in range(0, len(pages)):
		page = int(pages[i]) 			#current page we are looking at
		if (page in memory):			#if the page is in memory, do nothing
			print "referencing page %d %s" %(page, printMem(memory))
		elif (count != frames):			#if there is space in memory for it, add without victim
			memory[count] = page
			count += 1
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (no victim page)" %(page, printMem(memory))
		else:							#if there is no space for it, find victim	
			victim = [float("inf"), 0]	#[page number, time in future]
			steps = 0
			for m in memory:
				for j in range(i-1, -1, -1):
					steps += 1
					if m == int(pages[j]):
						break
				#if the page in memory will be used later in the future or it is a tie, but it is a lower number, it is the new victim
				if steps > victim[1] or (steps == victim[1] and m < victim[0]):	
					victim = [m, steps]
				steps = 0
			index = memory.index(victim[0])	
			memory[index] = page
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (victim page %d)" %(page, printMem(memory), victim[0])
	print "End of LRU simulation (%d page faults)" %(pfaults)

def LFU(pages, frames):
	memory = ["."] * frames
	count = 0
	pfaults = 0
	accesses = {}
	print "Simulating LFU with fixed frame size of %d" %(frames)
	for i in range(0, len(pages)):
		page = int(pages[i])
		if (page in memory):			#if the page is in memory, do nothing
			print "referencing page %d %s" %(page, printMem(memory))
		elif (count != frames):			#if there is space in memory for it, add without victim
			memory[count] = page
			count += 1
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (no victim page)" %(page, printMem(memory))
		else:							#if there is no space for it, find victim
			a = sorted(accesses, key=accesses.get)
			index = memory.index(a[0])	
			memory[index] = page
			del accesses[a[0]]
			pfaults += 1
			print "referencing page %d %s PAGE FAULT (victim page %d)" %(page, printMem(memory), a[0])	
		if (page in accesses):
			accesses[page] += 1
		else:
			accesses[page] = 1
	print "End of LFU simulation (%d page faults)" %(pfaults)


if __name__ == "__main__":
	if len(sys.argv) != 3:
		sys.stderr.write("Incorrect number of arguments.\n")
		sys.exit(1)
	fname = sys.argv[1]
	l = parse(fname)
	frames = 16
	formatF = 8
	t_memmove = 1
	simulateFirstFit(copy.deepcopy(l), frames, formatF, t_memmove)
	print
	simulateNextFit(copy.deepcopy(l), frames, formatF, t_memmove)
	print
	simulateBestFit(copy.deepcopy(l), frames, formatF, t_memmove)
	print

	'''
	vname = sys.argv[2]
	pages = vParse(vname)
	frames = 3
	OPT(pages, frames)
	print
	LRU(pages, frames)
	print
	LFU(pages, frames)
	'''
	




