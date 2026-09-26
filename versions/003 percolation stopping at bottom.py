import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import time

np.random.seed(0) # fixed seed so every run produces the same grids

n = 20 # the whole relevant bit works with 20x20 grids

def make_grid(n,p): # for the whole program n represents the size of the nxn grid and p represents the probability of a cell being closed (True is open, False is closed)
    arr = np.random.choice(a=[True,False], size=(n, n), p=[p, 1-p])
    return arr


def reaches_bottom(grid, i, j): # fills from cell (i,j) and returns True as soon as the fill reaches the bottom row, so the rest of the grid is never explored
    if visited[i,j] == True:
        return False # terminates if already visited as reasoned in question
    visited[i,j] = True
    if i == n-1:
        return True # reached the bottom, so the grid percolates and no further filling is needed

    ## recursive part of the function now begins
    ## each neighbour is tried in turn (below, right, left, above) and if any of them reaches the bottom the True is passed straight back up the chain of calls
    ## bounds are checked before indexing, so no IndexError can occur and negative indices can't wrap around
    if i < n-1 and grid[i+1,j] and reaches_bottom(grid, i+1, j): #check cell below
        return True
    if j < n-1 and grid[i,j+1] and reaches_bottom(grid, i, j+1): #check cell to the right
        return True
    if j > 0 and grid[i,j-1] and reaches_bottom(grid, i, j-1): #check cell to the left
        return True
    if i > 0 and grid[i-1,j] and reaches_bottom(grid, i-1, j): #check cell above
        return True
    return False


visited = np.array([[False for i in range(n)] for i in range(n)]) # marks which cells the fill has visited (a visited cell is a filled cell, so this is also the fill status)

## Now percolates is a more appropriate name for compute fill, and percolates is unnecessary
def percolates(grid): # seeds reaches_bottom from each open, unvisited top cell and returns whether the grid percolates, stopping at the first seed that reaches the bottom
    for i in range(n):
        if grid[0,i] == False: # cant start from a closed cell
            continue
        elif visited[0,i] == True:
            continue
        elif reaches_bottom(grid, 0, i):
            return True
    return False

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
        if percolates(grid):
            numberPercolates += 1
    chancePercolates = np.append(chancePercolates,numberPercolates/N) # calculates the probability that each p has a percolating grid and adds it to the list which will be graphed
t2 = time.time()

print(t2-t1) # not necessary but gives perspective on the time taken to go through process on my machine

plt.plot(P,chancePercolates, color = "Blue")
plt.grid()
plt.title("Stopping the fill as soon as it reaches the bottom")
plt.xlabel("P")
plt.ylabel("C(P)")
plt.figtext(0.99, 0.01, f"Time taken: {t2-t1:.2f} s", ha="right", va="bottom", fontsize=8)
plt.show()