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


## each grid is padded with a border of closed cells (making it (n+2)x(n+2)) and flattened into a single list
## cell k then has neighbours k+W (below), k+1 (right), k-1 (left) and k-W (above), and any neighbour off the real grid is a closed border cell
## so the fill can never step off the edge and no bounds checks are needed
W = n+2 # width of a padded row
bottom = n*W # index of the first cell in the bottom real row, any cell k >= bottom that the fill reaches is on the bottom row
topRow = range(W+1, W+1+n) # indices of the real cells in the top row


def reaches_bottom(grid, k): # fills from cell k and returns True as soon as the fill reaches the bottom row
    ## only ever called on open, unfilled cells, filled cells are set to False so they are never entered again
    grid[k] = False # marks this cell as filled
    if k >= bottom:
        return True # reached the bottom, so no further filling is needed

    ## tries below, right, left, then above, passing a True straight back up if any neighbour reaches the bottom
    ## grid[m] is only True if the neighbour is open and unfilled, the border is always closed so there is no need to check bounds
    if grid[k+W] and reaches_bottom(grid, k+W): #check cell below
        return True
    if grid[k+1] and reaches_bottom(grid, k+1): #check cell to the right
        return True
    if grid[k-1] and reaches_bottom(grid, k-1): #check cell to the left
        return True
    if grid[k-W] and reaches_bottom(grid, k-W): #check cell above
        return True
    return False


def percolates(grid): # seeds the fill from each open, unfilled top cell and returns True as soon as one reaches the bottom
    for k in topRow:
        if grid[k] and reaches_bottom(grid, k): # top cells filled by an earlier seed are False too, so they are skipped
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
    grids = np.pad(grids, ((0,0),(1,1),(1,1))).reshape(N, W*W) # adds the closed border to every grid at once and flattens each one, shape (N,W*W)

    for gridArray in grids: # takes each grid in turn
        grid = gridArray.tolist() # a single flat python list, much faster for reading single cells, converting one grid at a time is quicker and saves memory
        if percolates(grid):
            numberPercolates += 1
    chancePercolates = np.append(chancePercolates,numberPercolates/N) # calculates the probability that each p has a percolating grid and adds it to the list which will be graphed
t2 = time.time()

print(t2-t1) # not necessary but gives perspective on the time taken to go through process on my machine

plt.plot(P,chancePercolates, color = "Blue")
plt.grid()
plt.title("Padded, flattened grid with no bounds checks")
plt.xlabel("P")
plt.ylabel("C(P)")
plt.figtext(0.99, 0.01, f"Time taken: {t2-t1:.2f} s", ha="right", va="bottom", fontsize=8)
plt.show()
