#!/usr/bin/env python
# coding=utf-8

import itertools


class Puzzle(object):

    def __init__(self, lists):
        self._lists = [[e for e in lst] for lst in lists]
        self.n_slot = sum(lists, []).count(None)

    def get_slots(self):
        slots = [(x, y) for x, lst in enumerate(self._lists)
                 for y, e in enumerate(lst) if e is None]
        slots.sort(key=lambda slot: len(self.get_candidates(slot[0], slot[1])))
        return slots[0]

    def get_candidates(self, x, y):
        lists = self._lists  # local cache
        assert lists[x][y] is None
        existed = set()
        for e in lists[x] + list(zip(*lists)[y]) + self.get_square(x, y):
            existed.add(e)
        return set(range(1, 10)) - existed

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
            self.get_square(x, y),
        ]
        return self._check_lists(check_lists)

    def get_square(self, x, y):
        lists = self._lists  # local cache
        square_x_base = x / 3 * 3
        square_y_base = y / 3 * 3
        return [lists[xx][yy] for xx in xrange(square_x_base, square_x_base + 3)
                for yy in xrange(square_y_base, square_y_base + 3)]

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
        return Puzzle(self._lists)


def resolve(puzzle):
    stack = []
    stack.append(puzzle)
    while stack:
        current = stack.pop()
        x, y = current.get_slots()
        candidates = current.get_candidates(x, y)
        for i in candidates:
            next = current.clone()
            next.set(x, y, i)
            if next.n_slot == 0:
                return next
            else:
                stack.append(next)


def main():
    puzzle = Puzzle.create(open('puzzle4'))
    print puzzle
    print puzzle.check()
    result = resolve(puzzle)
    print 'result'
    print result

if __name__ == '__main__':
    main()
