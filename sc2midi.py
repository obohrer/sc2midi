import random
import sys
import sc2reader
from collections import defaultdict
from midiutil.MidiFile import MIDIFile

def is_player_action(e):
  return isinstance(e,sc2reader.events.PlayerActionEvent)

def ability2code(x):
  try:
    return x.ability_code
  except:
    return str(x.__class__)

def load_replay(filename):
  r = sc2reader.load_replay(filename)
  return r.players, r.events
    
class Note:
  def __init__(self, player_index, ts, index):
    self.player_index = player_index
    self.ts = ts
    self.index = index

class ReplayGenerator:
  def __init__(self,players, events):
    self.players = players
    
    self.players_indices = {}
    for i, pid in enumerate(map(lambda x:x.pid, players)):
      self.players_indices[pid-1] = i
    
    # notes range for each player
    self.free = [[x for x in xrange(1,50)], [x for x in xrange(51,100)]]
    map(random.shuffle, self.free)
    
    # assigned notes
    self.notes = [{},{}]
    self.tempo = 120
    self.channel = 0
    self.events = events
    self.midi = MIDIFile(2)

  def pid_to_index(self,pid):
    return self.players_indices[pid]
    
  def generate_note_index(self, pid, code):
    if not code in self.notes[pid]:
      self.notes[pid][code] = self.free[pid].pop()
    return self.notes[pid][code]

  def ability2note(self,ability):  
    code = ability2code(ability)
    pid = self.pid_to_index(ability.pid)
    note_index = self.generate_note_index(pid,code)
    return Note(pid, (ability.frame/64.0)*self.tempo*2/60, note_index)
  
  def abilities2notes(self,abilities):
    return map(self.ability2note, abilities)
  
  def extract_abilities(self):
    abilities = filter(is_player_action, self.events)
    return filter(lambda x: x.pid in self.players_indices, abilities)

  def generate_midi(self):
    abilities = self.extract_abilities()
    notes = self.abilities2notes(abilities)
    
    # track name and tempo.
    self.midi.addTrackName(0,0, self.players[0].name)
    self.midi.addTempo(0,0,self.tempo)
    self.midi.addTrackName(1,0, self.players[1].name)
    self.midi.addTempo(1,0,self.tempo)

    # compute freq of notes
    frequencies = defaultdict(int)
    notes_count = len(notes)
    for note in notes:
      frequencies[note.index] += 1.0/notes_count
    
    for note in notes:
      self.midi.addNote(note.player_index,self.channel,note.index,note.ts,
                        int((1.0-frequencies[note.index])*2)+0.5,
                        int((1.0-frequencies[note.index])*50)+50)
    return self.midi

def replay2midi(filename):
  players, events = load_replay(filename)
  generator = ReplayGenerator(players, events)
  midi = generator.generate_midi()
  match_name = '_vs_'.join(map(lambda x:x.name, players))
  midi_filename = format("%s.mid" % (match_name))
  binfile = open(midi_filename, 'wb')
  midi.writeFile(binfile)
  binfile.close()
  print "exported midi to %s" % (midi_filename)

if __name__ == "__main__":
    replay2midi(sys.argv[1])