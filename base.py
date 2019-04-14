from collections import Iterable
from functools import reduce, partial


def idx(x):
    return x


def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))

    return reduce(compose2, functions, lambda x: x)


class Applicative:
    def pure(self, a):
        pass

    def apply(self, a):
        raise NotImplementedError


class Functor:
    def __init__(self, get):
        self.get = get

    def map(self, f):
        raise NotImplemented

    def fill(self, a):
        return self.map(lambda _: a)


class Maybe(Functor, Applicative):
    def apply(self, a):
        return self.__class__(self.get(a))

    def map(self, f):
        if self == Nothing:
            return Nothing
        else:
            return Just(f(self.get))


class Nothing(Maybe):
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError


class Just(Maybe):

    def __init__(self, get):
        """
        :param get: Any
        """
        super(Just, self).__init__(get)

    def __repr__(self):
        return "Just({get})".format(get=repr(self.get))


class Try:
    def __call__(self, f):
        try:
            return Right(f())
        except Exception as e:
            return Left(e)


Try = Try()


class Para:
    def __call__(self, *args, **kwargs):
        return args, kwargs


Para = Para()


class Either(Functor, Applicative):
    def apply(self, a):
        if isinstance(self, Left):
            return self
        else:
            return self.__class__(self.get(a))

    def map(self, f):
        """
        :param f: a -> b
        :return: Either E b
        """
        if isinstance(self, Left):
            return self
        else:
            return Try(lambda: f(self.get))

    def flat_map(self, f):
        if isinstance(self, Left):
            return self
        else:
            temp = self.map(f)
            if isinstance(temp.get, Either):
                return temp.get
            else:
                return temp

    @staticmethod
    def traverse(es, f):
        """
        :param es: [a]
        :param f: a -> Either E b
        :return: [ Either E b ]
        """
        assert isinstance(es, Iterable)

        return Try(lambda: compose(list, partial(map, lambda e: f(e).get))(es))

    @staticmethod
    def sequence(es):
        """
        :param es: [Either E a]
        :return: Either E [a]
        """
        assert isinstance(es, Iterable)
        return Either.traverse(es, idx)

    def map2(self, other, f):
        """
        :param other: Either
        :param f: (a,b) -> c
        :return: Either E c
        """
        return Try(lambda: f(self.get, other.get))

    def __str__(self):
        return repr(self.get)

    def or_else(self, b):
        if isinstance(self, Left):
            return b
        else:
            return self


class Left(Either):
    def __init__(self, exception):
        """
        :param exception: Exception
        """
        super(Left, self).__init__(exception)


class Right(Either):
    def __init__(self, get):
        """
        :param get: Any
        """
        super(Right, self).__init__(get)


class Reader(Functor, Applicative):
    def __init__(self, f):
        """
        :param f: a -> b
        """

        super(Reader, self).__init__(f)

    def apply(self, g):
        """
        :param self: a -> ( x -> y)
        :param g: a -> x
        :return:
        """
        return self.__class__(lambda a: self.get(a)(g(a)))

    def map(self, f):
        """
        :param f: b -> c
        :return: Reader (a -> c)
        """
        return Reader(lambda a: f(self.get(a)))


def fmap(f):
    return lambda functor: functor.map(f)


class List(list, Functor):
    def map(self, f):
        return List([f(i) for i in self])


if __name__ == '__main__':
    print(Left(lambda a: 2 * a).apply(4))
    print(List([1, 2, 3, 4]).fill(12))
