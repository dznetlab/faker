# coding=utf-8

from __future__ import unicode_literals

from decimal import Decimal

import six
import sys
import warnings

from .. import BaseProvider


class Provider(BaseProvider):
    default_value_types = (
        'str', 'str', 'str', 'str', 'float', 'int', 'int', 'decimal',
        'date_time', 'uri', 'email',
    )

    def _check_signature(self, value_types, allowed_types):
        if value_types is not None and not isinstance(value_types, (list, tuple)):
            value_types = [value_types]
            warnings.warn(
                'Passing value types as positional arguments is going to be '
                'deprecated.  Pass them as a list or tuple instead.',
                PendingDeprecationWarning,
            )
        if value_types is None:
            value_types = ()
        return tuple(value_types) + allowed_types

    def pybool(self):
        return self.random_int(0, 1) == 1

    def pystr(self, min_chars=None, max_chars=20):
        """
        Generates a random string of upper and lowercase letters.
        :type min_chars: int
        :type max_chars: int
        :return: String. Random of random length between min and max characters.
        """
        if min_chars is None:
            return "".join(self.random_letters(length=max_chars))
        else:
            assert (
                max_chars >= min_chars), "Maximum length must be greater than or equal to minium length"
            return "".join(
                self.random_letters(
                    length=self.generator.random.randint(min_chars, max_chars),
                ),
            )

    def pyfloat(self, left_digits=None, right_digits=None, positive=False):
        if left_digits is not None and left_digits < 0:
            raise ValueError(
                'A float number cannot have less than 0 digits in its '
                'integer part')
        if right_digits is not None and right_digits < 0:
            raise ValueError(
                'A float number cannot have less than 0 digits in its '
                'fractional part')
        if left_digits == 0 and right_digits == 0:
            raise ValueError(
                'A float number cannot have less than 0 digits in total')

        left_digits = left_digits if left_digits is not None else (
            self.random_int(1, sys.float_info.dig))
        right_digits = right_digits if right_digits is not None else (
            self.random_int(0, sys.float_info.dig - left_digits))
        sign = 1 if positive else self.random_element((-1, 1))

        return float("{0}.{1}".format(
            sign * self.random_number(left_digits),
            self.random_number(right_digits),
        ))

    def pyint(self):
        return self.generator.random_int()

    def pydecimal(self, left_digits=None, right_digits=None, positive=False):
        return Decimal(str(self.pyfloat(left_digits, right_digits, positive)))

    def pytuple(self, nb_elements=10, variable_nb_elements=True, value_types=None, *allowed_types):
        return tuple(
            self.pyset(
                nb_elements,
                variable_nb_elements,
                value_types,
                *allowed_types))

    def pyset(self, nb_elements=10, variable_nb_elements=True, value_types=None, *allowed_types):
        return set(
            self._pyiterable(
                nb_elements,
                variable_nb_elements,
                value_types,
                *allowed_types))

    def pylist(self, nb_elements=10, variable_nb_elements=True, value_types=None, *allowed_types):
        return list(
            self._pyiterable(
                nb_elements,
                variable_nb_elements,
                value_types,
                *allowed_types))

    def pyiterable(
            self,
            nb_elements=10,
            variable_nb_elements=True,
            value_types=None,
            *allowed_types):
        value_types = self._check_signature(value_types, allowed_types)
        return self.random_element([self.pylist, self.pytuple, self.pyset])(
            nb_elements, variable_nb_elements, value_types, *allowed_types)

    def _random_type(self, type_list):
        value_type = self.random_element(type_list)

        method_name = "py{0}".format(value_type)
        if hasattr(self, method_name):
            value_type = method_name

        return self.generator.format(value_type)

    def _pyiterable(
            self,
            nb_elements=10,
            variable_nb_elements=True,
            value_types=None,
            *allowed_types):

        value_types = self._check_signature(value_types, allowed_types)

        value_types = [t if isinstance(t, six.string_types) else getattr(t, '__name__', type(t).__name__).lower()
                       for t in value_types
                       # avoid recursion
                       if t not in ['iterable', 'list', 'tuple', 'dict', 'set']]
        if not value_types:
            value_types = self.default_value_types

        if variable_nb_elements:
            nb_elements = self.randomize_nb_elements(nb_elements, min=1)

        for _ in range(nb_elements):
            yield self._random_type(value_types)

    def pydict(self, nb_elements=10, variable_nb_elements=True, value_types=None, *allowed_types):
        """
        Returns a dictionary.

        :nb_elements: number of elements for dictionary
        :variable_nb_elements: is use variable number of elements for dictionary
        :value_types: type of dictionary values
        """
        if variable_nb_elements:
            nb_elements = self.randomize_nb_elements(nb_elements, min=1)

        return dict(zip(
            self.generator.words(nb_elements),
            self._pyiterable(nb_elements, False, value_types, *allowed_types),
        ))

    def pystruct(self, count=10, value_types=None, *allowed_types):
        value_types = self._check_signature(value_types, allowed_types)

        value_types = [t if isinstance(t, six.string_types) else getattr(t, '__name__', type(t).__name__).lower()
                       for t in value_types
                       # avoid recursion
                       if t != 'struct']
        if not value_types:
            value_types = self.default_value_types

        types = []
        d = {}
        nd = {}
        for i in range(count):
            d[self.generator.word()] = self._random_type(value_types)
            types.append(self._random_type(value_types))
            nd[self.generator.word()] = {i: self._random_type(value_types),
                                         i + 1: [self._random_type(value_types),
                                                 self._random_type(value_types),
                                                 self._random_type(value_types)],
                                         i + 2: {i: self._random_type(value_types),
                                                 i + 1: self._random_type(value_types),
                                                 i + 2: [self._random_type(value_types),
                                                         self._random_type(value_types)]}}
        return types, d, nd
