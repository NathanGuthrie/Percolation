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
| 005 | All N grids for each `p` generated in one NumPy call | 0.49 s | ~1.6× | ~29× |
| 006 | Check before each call; fill marks the grid itself, `visited` removed | 0.32 s | ~1.4× | ~44× |
| 007 (failed experiment) | Closed-row / open-column pre-check, naive switch at `p = 0.5` | 0.318 s (006: 0.325 s, same session) | ~1.02× (within noise) | ~44× |
| 008 | Padded, flattened grid (built on 006): no bounds checks, one lookup per cell | 0.250 s (006: 0.339 s, same session) | ~1.36× vs 006 | ~60× (est.) |

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

## 005: `005 percolation with new generation.py`

**Change:** instead of generating each grid separately inside the inner loop, all N grids for a given `p` are generated in a single NumPy call at the start of that `p`'s loop.

- **`make_grid(n,p)` was replaced by `make_grids(N,n,p)`**, which returns `np.random.random((N,n,n)) < p`, an `(N, n, n)` boolean NumPy array where `grids[k]` is the k-th grid.
  - `np.random.random((N,n,n))` draws N·n·n floats uniformly from [0, 1).
  - `< p` turns each float into `True` (open) with probability exactly `p`, and `False` (closed) otherwise. This matches the old meaning of `p` as the probability that a cell is **open**. The old `make_grid` comment said "closed", but the code always used open.
  - Edge cases still behave: at `p = 0` no float is `< 0`, so every cell is closed. At `p = 1` every float in [0, 1) is `< 1`, so every cell is open.
- **Main loop:** `grids = make_grids(N,n,p)` is called once per `p`. The inner loop is now `for gridArray in grids:`, which takes one `n×n` NumPy grid at a time.
- **Converting to lists one grid at a time:** each grid is converted with `grid = gridArray.tolist()` just before it is filled, so the fill still runs on Python lists (the 004 step 2 speed-up is kept). Converting the whole `(N,n,n)` array with a single `.tolist()` was also tested:

  | Conversion (one `p`, N = 5000) | Time |
  |---|---|
  | `.tolist()` on the whole batch, then loop | ~16 ms |
  | Loop over the NumPy batch, `.tolist()` each grid (chosen) | ~10 ms |

  Converting one grid at a time was faster, and it also means only one grid's worth of Python lists exists at a time, instead of about 17 MB of lists for all 5,000 grids.
- The code has detailed comments explaining how `make_grids` works, the memory it uses and why each grid is converted separately.
- The plot title is now "Generating all grids for each p at once".

**Why it is faster:** every NumPy call has a fixed setup cost (calling from Python into NumPy, checking arguments and, for `np.random.choice` with `p=`, validating the probabilities and building a cumulative distribution). For a 20×20 grid this setup is much larger than the cost of generating the 400 random numbers. Previously it was paid N = 5000 times per `p`, and now it is paid once. `random() < p` is also a simpler operation than `choice` with probabilities.

| Grid generation (one `p`, N = 5000) | Time |
|---|---|
| 5,000 × `np.random.choice` (001–004) | ~43 ms |
| One `np.random.random((N,n,n)) < p` | ~3.8 ms |

Over the 135 values of `p`, generation drops from about 5.8 s to about 0.5 s of a full N = 5000 run (plus the per-grid `.tolist()`).

**Memory:** more is used, but only a small amount and only for one `p` at a time.
- The temporary float array is N·n·n·8 bytes, about 16 MB. It is freed straight after the `< p` comparison.
- The boolean batch is N·n·n bytes, about 2 MB. It is replaced when the next `p` starts.
- Only one grid's worth of Python lists exists at a time.
- Peak memory is therefore about 18 MB, compared with a few KB before. This doesn't matter at this size. For much larger `n` or `N` (for example 100×100 grids with N = 50,000, about 4 GB of floats), the grids should be generated in chunks, for example 1,000 at a time.

**Surprise: the results are still exact, not just statistically equal.** Batching was expected to change how random numbers are used, so the curve would only match 004 statistically. In fact it matches exactly:
- NumPy's legacy `np.random.choice(a, size, p=...)` works internally by drawing `size` uniform floats with the same generator as `np.random.random` and mapping each one through the cumulative probabilities `[p, 1]`. A float `u` becomes `True` exactly when `u < p`, which is the same test as `make_grids`.
- Five thousand separate calls of size `(20,20)` use the same stream of floats, in the same order, as one call of size `(5000,20,20)`, because NumPy fills arrays in row-major (C) order: grid 0 row by row, then grid 1, and so on.
- So with the same seed, every grid is identical to the grid the old code made.
- This relies on how NumPy's legacy `np.random.choice` is implemented. In principle, rounding in NumPy's cumulative distribution could flip a cell whose float lands exactly on the boundary, but no such case happened in the check below.

**Verification:**
- All 675,000 grids of a full run (135 values of `p` × 5,000), generated the old way (`np.random.choice`, one at a time) and the new way (`np.random.random((N,n,n)) < p`) from `seed(0)`, were compared cell by cell: **0 cells differ**.
- The full simulation at **N = 5000** gave an identical `chancePercolates` array to 004 at all 135 values of `p`. The full-run time went from 13.0 s (004) to 7.8 s (005).
- At N = 300: identical `chancePercolates` again, 0.77 s (004, this run) → 0.49 s (~1.6× faster than 004, ~29× faster than 001).
- A statistical comparison script (z-scores of the difference at each `p`) was prepared in case the results differed. It isn't needed while the grids stay identical, but will be used for any future change that does alter the random sequence.

**Where the time goes now:** grid generation is now small. What remains is mostly the recursive fill in Python (the function calls themselves), the per-grid `.tolist()` and clearing `visited`.

## 006: `006 percolation with check before function call.py`

**Change:** `reaches_bottom` is now only called on cells that are open **and not yet filled**. The separate `visited` grid is removed, and filled cells are marked by setting them to `False` in the grid itself.

**The problem it fixes:** in 005, the fill called `reaches_bottom` on every open neighbour, and the function then checked `visited` and returned `False` straight away if the cell had already been filled. Instrumenting 005 at N = 300 showed:
- 3,339,327 calls to `reaches_bottom` in total
- 1,614,692 of them (**48.4%**) returned immediately because the cell was already visited

In Python the function call itself (setting up a frame, passing arguments, returning) is the expensive part, so nearly half the calls were close to pure waste.

**What changed in the code:**
- **Filling in place:** the first line of `reaches_bottom` is now `grid[i][j] = False`. A filled cell then looks exactly like a closed cell, so no later check will ever enter it again.
- **One lookup per neighbour:** each neighbour check `grid[a][b]` is now `True` only if the neighbour is open **and** not yet filled. The function is therefore only called when it has real work to do, and the check at the start of the function (`if visited[i][j] == True: return False`) is gone.
- **`percolates` simplified** to `if grid[0][i] and reaches_bottom(grid, 0, i): return True`. A top cell already filled by an earlier seed is now `False`, so the separate "closed" and "already visited" checks become a single check.
- **Removed:** the `visited` list of lists, `falseRow`, and the `for row in visited: row[:] = falseRow` clearing loop that ran for every grid.
- **Why overwriting the grid is safe:** each `grid` is a fresh list made by `gridArray.tolist()` for that one fill and is never used again. The NumPy batch `grids` itself is not modified, only the list copy.
- The plot title is now "Checking before each call, filling the grid in place".
- Comments in the code explain all of the above, including why skipping filled cells is safe.

**Why skipping filled cells can't miss a percolation:** when the fill moves from cell A into a neighbour, A's call doesn't end. It waits part-way through its list of neighbours and carries on with the rest when the neighbour's call returns. So when the fill reaches an already-filled cell C by another route, C is either:
1. **finished:** it has already tried every neighbour and everything reachable through them, and none reached the bottom, so going back in would only repeat work that has already failed; or
2. **still in progress** (a call waiting further up the chain): it will try its remaining neighbours once control returns to it.

Either way every neighbour of C gets tried. Put another way, the cells reachable from the top form one connected blob, and the fill only needs to visit each cell of that blob once and check its neighbours to find all of it. This isn't new behaviour: every version since 2024 has skipped visited cells. 006 just makes the check before the call instead of just after it.

**Why the results are exactly the same:** the neighbours are tried in the same order (below, right, left, above) and the same cells are filled in the same order. The only difference is that calls which would have returned `False` immediately are never made.

**Verification:**
- Call count at N = 300 fell from 3,339,327 to **1,724,635**. That is exactly 3,339,327 − 1,614,692, so precisely the wasted calls were removed and nothing else changed.
- The full simulation at **N = 5000** gave an identical `chancePercolates` array to 005 at all 135 values of `p`. Full-run time: 7.6 s (005) → 5.6 s (006).
- At N = 300: identical `chancePercolates` again. 0.45 s (005, this run) → 0.32 s (~1.4× faster than 005, ~44× faster than 001).

**Why it's ~1.4× and not ~2×:** half the calls were removed, but the removed calls were the cheapest ones (a single check and return). The remaining calls do the real work (four neighbour checks and further calls), and there are fixed costs per grid too (`.tolist()`, the loop over the top row).

**Ideas noted for later versions:**
- Replace the recursion with an explicit stack (`while stack:`) to remove Python function-call overhead altogether and the recursion depth limit. It can keep the same fill order, so the results stay exact.
- Skip grids with a completely closed row using one NumPy check on the whole batch. **Tried in 007: correct, but no worthwhile gain.**
- Bigger options: fill all N grids at once with NumPy array operations; compile the fill with Numba; or compute each random grid's percolation threshold once and build the whole curve from N grids in total (which would only match earlier versions statistically).

## 007: `007 percolation with naive check.py` (failed experiment)

**Idea:** some grids can be decided without filling them at all, using one NumPy check on the whole batch:
- **A completely closed row** means nothing can get past that row, so the grid **cannot** percolate.
- **A completely open column** means the fill can go straight down it, so the grid **must** percolate.

Both are logical certainties about a single grid, not assumptions about the curve, so they can never give a wrong answer.

**The "first try" design choice:** closed rows seemed likely to be common only at low `p`, and open columns only at high `p`. As a naive first guess, the test switches over **halfway along the `p` range, at `p = 0.5`**:
- `p < 0.5`: only the closed-row test is run, and those grids add nothing to `numberPercolates`.
- `p ≥ 0.5`: only the open-column test is run, and those grids are counted as percolating straight away.

The switch point was deliberately **not** tuned using knowledge of the curve (for example, where it actually rises). In keeping with the project's "first try" spirit, it is just the midpoint. Because both tests are certainties, the switch point only affects speed, never the results.

**What changed in the code:**
- After `grids = make_grids(N,n,p)`, a pre-check block builds a boolean array `decided` of shape `(N,)`:
  - closed row: `(~grids.any(axis=2)).any(axis=1)`. `grids.any(axis=2)` is `True` for each row with at least one open cell, `~` flips it to "row completely closed", and `.any(axis=1)` asks whether the grid has any such row.
  - open column: `grids.all(axis=1).any(axis=1)`. `grids.all(axis=1)` is `True` for each column where every cell is open, and `.any(axis=1)` asks whether the grid has any such column. These grids are added to `numberPercolates` with `int(decided.sum())`.
- `grids = grids[~decided]` keeps only the undecided grids, and the existing loop fills those as before.
- `numberPercolates/N` is still divided by the full N, because decided grids are counted (or correctly not counted) by the pre-check.
- The plot title is now "Naive closed row / open column pre-check, switching at p = 0.5".
- Comments explain both tests, the switch-over and that this is an experiment.

**Results:**
- **Correct:** the full N = 5000 curve is identical to 006 at all 135 values of `p`, as expected since both tests are certainties.
- **Grids decided by the pre-check:** 82,570 of 675,000 in a full run (**12.2%**).
- **Time, full N = 5000, best of 3:** 006 5.53 s, 007 5.42 s (~2% faster).
- **Time, N = 300, best of 5:** 006 0.325 s, 007 0.318 s (~2% faster). Run-to-run variation within each version was similar in size, so this gain is only just above the noise.

**Why it failed:** 12% of grids skip the fill, but they are exactly the grids the fill already handled almost instantly:
- **Low `p`, closed row:** almost every top cell is closed, and the few open ones hit a dead end within a cell or two. The fill already cost almost nothing.
- **High `p`, open column:** since 003 the fill tries "below" first and stops at the bottom row, so a mostly open grid is solved in about 20 calls going nearly straight down.
- The time is spent on grids in the middle of the curve (roughly `p` = 0.5–0.65), where the fill has to wander. Those grids almost never have a completely closed row or completely open column, so neither test helps where it would matter.
- The pre-check also has its own small cost (about 1 ms per `p` for the NumPy operations and for building `grids[~decided]`), which cancels part of what it saves.

**Conclusion:** the pre-check is correct and harmless, but the ~2% gain isn't worth the extra code. It is left as a documented failed experiment. 006 remains the best "clean" version. Any further real speed-up would need to target the middle-`p` grids, for example an explicit stack instead of recursion, or a fundamentally different method.

**A related earlier measurement** (while deciding whether to try this, N = 300, best of 3): running the closed-row test on every `p` gave 0.320 s, and running both tests on every `p` gave 0.321 s, against 0.316 s for 006. Run everywhere, the tests were slightly slower. The naive `p = 0.5` switch-over at least avoids running a test where it can never succeed, which is why 007 comes out just ahead of 006 instead of just behind.

## 008: `008 percolation with padded grid.py`

**Built on 006**, the best clean version, not on 007: 007's pre-check was a failed experiment and is left out.

**Change:** each grid is surrounded by a border of closed cells and flattened into a single Python list, so the fill needs no bounds checks and each cell is a single lookup.

**Flattening:** a 20×20 grid becomes one list, and cell `(i, j)` becomes index `k = i*W + j`. Its neighbours are `k+W` (below), `k+1` (right), `k-1` (left) and `k-W` (above). `grid[k]` is one list lookup, where `grid[i][j]` is two (fetch the row, then the cell).

**Why flattening on its own isn't enough:** in a plain flat 20×20 list the edges stop behaving:
- **Right edge:** `k+1` from the last cell in a row is the *first cell of the next row*, a silent wrong connection with no error.
- **Left edge:** `k-1` from the first cell in a row is the last cell of the previous row.
- **Top edge:** `k-20` goes negative, and Python's negative indexing wraps round to the bottom of the grid (the same wraparound problem the 2024 code guarded against with `if j > 0`).
- **Bottom edge:** `k+20` runs past the end of the list and raises `IndexError`.

So a flat list without padding would still need checks like `j = k % n; if j < n-1 ...` on every call.

**Padding (the "sentinel" or "ghost cell" trick):** a ring of closed cells is added round every grid, making it `W×W` with `W = n+2 = 22`. Every real cell then has all four neighbours inside the list, and any neighbour off the real grid is a border cell, which is closed. The existing `if grid[m]` check ("open and unfilled") already refuses to enter closed cells, so it refuses the border too. The four bounds checks simply disappear.

```
# # # # # #      O = open, # = closed
# O O # O #      the outer ring is the padding
# # O O O #
# O # O # #
# # # # # #
```

**What changed in the code:**
- New constants, computed once:
  - `W = n+2`: width of a padded row.
  - `bottom = n*W`: index of the first cell of the bottom real row (padded row `n`). The border row below it (row `n+1`) is closed and never entered, so any filled cell with `k >= bottom` is on the real bottom row.
  - `topRow = range(W+1, W+1+n)`: indices of the real cells in the top row (padded row 1, columns 1 to n).
- **`reaches_bottom(grid, k)`** now takes one index instead of `(i, j)`. The bottom check is `k >= bottom` instead of `i == n-1`, and each neighbour check is `grid[k±…] and reaches_bottom(grid, k±…)`, with no `i < n-1`, `j < n-1`, `j > 0` or `i > 0`.
- **`percolates`** loops over `topRow` instead of `range(n)`.
- **Main loop:** after `make_grids`, a single line pads and flattens the whole batch:
  `grids = np.pad(grids, ((0,0),(1,1),(1,1))).reshape(N, W*W)`. `np.pad` adds one layer on each side of the two grid dimensions (not the batch dimension) and fills it with `False` by default. `.reshape(N, W*W)` then turns each padded grid into one row of 484 values. Each grid is still converted with `.tolist()` one at a time, now giving a flat list.
- `make_grids` is unchanged, so the grids (and random numbers) are exactly the same as 001–006.
- The plot title is now "Padded, flattened grid with no bounds checks".

**How much each part contributes** (prototype on the same 40,500 grids as N = 300, best of 3, all with identical percolation counts):

| Version | Time |
|---|---|
| 006 (list of lists, bounds checks) | 0.290 s |
| Flat list, no padding, bounds checks using `k % n` | 0.273 s (~6% faster) |
| Flat list with padding, no bounds checks (008) | 0.224 s (~23% faster) |

Most of the gain comes from removing the bounds checks, which padding makes possible. Flattening on its own helps only a little.

**Also tried: explicit stack instead of recursion.** A padded, flattened fill using a `while stack:` loop took 0.292 s, no faster than 006, so it was not used. Since Python 3.11 function calls have become much cheaper (this machine runs Python 3.13), and managing a stack by hand in Python costs about as much as the calls it replaces.

**Verification:**
- **N = 300, best of 5:** 006 0.339 s, 008 0.250 s (~1.36× faster). Curves identical.
- **Full N = 5000, best of 3:** 006 5.73 s, 008 4.13 s (~1.39× faster). Curves identical at all 135 values of `p`.
- The machine ran about 5% slower in this session than in earlier ones (006 measured 0.339 s here against 0.32 s before), so 008 was always timed against 006 in the same session. Against 001 it is roughly 60× faster, estimated by scaling from 006's earlier ~44×.

**Implementation note:** while creating the file, a scripted edit anchored on the text `N = 5000`, which also appears in a comment inside `make_grids`. That made two bad edits, and the file was then rewritten cleanly from scratch. The final file was checked by running it (identical curves above).

**Remaining idea (a judgement call on the project's spirit):** the 135 values of `p` are independent, so they could be split across the machine's 10 CPU cores with `multiprocessing`. With the grids still generated in the same order the results would stay exact, and a 5–8× speed-up might be expected. But it would be the same code on more hardware rather than better code.
