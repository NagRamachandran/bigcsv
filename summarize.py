from __future__ import division
import json
import pipes
import multiprocessing
import sys


BLANK = b''


# @profile
def run_length_encode(iterator):
    run_value, run_length = next(iterator), 1
    for value in iterator:
        if value < run_value:
            raise ValueError('unsorted iterator')
        elif value != run_value:
            yield run_value, run_length
            run_value, run_length = value, 1
        else:
            run_length += 1
    yield run_value, run_length


def summarize(iterator):
    num_values = 0
    num_uniques = 0
    num_empty = 0
    max_len = 0
    min_len = sys.maxint
    sum_len = 0

    for run_value, run_length in run_length_encode(line.rstrip(b'\n') for line in iterator):
        if run_value == BLANK:
            num_empty = run_length
        num_values += run_length
        num_uniques += 1
        val_len = len(run_value)
        max_len = max(max_len, val_len)
        min_len = min(min_len, val_len)
        sum_len += val_len * run_length

    return {
        'num_values': num_values,
        'num_fills': num_values - num_empty,
        'fill_ratio': (num_values - num_empty) / num_values,
        'max_len': max_len,
        'min_len': min_len,
        'avg_len': sum_len / num_values,
        'num_uniques': num_uniques,
    }


def sort_and_summarize(path):
    template = pipes.Template()
    template.append('LC_ALL=C sort', '--')
    with template.open(path, 'r') as fin:
        result = summarize(fin)
    return result


def multi_summarize(paths, processes=multiprocessing.cpu_count()):
    pool = multiprocessing.Pool(processes=processes)
    return pool.map(sort_and_summarize, paths)


def main():
    result = summarize(sys.stdin)
    sys.stdout.write(json.dumps(result, sort_keys=True) + '\n')


def main_multi():
    paths = list(sys.argv[1:])
    for path, result in zip(paths, multi_summarize(paths)):
        result['_path'] = path
        sys.stdout.write(json.dumps(result, sort_keys=True) + '\n')


if __name__ == '__main__':
    main_multi()
