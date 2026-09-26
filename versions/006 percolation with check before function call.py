import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colours
import time

np.random.seed(0) # fixed seed so every run produces the same grids
# grids are made all at once from here on, but the random numbers are used in the same order so they are the same grids as 001-004

n = 20 # the whole relevant bit works with 20x20 grids


def make_grids(N,n,p): # makes all N grids for one p in a single numpy call, True is open and p is the probability of a cell being open
    ## one big call instead of N small ones, as each numpy call has a fixed overhead that is much bigger than making 400 random numbers
    ## each random float in [0,1) below p becomes True, and grids[k] is the k-th grid
    ## uses about 18 MB at N = 5000, much bigger grids would need to be made in chunks
    return np.random.random((N,n,n)) < p


def reaches_bottom(grid, i, j): # fills from cell (i,j) and returns True as soon as the fill reaches the bottom row
    ## only ever called on open, unfilled cells, so no calls are wasted on cells that are already filled
    ## filled cells are set to False in the grid itself so they are never entered again, meaning no separate visited grid is needed
    grid[i][j] = False # marks this cell as filled
    if i == n-1:
        return True # reached the bottom, so no further filling is needed

    ## tries below, right, left, then above, passing a True straight back up if any neighbour reaches the bottom
    ## bounds are checked first so there are no IndexErrors or wraparound, and grid[a][b] is only True if the neighbour is open and unfilled
    if i < n-1 and grid[i+1][j] and reaches_bottom(grid, i+1, j): #check cell below
        return True
    if j < n-1 and grid[i][j+1] and reaches_bottom(grid, i, j+1): #check cell to the right
        return True
    if j > 0 and grid[i][j-1] and reaches_bottom(grid, i, j-1): #check cell to the left
        return True
    if i > 0 and grid[i-1][j] and reaches_bottom(grid, i-1, j): #check cell above
        return True
    return False


def percolates(grid): # seeds the fill from each open, unfilled top cell and returns True as soon as one reaches the bottom
    for i in range(n):
        if grid[0][i] and reaches_bottom(grid, 0, i): # top cells filled by an earlier seed are False too, so they are skipped
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

    grids = make_grids(N,n,p) # all N grids for this p as an (N,n,n) boolean array

    for gridArray in grids: # takes each grid in turn
        grid = gridArray.tolist() # python lists are much faster for reading single cells, converting one grid at a time is quicker and saves memory
        if percolates(grid):
            numberPercolates += 1
    chancePercolates = np.append(chancePercolates,numberPercolates/N) # calculates the probability that each p has a percolating grid and adds it to the list which will be graphed
t2 = time.time()

print(t2-t1) # not necessary but gives perspective on the time taken to go through process on my machine

plt.plot(P,chancePercolates, color = "Blue")
plt.grid()
plt.title("Checking before each call, filling the grid in place")
plt.xlabel("P")
plt.ylabel("C(P)")
plt.figtext(0.99, 0.01, f"Time taken: {t2-t1:.2f} s", ha="right", va="bottom", fontsize=8)
plt.show()
