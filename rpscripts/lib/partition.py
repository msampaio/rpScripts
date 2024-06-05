'''This module provides classes and functions for rhythmic partitioning analysis. For further information, see Gentil-Nunes 2009.

Gentil-Nunes, Pauxy. 2009. "Análise Particional: uma Mediação entre Composição Musical e a Teoria das Partições." Ph.D. Dissertation, Universidade Federal do Estado do Rio de Janeiro.

Gentil-Nunes, Pauxy. 2017. "Nestings and Intersections Between Partitional Complexes." MusMat - Brazilian Journal of Music and Mathematics I (2): 93--108. Available at https://musmat.org/wp-content/uploads/2018/06/09-Pauxy.pdf.
'''

from collections import Counter
from copy import deepcopy
import itertools
import json
import re


from ..config import ENCODING
from .base import get_number_combinations_pairs


def make_subseq(partition, n) -> list:
    '''Return a subset array from a given partition from 0 to `n` element.'''

    return [partition[i] for i in range(n)]


def get_partitions(number: int) -> list:
    '''Return the partitions of a given `number` as a list of lists.'''

    partitions_list = []

    partition = [0] * number
    last_pos = 0
    partition[last_pos] = number

    while True:
        partitions_list.append(make_subseq(partition, last_pos + 1))

        rem_val = 0
        while last_pos >= 0 and partition[last_pos] == 1:
            rem_val += partition[last_pos]
            last_pos -= 1

        if last_pos < 0:
            return partitions_list

        partition[last_pos] -= 1
        rem_val += 1

        while rem_val > partition[last_pos]:
            partition[last_pos + 1] = partition[last_pos]
            rem_val -= partition[last_pos]
            last_pos += 1

        partition[last_pos + 1] = rem_val
        last_pos += 1


def get_lexset(number: int) -> list:
    '''Return the lexical set of a given `number`. The lexical set is the list of all partitions from 1 to number.'''
    partitions = []
    for n in range(1, number + 1):
        partitions.extend(get_partitions(n))
    return partitions


def make_ryp_map(higher_cardinality: int) -> dict:
    '''Make a rhythmic partitioning Young lattice of a given cardinality.'''

    partitions = get_lexset(higher_cardinality)
    dic = {}
    for p in partitions:
        obj = Partition(p)
        dispersion = obj.get_dispersion_index()
        dn = obj.get_density_number()
        if dn not in dic.keys():
            dic[dn] = []
        if dispersion not in dic[dn]:
            dic[dn].append(dispersion)
    return {k: sorted(v) for k, v in dic.items()}


class Partition(object):
    '''Main partition class.'''

    def __init__(self, parts=None) -> None:
        self.parts = None
        self.parts_map = None
        if isinstance(parts, list):
            self.parts = sorted(parts)
        elif isinstance(parts, str):
            self.parts = []
            for el in parts.split('.'):
                if '^' in el:
                    part, n = el.split('^')
                    self.parts.extend([int(part)] * int(n))
                else:
                    self.parts.append(int(el))
        self.counter = Counter(self.parts)

    def __eq__(self, __value: object) -> bool:
        self.parts == __value.parts

    def __repr__(self) -> str:
        return '<P {}>'.format(self.as_string())

    def as_string(self) -> str:
        '''Return the partition as a string such as "1^3.2".'''

        if not self.parts:
            return '0'
        dic = {}
        for el in self.parts:
            if el not in dic.keys():
                dic[el] = 0
            dic[el] += 1

        str_repr =  '.'.join([str(k) if v < 2 else '{}^{}'.format(k, v)
            for k, v in sorted(dic.items())
        ])
        return str_repr

    def get_parts_size(self) -> int:
        '''Count the partition's number of parts.'''

        return len(self.parts)

    def get_density_number(self) -> int:
        '''Return the partition's density number.'''

        return int(sum(self.parts))

    def count_binary_relations(self):
        '''Count binary relations of partition's parts.'''

        density_number = self.get_density_number()
        return get_number_combinations_pairs(density_number)

    def get_agglomeration_index(self) -> int:
        '''Return the partition's agglomeration index.'''

        if self.parts == []:
            return None
        return int(sum([get_number_combinations_pairs(n) for n in self.parts]))

    def get_dispersion_index(self) -> int:
        '''Return the partition's dispersion index.'''

        if self.parts == []:
            return None
        return int(self.count_binary_relations() - self.get_agglomeration_index())

    def resize(self) -> list:
        '''Return the list of current's resized partitions.'''

        # Resizing (m) a part means to change its thickness. The positive
        # resizing implies the inclusion of more sounding components to a
        # block, making it "fatter"; the negative resizing is, on the contrary,
        # the thickening of a part, subtracting a sounding component from a
        # block. (Gentil-Nunes, 2017)

        resized = []

        for part in self.counter.keys():
            _parts = deepcopy(self.parts)
            ind = _parts.index(part)
            _parts[ind] += 1
            _parts.sort()
            resized.append(_parts)
        return list(map(Partition, resized))

    def revariate(self) -> list:
        '''Return the list of current's revariated partitions.'''

        # Revariance (v) is the changing of variety (number of parts) inside a
        # textural configuration. Positive revariance implies adding an unitary
        # part to the partition and negative revariance means subtracting an
        # unitary part from it. (Gentil-Nunes, 2017)

        return Partition(self.parts + [1])

    def transfer(self, default=True) -> list:
        '''Return the list of current's transfered partitions.'''

        # Transference (t) arises when resizing and revariance are applied
        # together, but with opposite signals (positive resizing with negative
        # revariance, and vice-versa). The consequence is that one sounding
        # component is displaced from a part to another, without affecting the
        # overall density- number. This kind of operation is very common in
        # traditional concert music. (Gentil-Nunes, 2017)

        def swap(part_1, part_2):
            _parts = deepcopy(self.parts)

            i1 = _parts.index(part_1)
            _parts.pop(i1)

            i2 = _parts.index(part_2)
            _parts.pop(i2)

            if part_1 > 1:
                _parts.append(part_1 - 1)
            _parts.append(part_2 + 1)

            return Partition(_parts)

        def subtract(part):
            if part > 1:
                _parts = deepcopy(self.parts)
                ind = _parts.index(part)
                _parts[ind] -= 1
                _parts.append(1)

                return Partition(_parts)

        base_disp_ind = self.get_dispersion_index()
        low_pos = 10 ** 10
        high_neg = -1

        def update_pos_neg(p: Partition, low_pos, high_neg) -> tuple:
            p_disp_ind = p.get_dispersion_index()
            if p_disp_ind > base_disp_ind and p_disp_ind < low_pos:
                low_pos = p_disp_ind
            if p_disp_ind < base_disp_ind and p_disp_ind > high_neg:
                high_neg = p_disp_ind
            return low_pos, high_neg


        partitions = []

        for part, quantity in self.counter.items():
            # subtract from an existing part and move to a new part
            p = subtract(part)
            if p:
                low_pos, high_neg = update_pos_neg(p, low_pos, high_neg)
                partitions.append(p)

            # transfer between parts with equal values
            if quantity > 1:
                p = swap(part, part)
                if p:
                    low_pos, high_neg = update_pos_neg(p, low_pos, high_neg)
                    partitions.append(p)


        # transfer/swap between parts with different values
        distinct = list(self.counter.keys())
        for part_1, part_2 in itertools.combinations(distinct, 2):
            p = swap(part_1, part_2)
            if p.parts != self.parts and p not in partitions:
                low_pos, high_neg = update_pos_neg(p, low_pos, high_neg)
                partitions.append(p)

            p = swap(part_2, part_1)
            if p.parts != self.parts and p not in partitions:
                low_pos, high_neg = update_pos_neg(p, low_pos, high_neg)
                partitions.append(p)

        result = {'positive': [], 'negative': []}

        partitions = sorted(partitions, key=lambda p: p.get_agglomeration_index())

        for p in partitions:
            p_disp_ind = p.get_dispersion_index()
            if default:
                if p_disp_ind == low_pos:
                    result['positive'].append(p)
                elif p_disp_ind == high_neg:
                    result['negative'].append(p)
            else:
                if p_disp_ind > base_disp_ind:
                    result['positive'].append(p)
                elif p_disp_ind < base_disp_ind:
                    result['negative'].append(p)
        return result


class PartitionLattice(object):
    '''Partition Lattice class. It helps in lattice creating and saving.'''

    def __init__(self, cardinality=10) -> None:
        print('Creating lattice map with cardinality {}.'.format(cardinality))
        self.filename = 'lattice_map.json'
        self.data = {}
        self.data = make_ryp_map(cardinality)

    def save_file(self):
        '''Save lattice map into file.'''

        print('Saving lattice map to file {}.'.format(self.filename))
        with open(self.filename, 'w', encoding=ENCODING) as fp:
            json.dump(self.data, fp)