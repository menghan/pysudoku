#!/usr/bin/env python
# coding=utf-8

import collections
import multiprocessing

def hotspot_profile(f):
    def func(*args, **kwargs):
        import os
        import hotshot
        import hotshot.stats
        path = '/tmp/solve-puzzle-%s.prof' % os.getpid()
        prof = hotshot.Profile(path)
        rv = prof.runcall(f, *args, **kwargs)
        prof.close()
        stats = hotshot.stats.load(path)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
        return rv
    return func


def get_bit_count(v):
    r = 0
    while v:
        if v & 1 == 1:
            r += 1
        v >>= 1
    return r


square_base = [0, 0, 0, 3, 3, 3, 6, 6, 6]


class Puzzle(object):

    _square_pos_cache = {
        (a, b): [(x, y) for x in xrange(square_base[a], square_base[a] + 3) for y in xrange(square_base[b], square_base[b] + 3)]
        for a in xrange(9)
        for b in xrange(9)
    }
    _bit2ints = [
        [i for i in xrange(1, 10) if (1 << i) & c]
        for c in xrange(0b1111111110 + 1)
    ]
    _bitcounts = [get_bit_count(i) for i in xrange(0b1111111110 + 1)]

    def __init__(self, lists, n_slot=None, candidates=None):
        self._lists = lists
        self.n_slot = n_slot if n_slot is not None else sum(lists, []).count(None)
        if candidates is not None:
            self._candidates = candidates
        else:
            self._candidates = collections.defaultdict(int)
            for x in xrange(9):
                for y in xrange(9):
                    self._candidates[(x, y)] = self._calculate_candidates(x, y)

    def next(self):
        lists = self._lists  # local cache
        candidates = self._candidates  # local cache
        min_cdd = 10  # 9 is the largest possible value
        break_it = False
        for x in xrange(9):
            for y in xrange(9):
                if lists[x][y] is not None:
                    continue
                cdd = self._bitcounts[candidates[(x, y)]]
                if cdd >= min_cdd:
                    continue
                mx, my, min_cdd = x, y, cdd
                if cdd == 1:
                    break_it = True
                    break
            if break_it:
                break
        related_poses = set(sum(
            [[(mx, yy) for yy in xrange(9)],
             [(xx, my) for xx in xrange(9)],
             self._square_pos_cache[(mx, my)]],
            [],
        ))
        related_poses.discard((mx, my))
        for x, y in set(related_poses):
            if lists[x][y] is not None:
                related_poses.discard((x, y))
        for value in self._bit2ints[candidates[(mx, my)]]:
            new_candidates = candidates.copy()
            invalid = False
            for x, y in related_poses:
                new_candidates[(x, y)] &= ~ (1 << value)
                if new_candidates[(x, y)] == 0:
                    invalid = True
                    break
            if invalid:
                continue
            new_lists = [lst[:] for lst in lists]
            new_lists[mx][my] = value
            new_n_slot = self.n_slot - 1
            yield Puzzle(new_lists, new_n_slot, new_candidates)

    def _calculate_candidates(self, x, y):
        lists = self._lists  # local cache
        existed = set(lists[x] + list(zip(*lists)[y]) + self.get_square(x, y))
        r = 0
        for e in xrange(1, 10):
            if e not in existed:
                r |= 1 << e
        return r

    def get_square(self, x, y):
        lists = self._lists  # local cache
        return [lists[xx][yy] for xx, yy in self._square_pos_cache[(x, y)]]

    @classmethod
    def create(cls, iterable):
        lst = []
        for sub_iterable in iterable:
            if isinstance(sub_iterable, basestring):
                lst.append(map(lambda i: int(i) if i != '_' else None,
                               list(sub_iterable.strip())))
            else:
                lst.append(sub_iterable)
        return cls(lst)

    def __str__(self):
        r = [''.join(map(lambda i: '_' if i is None else str(i), lst))
             for lst in self._lists]
        return '\n'.join(r)


def resolve(puzzle):
    results = []
    stack = []
    stack.append(puzzle)
    while stack:
        current = stack.pop()
        for next in current.next():
            if next.n_slot == 0:
                results.append(next)
            else:
                stack.append(next)
    return results


def main():
    puzzle = Puzzle.create(open('puzzle5'))
    print puzzle
    # nexts = list(puzzle.next())
    # pool = multiprocessing.Pool(2)
    # results = sum(pool.map(resolve, nexts), [])
    # results = hotspot_profile(resolve)(puzzle)
    results = resolve(puzzle)
    print 'result'
    for result in results:
        print result
        print

if __name__ == '__main__':
    main()
