#!/usr/bin/env python
# coding=utf-8

import collections

def profile(f):
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
        self._lists = [lst[:] for lst in lists]
        self.n_slot = n_slot if n_slot is not None else sum(lists, []).count(None)
        if candidates is not None:
            self._candidates = candidates.copy()
        else:
            self._candidates = collections.defaultdict(int)
            for x in xrange(9):
                for y in xrange(9):
                    self._candidates[(x, y)] = self._calculate_candidates(x, y)

    def get_slots(self):
        lists = self._lists  # local cache
        min_cdd = 10  # 9 is the largest possible value
        for x in xrange(9):
            for y in xrange(9):
                if lists[x][y] is None:
                    cdd = self._bitcounts[self._candidates[(x, y)]]
                    if cdd < min_cdd:
                        rx, ry, min_cdd = x, y, cdd
                        if min_cdd == 1:
                            return rx, ry
        return rx, ry

    def get_candidates(self, x, y):
        return self._bit2ints[self._candidates[(x, y)]]

    def _calculate_candidates(self, x, y):
        lists = self._lists  # local cache
        existed = set(lists[x] + list(zip(*lists)[y]) + self.get_square(x, y))
        r = 0
        for e in xrange(1, 10):
            if e not in existed:
                r |= 1 << e
        return r

    def set(self, x, y, value):
        assert isinstance(value, int) and 1 <= value <= 9
        lists = self._lists  # local cache
        assert lists[x][y] is None
        lists[x][y] = value
        self.n_slot -= 1
        related_poses = [(x, yy) for yy in xrange(9)] + \
                [(xx, y) for xx in xrange(9)] + \
                self._square_pos_cache[(x, y)]
        candidates = self._candidates  # local cache
        for x, y in related_poses:
            if lists[x][y] is not None:
                continue
            candidates[(x, y)] &= ~ (1 << value)
            if candidates[(x, y)] == 0:
                return False
        return True

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

    def clone(self):
        return Puzzle(self._lists, self.n_slot, self._candidates)


@profile
def resolve(puzzle):
    results = []
    stack = []
    stack.append(puzzle)
    while stack:
        current = stack.pop()
        x, y = current.get_slots()
        candidates = current.get_candidates(x, y)
        for i in candidates:
            next = current.clone()
            if not next.set(x, y, i):
                continue
            if next.n_slot == 0:
                results.append(next)
            else:
                stack.append(next)
    return results


def main():
    puzzle = Puzzle.create(open('puzzle5'))
    print puzzle
    results = resolve(puzzle)
    print 'result'
    for result in results:
        print result
        print

if __name__ == '__main__':
    main()
