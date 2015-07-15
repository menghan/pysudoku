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
        v = v & (v - 1)
        if v:
            r += 1
    return r


bitcounts = [get_bit_count(i) for i in xrange(0b1111111110)]
square_base = [0, 0, 0, 3, 3, 3, 6, 6, 6]


class Puzzle(object):

    __slots__ = ('_lists', 'n_slot', '_candidates')
    _square_pos_cache = {
        (a, b): [(x, y) for x in xrange(square_base[a], square_base[a] + 3) for y in xrange(square_base[b], square_base[b] + 3)]
        for a in xrange(9)
        for b in xrange(9)
    }

    def __init__(self, lists, n_slot=None, candidates=None):
        self._lists = [[e for e in lst] for lst in lists]
        self.n_slot = n_slot if n_slot is not None else sum(lists, []).count(None)
        if candidates is not None:
            self._candidates = candidates.copy()
        else:
            self._candidates = collections.defaultdict(int)

    def get_slots(self):
        min_cdd = 10  # 9 is the largest possible value
        for x, lst in enumerate(self._lists):
            for y, e in enumerate(lst):
                if e is None:
                    cdd = self.get_candidates_len(x, y)
                    if cdd < min_cdd:
                        rx, ry, min_cdd = x, y, cdd
        return rx, ry

    def get_candidates(self, x, y):
        if (x, y) not in self._candidates:
            self._candidates[(x, y)] = self._calculate_candidates(x, y)
        c = self._candidates[(x, y)] & 0b1111111110
        return self._bit2ints(c)

    def _bit2ints(self, c):
        return [i for i in xrange(1, 10) if (1 << i) & c]

    def get_candidates_len(self, x, y):
        if (x, y) not in self._candidates:
            self._candidates[(x, y)] = self._calculate_candidates(x, y)
        c = self._candidates[(x, y)] & 0b1111111110
        return bitcounts[c]

    def _calculate_candidates(self, x, y):
        lists = self._lists  # local cache
        assert lists[x][y] is None
        existed = set(lists[x] + list(zip(*lists)[y]) + self.get_square(x, y))
        r = 0
        for e in xrange(1, 10):
            if e not in existed:
                r |= 1 << e
        return r

    def calculate_all_candidates(self):
        lists = self._lists
        for x in xrange(9):
            for y in xrange(9):
                if lists[x][y] is None:
                    self.get_candidates(x, y)

    def set(self, x, y, value):
        assert isinstance(value, int) and 1 <= value <= 9
        if self._lists[x][y] is None:
            self.n_slot -= 1
        self._lists[x][y] = value
        related_poses = [(x, yy) for yy in xrange(9)] + \
                [(xx, y) for xx in xrange(9)] + \
                self._square_pos_cache[(x, y)]
        candidates = self._candidates  # local cache
        for pos in related_poses:
            candidates[pos] &= ~ (1 << value)

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
        for i in list(candidates):
            next = current.clone()
            next.set(x, y, i)
            if next.n_slot == 0:
                results.append(next)
            else:
                stack.append(next)
    return results


def main():
    puzzle = Puzzle.create(open('puzzle5'))
    print puzzle
    puzzle.calculate_all_candidates()
    results = resolve(puzzle)
    print 'result'
    for result in results:
        print result
        print

if __name__ == '__main__':
    main()
