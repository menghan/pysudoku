#!/usr/bin/env python
# coding=utf-8

import heapq
import collections


def profile(f):
    def func(*args, **kwargs):
        import os
        import hotshot
        import hotshot.stats
        path = '/tmp/solve-puzzle-%s.prof' % os.getpid()
        prof = hotshot.Profile(path)
        prof.runcall(f, *args, **kwargs)
        prof.close()
        stats = hotshot.stats.load(path)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
        stats.sort_stats('cumulative')
        stats.print_stats(20)
    return func


class Puzzle(object):

    _square_pos_cache = {}

    def __init__(self, lists, candidates=None):
        self._lists = [[e for e in lst] for lst in lists]
        self.n_slot = sum(lists, []).count(None)
        if candidates is not None:
            self._candidates = candidates.copy()
        else:
            self._candidates = collections.defaultdict(int)

    def get_slots(self):
        slots = [(x, y) for x, lst in enumerate(self._lists)
                 for y, e in enumerate(lst) if e is None]
        return heapq.nsmallest(1, slots, key=lambda slot: self.get_candidates_len(*slot))[0]

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
        r = 0
        while c:
            c = c & (c - 1)
            if c:
                r += 1
        return r

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
                self.get_square_positions(x, y)
        candidates = self._candidates  # local cache
        for pos in related_poses:
            candidates[pos] &= ~ (1 << value)

    def get_square_positions(self, x, y):
        if (x, y) not in self._square_pos_cache:
            square_x_base = x / 3 * 3
            square_y_base = y / 3 * 3
            self._square_pos_cache[(x, y)] = \
                    [(xx, yy) for xx in xrange(square_x_base, square_x_base + 3)
                     for yy in xrange(square_y_base, square_y_base + 3)]
        return self._square_pos_cache[(x, y)]

    def get_square(self, x, y):
        lists = self._lists  # local cache
        return [lists[xx][yy] for xx, yy in self.get_square_positions(x, y)]

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
        return Puzzle(self._lists, self._candidates)


def resolve(puzzle):
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
                yield next
            else:
                stack.append(next)


@profile
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
