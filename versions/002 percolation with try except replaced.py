import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import time

np.random.seed(0) # fixed seed so every run produces the same grids

n = 20 # the whole relevant bit works with 20x20 grids

def make_grid(n,p): # for the whole program n represents the size of the nxn grid and p represents the probability of a cell being closed (True is open, False is closed)
    arr = np.random.choice(a=[True,False], size=(n, n), p=[p, 1-p])
    return arr


def compute_fill_from_top(grid, i, j): # most of the work is done in this function even though we technically only use it to calculate the fill status in compute_fill
    if visited[i,j] == True:
        return # terminates if already visited as reasoned in question
    else:
        visited[i,j] = True

        ## recursive part of the function now begins
        ## works as follows
        ## calls itself on the cell below it:
        ## if the cell is not already visited it does this procedure for the cell it is called on
        ## if the cell is already visited that call terminates and it successively moves onto checking the right, left, and then above
        ## after it is finished every cell accessible from the originally called cell will be decided to be true, and all not reachable will be decided as false 
        ## bounds are checked before indexing, so no IndexError can occur and negative indices can't wrap around
        if i < n-1 and grid[i+1,j]: ##check cell below
            compute_fill_from_top(grid, i+1, j)
        if j < n-1 and grid[i,j+1]: ##check cell to the right
            compute_fill_from_top(grid, i, j+1)
        if j > 0 and grid[i,j-1]: ##check cell to the left
            compute_fill_from_top(grid, i, j-1)
        if i > 0 and grid[i-1,j]: ##check cell above
            compute_fill_from_top(grid, i-1, j)
    return


visited = np.array([[False for i in range(n)] for i in range(n)]) # marks which cells the fill has visited (a visited cell is a filled cell, so this is also the fill status)


def compute_fill(grid): # compute_fill_from_top must be "seeded" from each top cell, if a cell has already been visited there is no need, however.
    for i in range(n):
        if grid[0,i] == False: # cant start from a closed cell
            continue
        elif visited[0,i] == True:
            continue
        else:
            compute_fill_from_top(grid, 0, i)
    return visited


def percolates(visited): #takes the filled in grid status and determines whether the grid percolates
    percolateTest = False
    if visited[n-1].any(): # if any of the bottom entries are True then the grid percolates
        percolateTest = True
    return percolateTest

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
        visited = np.array([[False for j in range(n)] for j in range(n)]) # initialises visited
        visited = compute_fill(grid)
        if percolates(visited):
            numberPercolates += 1
    chancePercolates = np.append(chancePercolates,numberPercolates/N) # calculates the probability that each p has a percolating grid and adds it to the list which will be graphed
t2 = time.time()

print(t2-t1) # not necessary but gives perspective on the time taken to go through process on my machine

plt.plot(P,chancePercolates, color = "Blue")
plt.grid()
plt.title("Simple replacement of try/except with if statements")
plt.xlabel("P")
plt.ylabel("C(P)")
plt.figtext(0.99, 0.01, f"Time taken: {t2-t1:.2f} s", ha="right", va="bottom", fontsize=8)
plt.show()