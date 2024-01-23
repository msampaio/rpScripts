# Releases

## Next release

### Features added
- Charts of number of parts and density numbers values.

### Improvements

- Add missing information in the documentation.

## 2.1

### Features added

- New texture class calculator and plotter

### Improvements

- New Statistics auxiliary class

## 2.0.1

### Improvements

- Sloping-x option documentation

### Bug fixes

- Offset map creation
- Annotation file creation
- Minor writing fix
- Large offset fractions approximation
- Missing methods documentation addition

## 2.0

### Deprecated

- Moved ``RPC`` to ``calculator``
- Moved ``RPP`` to ``plotter``
- Moved ``RPA`` to ``annotator``
- Moved ``RPL`` to ``labeler``
- Moved multi-``CSV``-based to ``JSON``-based

### Features added

- New Command line interface
- Trimmer
- Converter (to ``CSV`` format)
- Statistical data printer
- Lattice map generator
- Sphinx documentation
- PIP package generator
- Binary generator
- `partition` module
- New modules with hacking-easy classes
- Memory optimization: position and duration events replace equally-size based events
- Frequency analysis calculator
- Probability calculator
- Docstrings
- New chart settings options

## 1.1

### Features added

- Rhythmic Partitioning Labeler script
- RPP refactoring (class based)
- Bubble partitiogram
- Comparative partitiogram
- Partitiogram dimensions as script options
- Documentation improvement
- Abstract classes for charts
- Optional CSV rendering without equal durations
- Functional tests (RPC)
- Annotation from MIDI files.

### Bug fixes

- Parsing of chords with notes with distinct tie values
- Kern parsing
- Events' duration calculating
- CSV format reading
- Example image's legends

## 1.0

### Features added

- RP Scripts documentation
- Standalone RPC Script
  - MusicXML, KRN and MIDI parser (Music21 based).
  - Rhythmic Partitioning calculator.
  - Output containing events with equal durations.
- Standalone RPP Script
  - Partitiogram
  - Multiple indexogram types: stairs, stem, combined, and standard (with and without bubble closing' vertical lines)
  - Image format selection (svg, png, jpg)
- Standalone RPA Script
  - Annotation in new MusicXML file.
  - Generation from given MusicXML and Kern files. It doesn't work with MIDI.
- Usage examples