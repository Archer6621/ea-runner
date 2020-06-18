import subprocess as sp
import concurrent.futures as cf
from pathlib import Path
from itertools import product
import json
import pandas as pd
import re
from datetime import datetime

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generic concurrent EA runner.')
    parser.add_argument('program', type=str, help='Program/command to run (without EA args)')
    parser.add_argument('path', type=str, help='Path to maxcut instances')
    parser.add_argument('workers', type=int, help='Number of concurrent workers')
    parser.add_argument('variants', type=str, help='Variant range to consider, range <start:end>, end is exclusive, or single <value>')
    parser.add_argument('sizes', type=str, help='Size range to consider, range <start:end>, end is exclusive, or single <value>')
    parser.add_argument('repeats', type=int, help='Number of repeats')
    args = parser.parse_args()

    # Collect instances
    from collections import namedtuple
    Instance = namedtuple("Instance", ["path", "size", "variant", "solution"])
    instances = []
    for path in Path(args.path).iterdir():
        if path.suffix==".txt":
            actual_path = str(path.resolve())
            split =  re.split(r"(n|i)", path.stem)
            size = int(split[2])
            variant = int(split[4])

            with open(path.with_suffix(".bkv"), 'r') as f:
                solution = int(f.readlines()[0].strip())

            if ':' in args.variants:
                r = list(map(int, args.variants.split(":")))
            else:
                r_val = int(args.variants)
                r = [r_val, r_val+1]

            if ':' in args.sizes:
                s = list(map(int, args.sizes.split(":")))
            else:
                s_val = int(args.sizes)
                s = [s_val, s_val+1]

            if r[0] <= variant < r[1] and s[0] <= size < s[1]: 
                instances.append(Instance(actual_path, size, variant, solution))

    # Collect parameter tuples
    with open("./params.json", 'r') as f:
        params = json.loads(f.read())
    params["instance"] = instances
    params["run"] = range(args.repeats)
    param_tuples = product(*params.values())

    pool = cf.ProcessPoolExecutor(max_workers=args.workers)
    f2p = {}
    for p in param_tuples:
        #[print(f" -{name:<32}: {value}") for name, value in zip(["instance"] + list(params.keys()), p)]
        program_args = (p[-2].path,) + p[:-2]
        print(f"Queuing `{args.program}` with args:", program_args)
        future = pool.submit(sp.check_output, args.program + " " + " ".join(map(str,program_args)), shell=1)
        f2p[future] = p

    print("Waiting for all jobs to finish...")
    out_columns = ["best", "evaluations"]
    all_columns = out_columns + list(params.keys())

    dataframes = []
    for future in cf.as_completed(f2p.keys()):
        print("Finished job: ", f2p[future])
        # TODO: determine whether all outputs will always be ints?
        outputs = map(int, future.result().decode("utf-8").split(","))
        row = {**dict(zip(out_columns, outputs)), **dict(zip(params.keys(), f2p[future]))}
        instance = row.pop("instance")._asdict()
        instance.pop("path")
        row = {**instance, **row}
        dataframes.append(pd.DataFrame.from_dict([row]))

    fn = f"results_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    print(f"Stored results in {fn}")
    print(pd.concat(dataframes))
    pd.concat(dataframes).to_csv(fn, index=False)
