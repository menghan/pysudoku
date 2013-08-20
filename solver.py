#!/usr/bin/env python
# coding=utf-8

import copy
import itertools


class Puzzle(object):

    def __init__(self, lists):
        self._lists = lists
        self.n_slot = sum(lists, []).count(None)

    def get(self, x, y):
        return self._lists[x][y]

    def set(self, x, y, value):
        assert value is None or isinstance(value, int) and 1 <= value <= 9
        self._lists[x][y] = value

    def check(self, pos=None):
        if pos is None:
            return self._check_whole()

    def _check_whole(self):
        for lsts in (self._lists, itertools.izip(*self._lists), self.get_squares()):
            for lst in lsts:
                if None not in lst and list(sorted(lst)) == range(1, 10):
                    return False
        return True

    def get_squares(self):
        for x0 in xrange(len(self._lists), 3):
            for y0 in xrange(len(self._lists[0]), 3):
                yield [self.get(x, y)
                       for x in xrange(x0, x0 + 3) for y in xrange(y0, y0 + 3)]

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
        lsts = copy.deepcopy(self._lists)
        return Puzzle(lsts)


def resolve(puzzle):
    return puzzle


def main():
    puzzle = Puzzle.create(open('puzzle1'))
    print puzzle
    print puzzle.check()
    result = resolve(puzzle)
    print 'result'
    print result

if __name__ == '__main__':
    main()
