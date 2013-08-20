#!/usr/bin/env python
# coding=utf-8


class Puzzle(object):

    def __init__(self, lists):
        self._lists = lists

    def get(self, x, y):
        return self._lists[x][y]

    def check(self, new=None):
        if new is None:
            return self._check_whole()

    def _check_whole(self):

        def __check(lst):
            return None in lst or list(sorted(lst)) == range(1, 10)

        for lst in self._lists + zip(*self._lists):
            if not __check(lst):
                return False

        for square in self.get_squares():
            if not __check(square):
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

puzzle = Puzzle.create(open('puzzle1'))
print puzzle
print puzzle.check()
