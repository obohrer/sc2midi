# sc2midi
Small EXPERIMENT to produce MIDI files from starcraft 2 replays.
Notes are separated in 2 groups (low/high) and attributed to a player.
Volume and duration of notes depend of ability usage frequency.
Time in MIDI file is scaled down to have smaller "songs" :)

## Dependencies
* sc2reader (https://github.com/GraylinKim/sc2reader)
* midiutil (https://code.google.com/p/midiutil/)

## Usage
```
python sc2midi.py path-to-replay
```
