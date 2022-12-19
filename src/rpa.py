import argparse
import csv
import fractions
import math
import music21


def find_nearest_smaller(value, seq):
    if value < seq[0]:
        return -1

    if value > seq[-1]:
        return seq[-1]

    size = len(seq)

    if size == 1 and value >= seq[0]:
        return seq[0]

    middle_pointer = math.floor(size/2)

    left = seq[:middle_pointer]
    right = seq[middle_pointer:]

    if value < right[0]:
        return find_nearest_smaller(value, left)
    else:
        return find_nearest_smaller(value, right)


def simplify_csv(csv_fname):
    seq = []
    last_row = None
    with open(csv_fname, 'r') as fp:
        i = 0
        for row in csv.reader(fp):
            if i > 0:
                if i == 1:
                    last_row = row
                if row[5] != last_row[5]:
                    seq.append(last_row)
                    last_row = row
            i += 1
    return seq


def make_offset_map(sco):
    measures = sco.parts[0].getElementsByClass(music21.stream.Measure).stream()
    return {om.element.offset: om.element.number for om in measures.offsetMap()}


def get_events_location(sco, csv_fname):
    offset_map = make_offset_map(sco)
    offsets = list(offset_map.keys())
    seq = simplify_csv(csv_fname)

    events_location = {}

    for row in seq:
        if row[3] == '0':
            a, b = 0, 1
        elif '/' in row[3]:
            a, b = list(map(int, row[3].split('/')))
        else:
            a, b = int(row[3]), 1
        global_offset = fractions.Fraction(a, b)
        partition = row[5]
        measure_offset = find_nearest_smaller(global_offset, offsets)
        measure_number = offset_map[measure_offset]
        offset = global_offset - measure_offset
        if measure_number not in events_location:
            events_location[measure_number] = []
        events_location[measure_number].append((offset, partition))

    return events_location


def main(sco, csv_fname, outfile):

    events_location = get_events_location(sco, csv_fname)

    p0 = sco.parts[0]
    new_part = music21.stream.Stream()
    new_part.insert(0, music21.clef.PercussionClef())

    measures = {}

    for m in p0.getElementsByClass(music21.stream.Measure):
        new_measure = music21.stream.Measure()
        new_measure.number = m.number
        new_measure.offset = m.offset
        if m.number in events_location.keys():
            for _offset, partition in events_location[m.number]:
                rest = music21.note.Rest(quarterLength=1/256)
                rest.offset = _offset
                rest.addLyric(partition)
                new_measure.insert(_offset, rest)
            new_measure = new_measure.makeRests(fillGaps=True)
            for el in new_measure:
                el.style.color = 'white'
                el.style.hideObjectOnPrint = True
        measures.update({m.number: new_measure})

    for m in measures.values():
        new_part.append(m)

    new_part = new_part.makeRests(fillGaps=True)

    sco.insert(0, new_part)
    sco.write(fmt='xml', fp=outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'rpa',
                description = 'Rhythmic Partitioning Annotator',
                epilog = 'Rhythmic Partitioning Annotator')
    parser.add_argument("-s", "--score", help = "Score filename.")
    parser.add_argument("-c", "--csv", help = "CSV filename.")

    args = parser.parse_args()
    sco_fname = args.score
    csv_fname = args.csv

    print('Running script on {} filename...'.format(sco_fname))

    sco = music21.converter.parse(sco_fname)
    outfile = csv_fname.rstrip('.csv') + '-annotated.xml'

    main(sco, csv_fname, outfile)