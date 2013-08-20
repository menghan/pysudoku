#!/usr/bin/env python
# coding=utf-8

import copy
import itertools


class Puzzle(object):

    def __init__(self, lists):
        self._lists = lists
        self.n_slot = sum(lists, []).count(None)

    def get_slots(self):
        for x, lst in enumerate(self._lists):
            for y, e in enumerate(lst):
                if e is None:
                    yield (x, y)

    def set(self, x, y, value):
        assert isinstance(value, int) and 1 <= value <= 9
        if self._lists[x][y] is None:
            self.n_slot -= 1
        self._lists[x][y] = value

    def check(self, pos=None):
        if pos is None:
            return self._check_whole()
        else:
            return self._check_by_pos(pos)

    def _check_lists(self, lists):
        for lst in lists:
            if len(filter(None, lst)) != len(set(filter(None, lst))):
                return False
        return True

    def _check_whole(self):
        return self._check_lists(itertools.chain(
            self._lists,
            itertools.izip(*self._lists),
            self.get_squares(),
        ))

    def _check_by_pos(self, pos):
        x, y = pos
        lists = self._lists  # local cache
        square_x_base = x / 3 * 3
        square_y_base = y / 3 * 3
        check_lists = [
            lists[x],
            zip(*lists)[y],
            [lists[xx][yy] for xx in xrange(square_x_base, square_x_base + 3)
             for yy in xrange(square_y_base, square_y_base + 3)]
        ]
        return self._check_lists(check_lists)

    def get_squares(self):
        lists = self._lists  # local cache
        for x0 in xrange(0, len(lists), 3):
            for y0 in xrange(0, len(lists[0]), 3):
                yield [lists[x][y] for x in xrange(x0, x0 + 3) for y in xrange(y0, y0 + 3)]

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
    stack = []
    stack.append(puzzle)
    while stack:
        current = stack.pop()
        for slot in current.get_slots():
            x, y = slot
            for i in xrange(1, 10):
                next = current.clone()
                next.set(x, y, i)
                if next.check((x, y)):
                    if next.n_slot == 0:
                        return next
                    else:
                        stack.append(next)
            break


def main():
    puzzle = Puzzle.create(open('puzzle1'))
    print puzzle
    print puzzle.check()
    result = resolve(puzzle)
    print 'result'
    print result

if __name__ == '__main__':
    main()