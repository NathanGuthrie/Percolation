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
