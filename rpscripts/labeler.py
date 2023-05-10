'''This module parses TXT label file and adds this information into the JSON file.'''

from .config import ENCODING
from .lib.base import EventLocation, GeneralSubparser, RPData, file_rename, find_nearest_smaller


class Edge(object):
    '''This class represents the point where a excerpt or section starts.'''

    def __init__(self, label=None, index=None, global_offset=None) -> None:
        self.label = label
        self.event_location = EventLocation(str_index=index)
        self.index = index # 'measure_number+local_offset'
        self.global_offset = global_offset

    def __repr__(self) -> str:
        return '<E {} {} {}>'.format(self.label, self.index, self.global_offset)

    def set_global_offset(self, offset_map: dict) -> None:
        '''Set the edge global offset from a given offset map.'''

        measure_number = self.event_location.measure_number
        local_offset = self.event_location.offset
        self.global_offset = offset_map[measure_number] + local_offset

    def set_index(self, offset_map: dict) -> None:
        '''Set the edge index (measure_number + global_offset).'''

        inverted = {v: k for k, v in offset_map.items()}
        m_go = find_nearest_smaller(self.global_offset, list(inverted.keys()))
        measure_number = inverted[m_go]
        local_offset = self.global_offset - m_go
        self.event_location = EventLocation(measure_number=measure_number, offset=local_offset)
        self.index = self.event_location.str_index


def parse_txt(filename: str) -> list:
    '''Return list of `Edge` objects created from extracted labels information given in TXT file.'''

    with open(filename, 'r', encoding=ENCODING) as fp:
        rows = [row.rstrip('\n') for row in fp.readlines() if row]

    edges = []
    for row in rows:
        label, ind = row.split(',')
        label = label.lstrip().rstrip()
        ind = ind.lstrip().rstrip()
        edge = Edge(label, ind)
        edges.append(edge)

    return edges


def main(json_filename: str, txt_fname: str) -> None:
    '''Add the given TXT file labels into the given JSON file.'''

    rpdata = RPData(json_filename)

    measures = rpdata.data['Measure number']
    last_measure = measures[-1]
    last_duration = rpdata.data['Duration'][-1]
    last_global_offset = rpdata.offset_map[str(last_measure)] + last_duration

    # Get excerpts edges
    edges = parse_txt(txt_fname)

    # Add global offset for each edge
    for edge in edges:
        edge.set_global_offset(rpdata.offset_map)

    # Add an edge at the end
    final_edge = Edge('End', global_offset=last_global_offset + 100)
    final_edge.set_index(rpdata.offset_map)
    edges.append(final_edge)

    # Insert a start global offset if necessary
    start_global_offset = rpdata.data['Global offset'][0]
    if edges[0].global_offset > start_global_offset:
        edges.insert(0, Edge('', '', start_global_offset))

    # Convert the edge list into a dictionary
    edges_dic = {
        (edges[i].global_offset, edges[i + 1].global_offset): edges[i].label
        for i in range(len(edges) - 1)
    }

    labels = []

    edges_keys = list(edges_dic.keys())

    edge_pointer = 0
    current_key = edges_keys[edge_pointer]

    row_pointer = 0

    while row_pointer < rpdata.size:
        start, end = current_key
        current_global_offset = rpdata.data['Global offset'][row_pointer]

        if current_global_offset >= start and current_global_offset < end:
            labels.append(edges_dic[current_key])
            row_pointer += 1
        else:
            edge_pointer += 1
            current_key = edges_keys[edge_pointer]

    rpdata.labels = labels

    path = file_rename(json_filename, 'json')
    rpdata.save_to_file(path)


class Subparser(GeneralSubparser):
    '''Implements argparser.'''

    def setup(self) -> None:
        self.program_name = 'label'
        self.program_help = 'JSON file labeler. Annotate JSON file with given labels'

    def add_arguments(self) -> None:
        self.parser.add_argument('-t', '--txt_filename', help="TXT filename (labels map)", type=str)

    def handle(self, args):
        print('Running script on {} filename...'.format(args.filename))

        main(args.filename, args.txt_filename)
