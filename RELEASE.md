# Releases

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