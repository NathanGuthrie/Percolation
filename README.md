# Speeding up percolation
[note: Oxford changes their computational projects every year, since it is a while since the time of the original project i feel it is safe to upload this without risk of it being used for plagiarism, but if the maths dept has a problem with it, they can feel free to get in touch and i will take it down.]

This is a project from Prelims Maths at Oxford, a Monte-Carlo simulation of the Percolation decision problem. I went back and redid the main computational portion for a roughly 60× speedup more recently, using agentic AI (Claude Code) to implement some of my ideas.

The scope of the use of Coding agents was purely for time saving, all ideas were my own, i ensured at every step that i understood the code, and could have created it myself. Additionally, In accordance with the University exam regulations, all relevant parts, i.e. the original submitted project, are entirely my own work. 

## The problem

The percolation decision problem asks whether, given a random grid of open and closed cells, you can travel from the top of the grid to the bottom travelling exclusively orthogonally through open cells. If so, a grid is said to percolate

The Monte-Carlo Simulation is used to approximate the probability of percolation in a random grid, where each cell has probability p of being open. 

More recently, i set myself the  goal to get an identical result In as fast a time as possible, on the same machine.

## Results
Plotting the probability of percolation against the probability of a cell being open gives a distinct steep sigmoid curve, centred around 0.6. It is an interesting result, and my lecturers at the time noted that this sudden shift in probability is of interest to several fields, an example being mathematical chemistry, where the fast shift can be used to model phase shifts in a substance

more recently, several efficiencies were found for a roughly 60× speedup, Aided by the massive speedup in efficiency which coding agents allow for, I played around with which data structures were used and how, as well as optimising the main recursive function. For example, I was surprised to find that numpy lists were slower than default python lists. This is because They were only being accessed, not editied.
## What's in here

- `original/`: the original code and report (submitted February 2024), and the course's `publish.py`, by Lawrence Mitchell and Patrick Farrell, under the BSD 3-clause licence in `original/LICENSE-publish.txt`.
- `versions/`: versions 001 to 008. For the most part, each makes one major change (usually an improvement) compared to the last, and produces the same output.
- `plots/`: the plot each version produces, with its run time.
- `CHANGELOG.md`: each change, This log was entirely generated and maintained by Claude.

## Running it

From this folder:

```
pip install -r requirements.txt
python3 "versions/008 percolation with padded grid.py"
```

Every file in `versions/` runs the same way. The original also needs `jupytext` and `nbconvert`, and must be run from inside `original/`.

## What's next
I have considered multithreading for generation of random numbers, which would necessarily mean a differeound output. Similarly, I am learning about the Newman-ziff algorithm with much interest, i hope to be able to implement it for a similar (but not identical) result to previous with much improved time efficiency (O(n) rather than O(n^2)).

