# Evolutionary Algorithm Runner (for MAXCUT instances)
Multi-processing evolutionary algorithm runner. Will take the carthesian product of all its input parameters times the amount of repeats, and will run them on as many processes as specified simultaneously.

## Requirements
- Python 3.6+
- pandas: `pip install pandas`


## Usage

### Interface
The algorithm must satisfy the following input/output interface:
```
Input:  <path_to_instance> <all other params...>
Output: <best_found>, <evaluations>
```
So basically, as long as it accepts the instance path first (only the path to the `.txt` file), it will work fine.

### Help
The help provided by the python script itself
```
positional arguments:
  program     Program/command to run (without EA args)
  path        Path to maxcut instances
  workers     Number of concurrent workers
  variants    Variant range to consider, range <start:end>, end is exclusive,
              or single <value>
  sizes       Size range to consider, range <start:end>, end is exclusive, or
              single <value>
  repeats     Number of repeats
```

### Parameter specification
The parameters for the algorithm can be specified in a file located in the same folder as the runner, called `params.json`.

It looks like this for my own algorithm:
```json
{
	"n" : [2048],	
	"max_evaluations" : [100000],
	"w" : [1.0],
	"c1" : [2.0],
	"c2" : [2.0],
	"greedy_init" : [1, 0]
}
```

The runner will take the carthesian product between all these lists, and feed the arguments to the algorithm command in the same order as they appear in the json file. It runs all these combinations for every eligible instance (with the right size and variant number) on the instance path. Naturally, if every list contains just one element, there will only be one combination. In this specific case for my algorithm, it will run it with greedy initialization and without, for each eligible instance, times the number of repeats.

### Usage Example
This is an example for my own algorithm.

Command: `runner.py "python ../pyswarms_maxcut.py" "..\maxcut\set0b" 12 0:5 0:2000 10`

It will run the command `python ../pyswarms_maxcut.py`, and give it MAXCUT instances in the folder `..\maxcut\set0b`. It will run on 12 processes simultaneously, and pick graph variants 0, 1, 2, 3 and 4. It will pick all instances with graph sizes between 0 to 2000, and it run each individual instance 10 times. So per instance size, we will have 5 * 10 runs.


## Output

It will output a `.csv` file, with the following columns:
```
size,                        size of instance
variant,                     instance variant number
solution,                    best known solution
best,                        best found solution by algorithm so far
evaluations,                 evaluations needed to reach this solution
...
<algorithm parameters>       parameters fed to the algorithm in order, excluding instance path
...
run                          the number of the run for these parameters (for the repeats)
```

This can easily be loaded using pandas, and plotted using seaborn (will automatically plot errors):
```python
import pandas as pd
import seaborn as sns

df = pd.read_csv(r"C:\path\to\results\results.csv")
df['Optimum Reached'] = df.solution==df.best          # Creates a column indicating whether optimum was reached
sns.lineplot(x="size", y="Optimum Reached", data=df)  # Plots instance size vs convergence rate
```

To get seaborn:  `pip install seaborn`
