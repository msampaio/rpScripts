'''This module provides classes and functions for rhythmic partitioning analysis. For further information, see Gentil-Nunes 2009.

Gentil-Nunes, Pauxy. 2009. "Análise Particional: uma Mediação entre Composição Musical e a Teoria das Partições." Ph.D. Dissertation, Universidade Federal do Estado do Rio de Janeiro.
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
        # block.

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
        # unitary part from it.

        return Partition(self.parts + [1])

    def transfer(self, default=True) -> list:
        '''Return the list of current's transfered partitions.'''

        # Transference (t) arises when resizing and revariance are applied
        # together, but with opposite signals (positive resizing with negative
        # revariance, and vice-versa). The consequence is that one sounding
        # component is displaced from a part to another, without affecting the
        # overall density- number. This kind of operation is very common in
        # traditional concert music.

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

    # TODO: confirmar esse nome
    def get_transfers_index(self):
        dn = self.get_density_number()
        return self.get_dispersion_index() / dn * (dn - 1) / 2

    def _aux_get_sons(self):
        p_str = self.as_string()
        relations_list = []
        if self.get_parts_size() > 1:
            for part in self.counter.keys():
                _parts = self.parts[:]
                _parts.remove(part)
                p = Partition(_parts)
                child = p.as_string()
                relation = (p_str, child, 'S')
                if relation not in relations_list:
                    relations_list.append(relation)
        return relations_list

    def get_subpartitions(self):
        node = PartitionComplexNode(self)
        node.get_descendants()
        return node

    # def get_subpartitions(self):
    #     size = self.get_parts_size()
    #     subpartitions = []

    #     # daughters
    #     for n in range(2, size + 1):
    #         permutations = itertools.permutations(self.parts, n)
    #         for j in range(2, n):
    #             for seq in permutations:
    #                 a = seq[:j]
    #                 b = seq[j:]
    #                 c = sum(list(a))
    #                 subseq = list(b)
    #                 subseq.append(c)
    #                 subseq = sorted(subseq)
    #                 if subseq not in subpartitions:
    #                     subpartitions.append(subseq)

    #     # sons
    #     for n in range(1, size + 1):
    #         combinations = itertools.combinations(self.parts, n)
    #         for tup in combinations:
    #             value = list(tup)
    #             if value not in subpartitions:
    #                 subpartitions.append(value)
    #             value_sum = [sum(value)]
    #             if value_sum not in subpartitions:
    #                 subpartitions.append(value_sum)
    #     return sorted(list(map(Partition, subpartitions)), key=lambda p: p.parts)


class AuxiliaryPartitionComplex(object):
    def __init__(self, partition: Partition) -> None:
        self.partition = partition
        self.parts_length = partition.get_parts_size()
        self.relations = []
        self.targets = set()
        self.sources = set()

    def run(self):
        # Relation:
        # (parent_str, child_str, relation_type)
        pass

    def set_sons(self):
        relations_list = self.partition._aux_get_sons()
        for relation in relations_list:
            self.targets.add(relation[1])
            if relation not in self.relations:
                self.relations.append(relation)

    def set_descendants(self):
        self.set_sons()
        # dado uma partição P, se ela não existir nos target, calcular todos os child. Caso contrário, encerrar.
        # diferenciar filho de filha.
        for target in self.targets:
            if not re.match('^[0-9]+$', target) and target not in self.sources:
                partition = Partition(target)
                relations = partition._aux_get_sons()



                print(target)
        pass


class PartitionComplexNode(object):
    def __init__(self, partition: Partition, parent_key=None) -> None:
        self.partition = partition
        self.parts_length = partition.get_parts_size()
        self.parent_key = parent_key # it can be useful in the future
        self.sons = []
        self.daughters = []

    def __repr__(self) -> str:
        return '<PC {}>'.format(self.partition.as_string())

    def get_sons(self):
        sons_nodes = []
        if self.parts_length > 1:
            for part in self.partition.counter.keys():
                _parts = self.partition.parts[:]
                _parts.remove(part)
                p = Partition(_parts)
                node = PartitionComplexNode(p, self.partition.as_string())
                if node not in sons_nodes:
                    sons_nodes.append(node)
            self.sons = sons_nodes
        return self.sons

    def get_daughters(self):
        parts_to_sum = []
        daughters_parts = []

        # process repeated parts: 1^2+, 2^2+, etc
        for part, quantity in self.partition.counter.items():
            parts_to_sum.append(part)
            if quantity > 1:
                _parts = self.partition.parts[:]
                _parts.remove(part)
                _parts.remove(part)
                _parts.append(part * 2)
                daughters_parts.append(_parts)

        # process combinations of unique parts
        for part_1, part_2 in itertools.combinations(parts_to_sum, 2):
            _parts = self.partition.parts[:]
            _parts.remove(part_1)
            _parts.remove(part_2)
            _parts.append(part_1 + part_2)
            daughters_parts.append(_parts)

        self.daughters = [PartitionComplexNode(Partition(parts), self.partition.as_string()) for parts in daughters_parts]
        return self.daughters

    def get_children(self):
        # get sons and daughters
        if self.sons == []:
            self.get_sons()
        if self.daughters == []:
            self.get_daughters()

        # make a list with both sons and daughters
        children = []
        children.extend(self.sons)
        children.extend(self.daughters)
        return children

    def get_descendants(self):
        for child in self.get_children():
            child.get_descendants()

    # def get_family_map(self, dic={}):
    #     def aux(dic: dict, node: PartitionComplexNode):
    #         key = node.partition.as_string()
    #         parent_key = node.parent_key
    #         dic.update({key: parent_key})
    #         return dic

    #     children = self.get_children()
    #     for child in children:
    #         dic = aux(dic, child)
    #         dic = child.get_family_map(dic)
    #     return dic
    #     # for child in

    def print_tree(self, category='sons', tab=''):
        print('{}- {}'.format(tab, self.partition.as_string()))
        tab += ' ' * 2
        if category == 'sons':
            children = self.sons
        elif category == 'daughters':
            children = self.daughters
        # else:
        #     self.print_tree('sons', tab)
        #     self.print_tree('daughters', tab)

        if children:
            for child in children:
                child.print_tree(category, tab)

    def print_descendants(self):
        print('Node: {}, parent: {}'.format(self.partition.as_string(), self.parent_key))
        children = self.get_children()
        if children != []:
            for child in self.get_children():
                child.print_descendants()



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


class PartitionComparator(object):
    def __init__(self, partition_1: Partition, partition_2: Partition) -> None:
        self.p1 = partition_1
        self.p2 = partition_2

    def get_jacquard_similarity(self):
        '''Return Jacquard similarity value. See Moreira, 2019.'''

        intersection = set(self.p1.parts).intersection(self.p2.parts)
        s1 = self.p1.get_parts_size()
        s2 = self.p2.get_parts_size()
        inter_size = len(intersection)
        return inter_size / (s1 + s2 - inter_size)