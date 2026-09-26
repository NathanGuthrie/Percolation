# Speeding up percolation: changelog

This project speeds up the Monte Carlo percolation simulation from the original university assignment (`original/Project C Percolation.py`, Project C, due 19/02/2024). Each numbered file in `versions/` is one version (its plot is in `plots/`), and each version makes one change to the previous one so that its effect on speed can be measured on its own.

## What the simulation does

- A grid of `n × n` cells (`n = 20`) is generated. Each cell is open (`True`) with probability `p` and closed (`False`) otherwise.
- The grid **percolates** if water poured in at the top can reach the bottom row by moving up, down, left or right through open cells.
- For each value of `p` in `P`, `N = 5000` random grids are generated and the fraction that percolate, `C(P)`, is recorded.
- `P` is 135 values made by joining three `linspace`s: 20 points in [0, 0.4], 100 points in [0.4, 0.7] (denser around the critical region) and 15 points in [0.7, 1], with duplicates removed by `np.unique`.
- The plot is `C(P)` against `P`, with the total simulation time shown as a footnote in the bottom-right corner.

## Naming

- `visited` (called `fillStat` in the original assignment) is the boolean grid marking which cells the fill has reached. The name is used from 001 onwards.
- From 003 onwards the fill functions return booleans, so they are named for what they return: `reaches_bottom(grid, i, j)` (was `compute_fill_from_top`) returns whether a fill from that cell reaches the bottom row, and `percolates(grid)` (was `compute_fill`) returns whether the grid percolates. 001 and 002 keep `compute_fill_from_top` and `compute_fill`, because there they really do compute the fill.

## How versions are compared

- Every version sets `np.random.seed(0)` at the top, so every run generates exactly the same sequence of grids. As long as a change doesn't alter how random numbers are drawn, two versions must produce **identical** curves. Any difference in the curve would mean a bug.
- Equivalence is checked by running two versions one after the other with `N` reduced to 300 (all 135 values of `p`, so 40,500 grids each) and comparing the `chancePercolates` arrays element by element.
- The timings below come from those N = 300 runs on the same machine, so they are relative comparisons and not the full N = 5000 times. The full-run times are in the footnote of each version's plot.
- To reproduce a plot, run the whole file from scratch (for example `python3 "versions/003 percolation stopping at bottom.py"`). If you run only selected lines, or run two files in the same Python session without re-running the seed line, the random sequence is different and so is the curve.

## Timing summary (N = 300)

| Version | Change | Time | Speed-up vs previous | Speed-up vs 001 |
|---|---|---|---|---|
| 001 | Original code, demos stripped, seeded | 14.1 s | n/a | 1.0× |
| 002 | `try/except IndexError` → bounds-checked `if` | 7.9 s | ~1.8× | ~1.8× |
| 003 | Stop filling as soon as the bottom row is reached | 2.9 s | ~2.7× | ~4.8× |
| 004 (step 1) | `visited` as one NumPy array reused and cleared with `.fill(False)` | 2.3 s | ~1.2× | ~6.1× |
| 004 (step 2, current) | `grid` and `visited` as plain Python lists of lists | 0.74 s | ~3.1× vs step 1 | ~19× |

---

## `original/`: the original assignment

The code as submitted. It includes all of questions C.1–C.6: examples of `make_grid`, grid visualisation (`visualise_grid`, `visualise_fill`), ten example percolation plots and the Monte Carlo simulation. It also imports and calls `publish` from the course's `publish.py` helper module (also in `original/`), which runs the script and renders it to `Project C Percolation.html`, the report that was marked. These files are kept exactly as submitted and are not changed.

## 001: `001 original percolation.py`

**Goal:** a minimal, runnable copy of just the Monte Carlo part of the original, to use as the baseline.

Changes from the original assignment:

- **Removed everything that wasn't needed for the simulation:** the C.1 `make_grid` examples, `visualise_grid`, `visualise_fill` and the C.2–C.5 demo plots. None of the simulation depends on them.
- **Moved `n = 20` to the top of the file.** In the original, `n` was reassigned several times (4, 5, 3, 20) as the demos ran and was 20 by the time the simulation started. Setting it once at the top gives the same result.
- **Removed `from publish import *` and the `publish()` call.** `publish.py` isn't next to the versions (it lives in `original/`) and isn't needed for the simulation, so the import would have stopped the script with `ModuleNotFoundError`.
- **Removed the unused `import random`.** All randomness comes from `np.random.choice`.
- **Added `np.random.seed(0)`** so every run produces the same grids and later versions can be checked exactly against this one.
- **Added the time taken to the plot** as a footnote using `plt.figtext`, formatted to 2 decimal places.
- **Changed the plot title** to "Naive simulation from a valiant uni attempt".

The algorithm is unchanged: `make_grid`, `compute_fill_from_top`, `compute_fill`, `percolates`, `N`, `P` and the simulation loop are copied exactly.

### Algorithm as it stands in 001 (the baseline)

- `visited` is a global `n × n` boolean array that marks which cells have been filled (visited). The main loop resets it before each grid.
- `compute_fill(grid)` loops over the top row and calls `compute_fill_from_top(grid, 0, j)` for every open top cell that hasn't already been filled.
- `compute_fill_from_top` is a recursive depth-first flood fill. It marks the cell as filled, then tries the neighbours in the order below, right, left, above.
- Each neighbour check is wrapped in `try/except IndexError`, so stepping off the bottom or right edge is caught as an exception. Stepping off the left or top edge doesn't raise an error (Python's `-1` index wraps round to the other side), so extra `if j > 0` / `if i > 1` checks handle those.
- After the flood fill has **filled the whole reachable region**, `percolates(visited)` checks whether any cell in the bottom row is filled.

### Known quirks carried over from the original (not bugs in the output)

- The move up uses `if i > 1` where it should be `i > 0`, so the fill can never step up into row 0. This doesn't change results, because every open cell in row 0 is already a starting point in `compute_fill`.
- The comment on `make_grid` says `p` is the chance a cell is *closed*, but the code uses `p` as the chance a cell is *open*.
- Each `try` block covers the recursive call as well as the neighbour lookup, so an `IndexError` raised deeper in the recursion would be silently ignored. Nothing currently raises one, but it could hide bugs.
- The largest possible recursion depth is `n² = 400`, which is under Python's default limit of 1000. Grids much bigger than 20×20 would hit `RecursionError`.
- `visited` is a global that the main loop rebinds. This works, but it will get in the way of vectorising or parallelising.

## 002: `002 percolation with try except replaced.py`

**Change:** replaced the four `try/except IndexError` blocks in `compute_fill_from_top` with bounds checks made before indexing.

```python
if i < n-1 and grid[i+1,j]:   # below
    compute_fill_from_top(grid, i+1, j)
if j < n-1 and grid[i,j+1]:   # right
    compute_fill_from_top(grid, i, j+1)
if j > 0   and grid[i,j-1]:   # left
    compute_fill_from_top(grid, i, j-1)
if i > 0   and grid[i-1,j]:   # above
    compute_fill_from_top(grid, i-1, j)
```

**Why it is faster:**
- Raising and catching an exception in Python is expensive compared with a simple integer comparison. The old code raised an `IndexError` every time the fill touched the bottom or right edge.
- The old code read `grid[i, j-1]` and `grid[i-1, j]` before checking whether the index was valid. Now `and` stops as soon as the bounds check fails, so the grid is only read for valid neighbours.
- Setting up a `try` block on every neighbour check also has a small cost, and that is gone too.

**Other details:**
- The same `if` checks now handle negative-index wraparound on the left and top edges, so the separate `j > 0` / `i > 1` workarounds are gone.
- The `i > 1` quirk is corrected to `i > 0`. As explained under 001, this doesn't change the output.
- `== True` comparisons in the neighbour checks were dropped because the grid values are already booleans.
- Neighbours are still checked in the same order (below, right, left, above).
- The plot title is now "Simple replacement of try/except with if statements".

**Verification:**
- The two versions of `compute_fill` gave identical fill patterns on 5,000 random 20×20 grids.
- The full simulation at N = 300 gave an identical `chancePercolates` array to 001 at all 135 values of `p`.
- Time: 14.1 s → 7.9 s (~1.8× faster).

## 003: `003 percolation stopping at bottom.py`

**Change:** the fill stops as soon as it reaches the bottom row, instead of filling the whole reachable region and checking the bottom row afterwards. The old `percolates(visited)` function has been removed, and the two fill functions are renamed to say what they now return (see below).

- `compute_fill_from_top` is renamed `reaches_bottom(grid, i, j)` and now returns a boolean:
  - It returns `False` straight away if the cell was already visited.
  - Otherwise it marks the cell as filled. If the cell is in the bottom row (`i == n-1`), it returns `True`, because the grid percolates.
  - Otherwise it tries the neighbours in the same order (below, right, left, above). Each check has the form `bounds and grid[...] and reaches_bottom(...)`, so as soon as a recursive call returns `True`, this call returns `True` without trying the remaining neighbours. The `True` is passed all the way back up the chain of calls.
  - If no neighbour reaches the bottom, it returns `False`.
- `compute_fill` is renamed `percolates(grid)` and now returns whether the grid percolates, not `visited`. It still starts a fill from each open, unvisited top cell, but returns `True` as soon as one of them reaches the bottom. It returns `False` if none do.
- The old `percolates(visited)` function is deleted. The main loop is now `if percolates(grid): numberPercolates += 1`.
- The plot title is now "Stopping the fill as soon as it reaches the bottom".

**Why it is faster:** for high `p`, almost every grid percolates and most cells are open. Previously the whole connected region (often most of the 400 cells) was flooded before the bottom row was checked. Now the fill tries "below" first, so it usually goes nearly straight down and stops after only about `n` cells. Grids that don't percolate still have to explore everything reachable, so there is less saving at low `p`.

**Side effect:** `visited` now only holds the cells visited before the fill stopped, not the whole filled region. That's fine for the simulation, but `visited` can no longer be used to draw the fully filled grid.

**Minor leftover:** the `i < n-1` check on the "below" neighbour can never be false now, because bottom-row cells return before reaching it. It is harmless and was left in.

**Verification:**
- The full simulation at N = 300 gave an identical `chancePercolates` array to 002 at all 135 values of `p`.
- Time: 7.9 s → 2.9 s (~2.7× faster than 002, ~4.8× faster than 001).

## 004: `004 percolation with fast grid setup.py`

Version 004 was built in two steps. Step 1 is kept below for reference. Step 2 is the current state of the file.

### Step 1: `visited` as a reused NumPy array (superseded by step 2)

**Change:** replaced the per-grid list comprehension with a single NumPy boolean array that is created once and cleared in place for each new grid.

- **Before (001–003):** for every one of the 675,000 grids in a full run, a new array was built with `np.array([[False for j in range(n)] for j in range(n)])`. That creates a 20-element Python list 20 times (400 Python `False` objects), and NumPy then has to inspect that nested list to work out its shape and type before copying it into an array.
- **After:** `visited = np.zeros((n,n), dtype=bool)` is created once at module level. Inside the main loop, `visited.fill(False)` resets it in place. This is a single C-level memory write over 400 bytes, with no new array created and no Python lists built.
- The previous line at module level, `visited = np.array([[False ...]])`, which was rebound in the loop anyway, is now the one real allocation.
- The plot title is now "Fast visited grid setup".

**Options benchmarked** (time for one 20×20 all-False grid, `timeit`, 200,000 repeats):

| Method | Time per call |
|---|---|
| `np.array([[False for j in range(n)] for j in range(n)])` (old) | ~11.9 µs |
| `np.full((n,n), False)` | ~0.35 µs |
| `v[:] = False` (reuse existing array) | ~0.15 µs |
| `np.zeros((n,n), dtype=bool)` (new array each time) | ~0.11 µs |
| `v.fill(False)` (reuse existing array) | **~0.06 µs** (chosen) |

`np.zeros` would have given nearly all the benefit. Reusing one array with `.fill(False)` is about twice as fast again and avoids creating an array for every grid, so that was chosen.

**Why the saving is modest:** about 12 µs is saved per grid. Over the 40,500 grids of the N = 300 test that's roughly 0.5 s, which is what was measured. Over the 675,000 grids of a full N = 5000 run it's roughly 8 s. Most of the remaining time is now in the recursive fill itself and in `make_grid`.

**Caveat:** because `visited` is now one shared array reused for every grid, it must be cleared before each call to `percolates`. The `visited.fill(False)` line in the main loop must stay directly before it.

**Verification:**
- The full simulation at N = 300 gave an identical `chancePercolates` array to 003 at all 135 values of `p`.
- Time: 2.8 s (003, on this run) → 2.3 s (~1.2× faster than 003, ~6.1× faster than 001).

### Step 2: plain Python lists instead of NumPy arrays (current)

**Change:** `grid` and `visited` are now ordinary Python lists of lists, and every cell access uses `[i][j]` instead of `[i,j]`.

- **`make_grid`** still generates the grid with `np.random.choice`, exactly as before, so the random sequence and the grids are unchanged. It now returns `arr.tolist()`, a list of 20 lists of 20 Python `bool`s.
- **`visited`** is now `[[False]*n for _ in range(n)]`, created once at module level. A second list `falseRow = [False]*n` is also created once.
- **Resetting `visited`** for each grid: the main loop runs `for row in visited: row[:] = falseRow`, which overwrites each row in place with a copy of `falseRow`. As in step 1, this avoids creating new lists for every grid, and it must stay directly before `percolates(grid)`.
- **Indexing:** in `reaches_bottom` and `percolates`, all `grid[a,b]` / `visited[a,b]` became `grid[a][b]` / `visited[a][b]`.
- The plot title is now "Python lists instead of numpy arrays for the fill".

**Why it is faster:** NumPy is fast for operations on whole arrays, which run in C. The recursive fill instead reads and writes **one cell at a time from Python**, thousands of times per grid. For every single-element access, NumPy has to parse the index tuple, check bounds, work out the memory offset and wrap the result in a new NumPy scalar object (`np.bool_`). A Python list lookup just returns a pointer to an object that already exists (`True` or `False`). The truth tests in the `if` checks are also cheaper on Python `bool`s than on `np.bool_`. Across the whole run these savings add up to much more than the one-off cost of `.tolist()`.

**Costs benchmarked** (single 20×20 grid, `timeit`, 200,000 repeats):

| Operation | Time per call |
|---|---|
| `a.tolist()` (convert a NumPy grid to lists) | ~1.3 µs |
| `[[False]*n for _ in range(n)]` (new visited list) | ~0.84 µs |
| `for r in v: r[:] = F` (clear existing visited list in place, chosen) | ~0.74 µs |

Clearing the lists takes longer than NumPy's `.fill(False)` (~0.06 µs), and `.tolist()` adds ~1.3 µs per grid. Both are small next to the time saved on the tens to hundreds of cell accesses each fill makes.

**Verification:**
- The full simulation at N = 300 gave an identical `chancePercolates` array to step 1 (NumPy `visited`) at all 135 values of `p`. The grids are still generated by the same `np.random.choice` calls, so the results are exact, not just statistically equal.
- Time: 2.3 s (step 1) → 0.74 s (~3.1× faster than step 1, ~19× faster than 001).

**Ideas noted for later versions:**
- **Done in 005:** generating all N grids for each `p` in one call. This was expected to change the random sequence, but it turned out not to (see 005).
