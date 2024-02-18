# # Computational Mathematics
# ## Project C: Percolation
# ## Due: 19/02/2024





#
# ***
# ### C.1: Representing the state
#

#
# Modules
# 


import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import time
from publish import *

#
# ***
# Question C.1
#

def make_grid(n,p): # for the whole program n represents the size of the nxn grid and p represents the probability of a cell being closed (True is open, False is closed)
    arr = np.random.choice(a=[True,False], size=(n, n), p=[p, 1-p])
    return arr

print(make_grid(4,0.5), end = "\n \n")
print(make_grid(4,0.25), end = "\n \n")
print(make_grid(4,0.25), end = "\n \n") # different resut when called twice
print(make_grid(4,0.75), end = "\n \n") # should be more commonly True than last examples
print(make_grid(4,0), end = "\n \n") # sanity check, none are true
print(make_grid(4,1), end = "\n \n") # all are true

#
# ***
# Question C.2
#

def visualise_grid(grid,n): # simply visualises a given grid and draws gridlines
    plt.clf() # starts on a blnack grid
    plt.imshow(grid, cmap = colours.ListedColormap(["black","white"]))
    axis = plt.gca()
    axis.set_xticks(np.arange(-.5, n, 1), minor=True)
    axis.set_yticks(np.arange(-.5, n, 1), minor=True)
    axis.grid(which="minor", color="black", linewidth=2)
    plt.xticks([])
    plt.yticks([])
    #everything here to do with axes is just adding ticks to create grid lines and then removing their labels so that the resultant image is a grid

n = 5

for i in range(4): #visualises some sample grids
    grid = make_grid(n,0.5) #probability chosen for the sake of example
    print(grid)
    visualise_grid(grid,n)
    plt.show()

#
# ***
# ### C.2: Calculating Percolation
#

#
# Question C.3
# 

def visualise_fill(grid, fillStat,n): #takes the grid and its filled status (whether each cell is full or not) and plots them, black closed, white open empty, blue filled
    plt.clf()
    visualise_grid(grid,n)
    plt.imshow(fillStat, cmap = colours.ListedColormap(["none","Blue"]))


n = 3
grid = [[False,False,True],[True,True,True],[False,True,False]]  #a grid with a few examples for correct and incorrect percolations

fillStat = [[False,False,True],[True,True,True],[False,True,False]]

fillStat2 = [[True,True,False],[True,False,True],[False,True,False]] ## this data does not show correct percolation but i wanted to see if it was drawing over the visualise_grid image, just in case (it does)

fillStatFalse = [[False for i in range(n)] for i in range(n)] ## tests when fillStat is all false 

visualise_grid(grid,n)
plt.show()
visualise_fill(grid,fillStat,n)
plt.show()
visualise_fill(grid, fillStat2,n)
plt.show()
visualise_fill(grid, fillStatFalse,n)
plt.show()

#
# ***
# Question C.4 
#

# fillStat is a global variable (at least relative to this function), that way each update from the function doesnt require it to be returned 
def compute_fill_from_top(grid, i, j): # most of the work is done in this function even though we technically only use it to calculate the fill status in compute_fill
    if fillStat[i,j] == True:
        return # terminates if already visited as reasoned in question
    else:
        fillStat[i,j] = True

        ## recursive part of the function now begins
        ## works as follows
        ## calls itself on the cell below it:
        ## if the cell is not already visited it does this procedure for the cell it is called on
        ## if the cell is already visited that call terminates and it successively moves onto checking the right, left, and then above
        ## after it is finished every cell accessible from the originally called cell will be decided to be true, and all not reachable will be decided as false 
        try: 
            if grid[i+1,j] == True: ##check cell below
                compute_fill_from_top(grid, i+1, j)
        except IndexError: # cant check to the bottom or right if already at the bottom or right hand side, this prevents an error from raising
            pass
        try:
            if grid[i,j+1] == True:
                compute_fill_from_top(grid, i, j+1)
        except IndexError:
            pass
        try:
            if grid[i,j-1] == True:
                if j > 0: # index [-1] = index [n-1] in python so this prevents wraparound caused by that
                    compute_fill_from_top(grid, i, j-1)
        except IndexError:
            pass
        try:
            if grid[i-1,j] == True:
                if i>1:
                    compute_fill_from_top(grid, i-1, j)
        except IndexError:
            pass
    return


fillStat = np.array([[False for i in range(n)] for i in range(n)]) #fillstat also checks for visited, as a full cell is visited and a visited cell is full.
def compute_fill(grid): # compute_fill_from_top must be "seeded" from each top cell, if a cell has already been visited there is no need, however.
    for i in range(n):
        if grid[0,i] == False: # cant start from a closed cell
            continue
        elif fillStat[0,i] == True:
            continue
        else:
            compute_fill_from_top(grid, 0, i)
    return fillStat

#
# ***
# Question C.5
#

def percolates(fillStat): #takes the filled in grid status and determines whether the grid percolates
    percolateTest = False
    if fillStat[n-1].any(): # if any of the bottom entries are True then the grid percolates
        percolateTest = True
    return percolateTest

n = 20  #working with 20x20 grids from now on
for i in range(10): # gives 10 example grids with whether they percolate as the title
    fillStat = np.array([[False for i in range(n)] for i in range(n)]) # initialises fillStat
    grid = make_grid(20,0.6) # creases 20x20 grid p = 0.6
    fillStat = compute_fill(grid) # computes the full cells of the grid
    percolateTest = percolates(fillStat) # decides whether the grid percolates
    visualise_grid(grid,n) # visualises the grid and then the filled in grid with its percolation status, so that it can be seen that the percolation process and graphing is legitimate
    plt.show()
    visualise_fill(grid,fillStat,n)
    if percolateTest:
        plt.title("This grid percolates")
    else:
        plt.title("This grid does not percolate")
    plt.show()
    plt.clf()


#
# ***
# ### C.3: Monte Carlo Simulation
#

#
# ***
# Question C.6
#


N = 5000 # N and P are from the question
chancePercolates = np.array([])
P = np.linspace(0,0.4,20)
P = np.append(P,np.linspace(0.4,0.7,100)) # P is the union of several linspaces, this is so a higher density can be achieved in the central [0.4,0.7] region
P = np.append(P,np.linspace(0.7,1,15)) 

P = np.unique(P)

t1 = time.time()
for p in P:
    numberPercolates = 0 #counts the number of percolating grids from a particular p
    for i in range(N): # takes N sample grids for each p, checks if they percolate, and then increments/doesnt numberPercolates depending on the result
        grid = make_grid(20,p)
        fillStat = np.array([[False for j in range(n)] for j in range(n)]) # initialises fillStat
        fillStat = compute_fill(grid)
        if percolates(fillStat):
            numberPercolates += 1
    chancePercolates = np.append(chancePercolates,numberPercolates/N) # calculates the probability that each p has a percolating grid and adds it to the list which will be graphed
t2 = time.time()

print(t2-t1) # not necessary but gives perspective on the time taken to go through process on my machine

plt.plot(P,chancePercolates, color = "Blue")
plt.grid()
plt.title("Monte Carlo Simulation of grids")
plt.xlabel("P")
plt.ylabel("C(P)")
plt.show()

publish()