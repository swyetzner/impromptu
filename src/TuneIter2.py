# install midi library here: https://github.com/vishnubob/python-midi/
import midi
import math
import itertools
import sys
import abc
import json
#sys.path.insert(0, '../tests/WAVTestFiles/Test1')
sys.path.insert(0, '/support/')
import os
import subprocess
#from convert import *
#import convert
#from pydub import AudioSegment
#import pyaudio




class Duration(object):
    SIXTEENTH = (1,16)
    EIGHTH = (1,8)
    QUARTER = (1,4)
    HALF = (1,2)
    WHOLE = (1,1)

class Clef(object):
    TREBLE, BASS = range(2)

class Accidental(object):
    NATURAL, SHARP, FLAT = range(3)

class Helper(object):
    @staticmethod
    def floatComp(a,b, threshold):
        if(abs((a-b)) < threshold):
            return True
        else:
            return False


class Pitch(object):

    # Column index for Note Number, refer to http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/midi_note_numbers_for_octaves.htm
    # where C4 is 60, not 72, that is shift octaves down one
    # also refer to https://usermanuals.finalemusic.com/Finale2012Mac/Content/Finale/MIDI_Note_to_Pitch_Table.htm
    letterNotes = {0 : 'c', 1 : 'c#', 2 : 'd', 3 : 'd#', 4 : 'e', 5 : 'f', 6 : 'f#', 7 : 'g', 8 : 'g#', 9 : 'a', 10 : 'a#', 11 : 'b'}

    def __init__(self, **kwargs):
        MIDINote = kwargs.get('MIDINote', None)
        if MIDINote:
            returnPitch = self.MIDInotetoPitch(MIDINote) 
            self.letter = returnPitch.letter
            self.octave = returnPitch.octave
            self.accidental = returnPitch.accidental

        else:
            self.letter = kwargs.get('letter', None)
            if self.letter != None:
                self.letter = self.letter.lower()
            self.octave = kwargs.get('octave', None)
            self.accidental = kwargs.get('accidental', Accidental.NATURAL)

    def pitchEqual(self, p):
        if (p.letter == self.letter) and (p.accidental == self.accidental) and (p.octave == self.octave):
            return True
        return False

    def setLetter(self, letter):
        self.letter = letter

    def setOctave(self, octave):
        self.octave = octave

    def setAccidental(self, accidental):
        self.accidental = accidental

    @classmethod
    # takes a MIDI note and generates a Pitch instance (e.g. MIDI note 60 is pitch C4)
    # one to one mapping between MIDI notes and pitches on the piano
    def MIDInotetoPitch(cls, MIDIint):
        octaveTemp = int(MIDIint-12)/12
        letterTemp = cls.letterNotes.get(int(MIDIint-12)%12)
        if '#' in letterTemp:
            letterTemp = letterTemp.strip('#')
            accidentalTemp = Accidental.SHARP
        else:
            accidentalTemp = Accidental.NATURAL
        return cls(octave=octaveTemp, letter=letterTemp, accidental = accidentalTemp)

    def PitchtoString(self):
        acc = {Accidental.NATURAL: '', Accidental.SHARP: '#', Accidental.FLAT: 'Flat'}.get(self.accidental)
        return "Pitch: " + str(self.letter) + str(self.octave) + acc

class Event(object):
    def __init__(self, **kwargs):
        self.duration = kwargs.get('duration', Duration.QUARTER)
        if (kwargs.get('onset') != None) and (kwargs.get('onset') >= 0):
            self.onset = kwargs.get('onset')
        else:
            self.onset = None
        self.duration = kwargs.get('duration', Duration.QUARTER)
        # duration in seconds
        self.s_duration = kwargs.get('s_duration', None)

    @abc.abstractmethod
    def getPitch(self):
        """Method that should be implemented in subclasses."""

    def eventEqual(self, event):
        if self.duration != event.duration or self.onset != event.onset:
            return False
        if type(self) == type(event):
            if isinstance(self, Chord):
                return self.chordEqual(event)
            if isinstance(self, Note):
                return self.noteEqual(event)
            else: # is rest
                return True

    def editEvent(self, event):
        if event.duration != None:
            self.duration = event.duration
        if type(self) == type(event):
            if isinstance(self, Chord) and isinstance(event, Chord):
                return self.editChord(event)
            if isinstance(self, Note) and isinstance(event, Note):
                return self.editNote(event)

    def isRest(self):
        if isinstance(self, Rest):
            return True
        return False

    def setDuration(self, duration):
        self.duration = duration

    def setOnset(self, onset):
        if onset >= 0: self.onset = onset

    @abc.abstractmethod
    def setPitch(self, pitch):
        """Method that should be implemented in subclasses."""

class Chord(Event):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.pitches = kwargs.get('pitches', [])
    def getPitch(self):
        return self.pitches

    def chordEqual(self, chord):
        if self.duration != chord.duration or self.onset != chord.onset:
            return False
        if len(chord.pitches) != len(self.pitches):
            return False
        for i in range(0, len(chord.pitches)):
            if self.pitches[i].pitchEqual(chord.pitches[i]) == False:
                return False
        return True

    def editChord(self, chord):
        if chord.getPitch != None:
            self.setPitches(chord.getPitch)

    def addPitch(self, event):
        if self.getPitch() != None:
            self.setPitch(self.getPitch().extend(event))
        else:
            self.setPitch(event.getPitch())

    def setPitch(self, listofPitches):
        self.pitches = listofPitches

class Rest(Event):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
    def getPitch(self):
        return [Pitch(letter= 'r')]
    def setPitch(self, pitch):
        print "Cannot change pitch of a rest. Please delete event."
        return
    def NotetoString(self):
        durationstring = {Duration.SIXTEENTH: 'Sixteenth', Duration.EIGHTH: 'Eighth', Duration.QUARTER: 'Quarter', Duration.HALF: 'Half', Duration.WHOLE: 'Whole' }.get(self.duration)
        return "Rest: Duration (seconds) - %s, Duration - %s, Onset - %s \n" %(str(self.s_duration), durationstring, str(self.onset))        

class Note(Event):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.pitch = kwargs.get('pitch', None)
        self.frequency = kwargs.get('frequency', None)
        if self.pitch == None and self.frequency != None:
            self.pitch = self.convertFreqToPitch(self.frequency)
    
    def getPitch(self):
        return [self.pitch]

    # wrapper constructor to create Rest Note
    @classmethod
    def Rest(cls, **kwargs):
        return cls(duration = kwargs.get('duration'), s_duration = kwargs.get('s_duration'), frequency = 0.0, onset = kwargs.get('onset'), pitch = Pitch(letter = 'r'))

    def setPitch(self, p):
        self.pitch = p

    def editNote(self, note):
        if note.pitch != None:
            self.setPitch(note.pitch)

    def NotetoString(self):
        durationstring = {Duration.SIXTEENTH: 'Sixteenth', Duration.EIGHTH: 'Eighth', Duration.QUARTER: 'Quarter', Duration.HALF: 'Half', Duration.WHOLE: 'Whole' }.get(self.duration)
        return "Note: Freq - %s, Duration (seconds) - %s, Duration - %s, Onset - %s \n \t %s" %(str(self.frequency), str(self.s_duration), durationstring, str(self.onset), self.pitch.PitchtoString())

    def isRest(self):
        if self.pitch.letter == 'r':
            return True
        else:
            return False

    @staticmethod
    def convertFreqToPitch(freq):
        # refer to http://stackoverflow.com/questions/20730133/extracting-pitch-features-from-audio-file
        MIDINote = round(12*math.log(freq/440.0, 2) + 69)
        return Pitch(MIDINote=MIDINote)

    @staticmethod
    def frequencyEqual(freq1, freq2):
        # frequency bounded in [20, 4200] because in human hearing range
        if min(freq1, freq2) < 20 or max(freq1, freq2) > 4200:
            return False
        return Helper.floatComp(freq1, freq2, 4)

    def noteEqual(self, n):
        #if math.isclose (n.frequency, self.frequency):
        #if math.isclose (n.onset, self.onset):
        if Pitch.pitchEqual(self.pitch, n.pitch) and (self.duration == n.duration):# and (self.onset == n.onset):
            return True
        return False

    def isRest(self):
        if self.pitch.letter == 'r':
            return True
        return False

class Key(object):
    def __init__(self, **kwargs):
        self.isMajor = kwargs.get('isMajor', True)
        self.pitch = kwargs.get('pitch', Pitch())

    def keyEqual(self, k):
        if (k.isMajor == self.isMajor) and Pitch.pitchEqual(self.pitch, k.pitch):
            return True
        return False

    def KeytoString(self):
        buf = 'Key Signature - %s ' %(self.pitch.PitchtoString())
        if (self.isMajor):
            buf = buf + 'Major'
        else:
            buf = buf + 'Minor'
        return buf


# refer to vartec's answer at http://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
class Tune(object):

    def __init__(self, **kwargs):
        self.timeSignature = (4,4) # default time Signature
        self.keySignature = kwargs.get('keySignature')
        self.clef = kwargs.get('clef', Clef.TREBLE)
        # default title is midi file name
        self.title = self.setTitle(kwargs.get('title', kwargs.get('midi')))
        self.contributors = self.setContributors(kwargs.get('contributors', ['Add Contributors']))
        self.midifile = None
        self.events = None
        if kwargs.get('wav') != None and kwargs.get('wav').endswith('wav'):
            self.readWav(kwargs.get('wav'))
        elif kwargs.get('mp3') != None and kwargs.get('mp3').endswith('mp3'):
            raise NotImplementedError
        elif kwargs.get('midi') != None and kwargs.get('midi').endswith('.mid'):
            self.midifile = kwargs.get('midi')
            pattern = self.MIDItoPattern(self.midifile)
            if (pattern.format!=1): # will only look at first track, don't want type 0 MIDI file has all of the channel data on one track
                print "\n***\nWARNING: Conversion of format %d MIDI files with more than one track is currently not supported and is still in development\n***\n" %(pattern.format)
            for event in pattern[0]: # looking through midi header
                if isinstance(event, midi.TimeSignatureEvent):
                # [nn dd cc bb] refer to http://www.blitter.com/~russtopia/MIDI/~jglatt/tech/midifile/time.htm
                    self.timeSignature = (event.data[0], 2<<event.data[1])
            # override time sig in MIDI file
            if 'timeSignature' in kwargs:
                self.timeSignature = self.setTimeSignature(kwargs.get('timeSignature'))
            # first compute onset of Notes to construct list of Notes
            self.events = self.computeOnset(self.midifile)
            # then compute pitches of Notes
            i = 0
            for track in pattern:
                for event in track: # looking through first track
                    if isinstance(event, midi.NoteOnEvent):
                        self.events[i].setPitch(Pitch.MIDInotetoPitch(event.get_pitch()))
                        i += 1
            # then, insert rests
            self.events = self.calculateRests(self.events)
            # lastly, compute chords
            self.events = self.calculateRests(self.events)


    # wrapper constructor with only MIDI file as parameter
    @classmethod
    def TuneWrapper(cls, file):
        if file.endswith('.mid'):
            return cls(midi=file)
        elif file.endswith('.mp3'):
            return cls(mp3=file)
        elif file.endswith('.wav'):
            return cls(wav=file)


    def getKey(self):
        return self.keySignature

    def setKey(self, k):
        self.keySignature = k

    def setTitle(self, title):
        if title != None and len(title) < 64:
            self.title = title

    def getTitle(self):
        return self.title

    def setContributors(self, cont):
        self.contributors = []
        for i in range(len(cont)):
            if len(cont[i]) <= 64:
                self.contributors.append(cont[i])

    def getContributors(self):
        return self.contributors

    def getTimeSignature(self):
        return self.timeSignature

    def setTimeSignature(self, ts):
        self.timeSignature = ts
        for i in range(2):
            if ts[i] <= 0 or isinstance(ts[i], int) == False:
                self.timeSignature = (4,4)

    def setEventsList(self, lst):
        self.events = lst

    def getEventsList(self):
        return self.events

    def eventListToChords(self):
        for i in range(0,len(self.events)):
            if floatComp(self.events[i].onset,self.events[i+1].onset,0.001):
                if isinstance(self.events[i],Chord):
                    self.events[i].addPitch(self.events[i+1]) #checks chords and notes
                    self.events.pop(i+1)
                    i=i-1
                elif isinstance(self.events[i+1],Chord):
                    self.events[i+1].addPitch(self.events[i]) #checks chords and notes
                    self.events.pop(i)
                    i=i-1
                elif isinstance(self.events[i],Note) and isinstance(self.events[i+1],Note):
                    self.events[i] = Chord(pitches = [self.events[i],self.events[i+1]] ,duration= self.events[i].duration,onset=self.events[i].onset)
                    self.events.pop(i+1)
                    i=i-1
                elif isinstance(self.events[i],Rest) and isinstance(self.events[i+1],Note):
                    self.events[i] = self.events[i+1]
                    self.events.pop(i+1)
                    i=i-1
                elif isinstance(self.events[i],Note) and isinstance(self.events[i+1],Rest):
                    self.events[i+1] = self.events[i]
                    self.events.pop(i)
                    i=i-1
                elif isinstance(self.events[i],Rest) and isinstance(self.events[i+1],Rest):
                    self.events.pop(i+1)
                    i = i-1

    def addEvent(self, idx, event):
        self.events.insert(idx, event)

    def deleteEvent(self, idx):
        del self.events[idx]

    def editEvent(self, idx, event):
        # event contains new information (can be subset), so update original event 
        # with new info
        self.events[idx] = self.events[idx].editEvent(event)

    def eventsListEquals(self, list2):
        if len(self.getEventsList()) != len(list2):
            return False
        for i in range(0, len(list2)):
            if list2[i].eventEqual(self.getEventsList()[i]) == False:
                return False
        return True

    def durationTunetoJSON(self, tup):
        if tup == (1,1):
            return 'WHOLE'
        elif tup == (1,2):
            return 'HALF'
        elif tup == (1,4):
            return 'QUARTER'
        elif tup == (1,8):
            return 'EIGHTH'
        elif tup == (1,16):
            return 'SIXTEENTH'

    def writePitchtoFile(self, pitch, myfile):
        letter = ''
        octave = ''
        accidental = ''
        if pitch.letter != None:
            letter = pitch.letter
        if pitch.octave != None:
            octave = str(pitch.octave)
        if pitch.accidental != None:
            accidental = str(pitch.accidental)
        myfile.write('\t\t\t\t"pitch":{\n\t\t\t\t\t"letter":"%c",\n\t\t\t\t\t"octave":"%s",\n\t\t\t\t\t"accidental":"%s"\n\t\t\t\t}\n' %(letter, octave, accidental))

    def TunetoJSON(self):
        if self.title != None:
            filename = 'tune-' + self.title + '.json'
        else:
            filename = 'tune-generic.json'
        f = open(filename, 'w')
        
        f.write('{\n')
        f.write('\t"tune": {\n')
        
        f.write('\t\t"timeSignature": ["%d","%d"],\n' %(self.timeSignature[0], self.timeSignature[1]))
        
        f.write('\t\t"clef": "%d",\n' %(self.clef))
        
        if self.title != None:
            f.write('\t\t"title": "%s",\n' %(self.title))
        else:
            f.write('\t\t"title": "",\n')

        f.write('\t\t"contributors": [')
        if self.contributors != None:
            n_contributors = len(self.contributors)
            for num in (0, n_contributors - 1):
                f.write('"%s"' %(self.contributors[num]))
                if num != n_contributors - 1:
                    f.write(',')
        f.write('],\n')

        f.write('\t\t"events":[\n')
        events = self.getEventsList()
        e_len = len(events)
        for x in range(0, e_len):
            event = events[x]
            f.write('\t\t\t{\n')
            if isinstance(event, Chord):
                f.write('\t\t\t\t"class":"chord",\n')
                f.write('\t\t\t\t"duration":"%lf",\n' %(event.duration))
                f.write('\t\t\t\t"s_duration":"%lf",\n' %(event.s_duration))
                f.write('\t\t\t\t"frequency":"%lf",\n' %(event.frequency))
                f.write('\t\t\t\t"onset":"%lf",\n' %(event.onset))
                
                f.write('\t\t\t\t"pitches":[\n')
                pitches = event.getPitch()
                n_pitches = len(pitches)
                for n in range(0, n_pitches):
                    f.write('\t\t\t\t\t{\n')
                    f.write('\t\t\t\t\t"letter":"%c",\n' %(pitches[n].letter))
                    f.write('\t\t\t\t\t"octave":"%d",\n' %(pitches[n].octave))
                    f.write('\t\t\t\t\t"accidental":"%d",\n' %(pitches[n].accidental))
                    f.write('\t\t\t\t\t}')
                    if n != n_pitches-1:
                        f.write(',\n')
                    else:
                        f.write('\n')
                f.write('\t\t\t\t],\n')
                f.write('\t\t\t}')
            elif isinstance(event, Note):
                f.write('\t\t\t\t"class":"note",\n')

                if event.duration != None:
                    dur_str = self.durationTunetoJSON(event.duration)
                    f.write('\t\t\t\t"duration":"%s",\n' %(dur_str))
                else:
                    f.write('\t\t\t\t"duration":"",\n')

                if event.duration != None:
                    f.write('\t\t\t\t"s_duration":"%lf",\n' %(event.s_duration))
                else:
                    f.write('\t\t\t\t"s_duration":"",\n')

                if event.frequency != None:
                    f.write('\t\t\t\t"frequency":"%lf",\n' %(event.frequency))
                else:
                    f.write('\t\t\t\t"frequency":"",\n')

                f.write('\t\t\t\t"onset":"%lf",\n' %(event.onset))

                self.writePitchtoFile(event.pitch, f)
            elif isinstance(event, Rest):
                f.write('\t\t\t\t"class":"rest",\n')

                if event.duration != None:
                    dur_str = self.durationTunetoJSON(event.duration)
                    f.write('\t\t\t\t"duration":"%s",\n' %(dur_str))
                else:
                    f.write('\t\t\t\t"duration":"",\n')

                if event.duration != None:
                    f.write('\t\t\t\t"s_duration":"%lf",\n' %(event.s_duration))
                else:
                    f.write('\t\t\t\t"s_duration":"",\n')

                f.write('\t\t\t\t"onset":"%lf",\n' %(event.onset))

                f.write('\t\t\t\t"pitch":{\n')  
                f.write('\t\t\t\t\t"letter":"r",\n') 
                f.write('\t\t\t\t\t"octave":"",\n') 
                f.write('\t\t\t\t\t"accidental":""\n')  
                f.write('\t\t\t\t}\n')      

            f.write('\t\t\t}')
            if x != e_len-1:
                f.write(',\n')
            else:
                f.write('\n')           

        f.write('\t\t],\n')

        keysig = self.keySignature
        if keysig == None:
            f.write('\t\t"keySignature": {}\n')
        else:
            f.write('\t\t"keySignature": {\n')
            if keysig.isMajor != None:
                f.write('\t\t\t"isMajor":"%s",\n' %(keysig.isMajor))
            else:
                f.write('\t\t\t"isMajor":"",\n')
            f.write('\t\t\t')
            writePitchtoFile(keysig.pitch, f)
            f.write('\t\t}\n')

        f.write('\t}\n')
        f.write('}\n')

        f.close

    def pitchJSONtoTune(self, pitch):
        if pitch['accidental'] != '':
            ksig_pitch_accidental = int(pitch['accidental'])
        else:
            ksig_pitch_accidental = ''
        ksig_pitch_letter = str(pitch['letter'])
        if pitch['octave'] != '':
            ksig_pitch_octave = int(pitch['octave'])
        else:
            ksig_pitch_octave = ''
        pitch = Pitch(accidental=ksig_pitch_accidental, letter=ksig_pitch_letter, octave=ksig_pitch_octave)
        return pitch

    def durationJSONtoTune(self, dur_str):
        if dur_str == 'SIXTEENTH':
            dur = Duration.SIXTEENTH
        elif dur_str == 'EIGHTH':
            dur = Duration.EIGHTH
        elif dur_str == 'QUARTER':
            dur = Duration.QUARTER
        elif dur_str == 'HALF':
            dur = Duration.HALF
        elif dur_str =='WHOLE':
            dur = Duration.WHOLE
        return dur

    def eventJSONtoTune(self, event):
        onset = float(event['onset'])
        duration = self.durationJSONtoTune(str(event['duration']))   
        #new_event = Event(duration=duration, onset=onset)

        if event['class'] == 'note':
            new_event = Note(duration=duration, onset=onset)
            n_frequency = float(event['frequency'])
            n_pitch = self.pitchJSONtoTune(event['pitch'])
            new_event.frequency = n_frequency
            new_event.setPitch(n_pitch)
        elif event['class'] == 'rest':
            new_event = Rest(duration=duration, onset=onset)
        elif event['class'] == 'chord': 
            new_event = Chord(duration=duration, onset=onset)
            pitches = []
            for p in event['pitches']:
                pch = pitchJSONtoTune(p)
                pitches.append(p)
            new_event.setPitch(pitches)
        return new_event
            

    def JSONtoTune(self, json_file):
        json_data = json.load(json_file)
        json_tune = json_data['tune']

        tune_title = json_tune['title']
        
        tune_contributors = []
        for contri in json_tune['contributors']:
            tune_contributors.append(str(contri))

        tune_clef = int(json_tune['clef'])

        tune_tsig1 = int(json_tune['timeSignature'][0])
        tune_tsig2 = int(json_tune['timeSignature'][1])
        tune_tsig = (tune_tsig1, tune_tsig2)

        tune_ksig_pitch = self.pitchJSONtoTune(json_tune['keySignature']['pitch'])
        iMflag = str(json_tune['keySignature']['isMajor'])
        iMflag.lower()
        ksigisMajor = True
        if iMflag == 'true':
            ksig_isMajor = True
        if iMflag == 'false':
            ksigisMajor = False
        tune_ksig = Key(pitch=tune_ksig_pitch, isMajor=ksigisMajor)

        tune_events = []
        for event in json_tune['events']:
            new = self.eventJSONtoTune(event)
            tune_events.append(new)

        self.setTitle(tune_title)
        self.setContributors(tune_contributors)
        self.clef = tune_clef
        self.setTimeSignature(tune_tsig)
        self.setKey(tune_ksig)
        self.setEventsList(tune_events)

    @staticmethod
    def convertFreqToPitch(freqlist):
        # return list of pitches
        pitchlist = []
        for freq in freqlist:
            # refer to http://stackoverflow.com/questions/20730133/extracting-pitch-features-from-audio-file
            pitchlist.append(Note.convertFreqToPitch(freq))
        return pitchlist

    ## SHOULD WE MOVE ticketsToTime and computeOnset methods to Event class?

    # turns ticks to time in seconds
    # The formula used is:
    # (# ticks * 60) / (BPM * resolution)
    @staticmethod
    def ticksToTime(ticks, bpm, resolution):
        return (ticks * 60) / (bpm * resolution)

    # takes in a duration in seconds, returns Duration enum value
    # 1 second = quarter note
    @staticmethod
    def secondsToDuration(dur):
        if (dur <= 0):
            return Duration.SIXTEENTH
        approx_power = math.log(1/dur, 2)
        note_val = 4 - (round(approx_power) + 2)
        Dur_array = [Duration.SIXTEENTH, Duration.EIGHTH, Duration.QUARTER, Duration.HALF, Duration.WHOLE]
        if note_val < 0:
            return None
        if note_val >= 4:
            # next iteration: add greater variety of note durations, e.g. combination of notes
            return Duration.WHOLE
        else: 
            return Dur_array[int (note_val)]

    # Reads a MIDI file in, returns a list of Notes
    # Notes are populated with onset and duration
    # assumes a one track MIDI file with notes in chronological order

    def computeOnset(self, myfile):
        pattern = self.MIDItoPattern(myfile)
        NotesList = []
        index = 0
        bpm = 0
        resolution = pattern.resolution
        s_duration = 0
        # changes ticks to cumulative values
        pattern.make_ticks_abs() 
        for track in pattern:
            for event in track:
                if isinstance(event, midi.SetTempoEvent):
                    bpm = event.bpm
                if isinstance(event, midi.NoteEvent):
                    if (isinstance(event, midi.NoteOffEvent) or (isinstance(event, midi.NoteOnEvent) and event.data[1] == 0)):
                        endset = self.ticksToTime(event.tick, bpm, resolution)
                        currNote = NotesList[index]
                        s_duration = endset - currNote.onset
                        currNote.s_duration = s_duration
                        currNote.duration = self.secondsToDuration(s_duration)
                        index += 1
                    else:
                        onset = self.ticksToTime(event.tick, bpm, resolution)
                        # print onset
                        newNote = Note(onset = onset)
                        NotesList.append(newNote)
        return NotesList

    # Takes a list of pitched Notes, returns a list of Notes with the included rests
    def calculateRests(self, list_of_notes):
        n_notes = len(list_of_notes)
        allNotes = []
        for i in range(0, n_notes-1):
            allNotes.append(list_of_notes[i])
            noteonset = list_of_notes[i].onset if list_of_notes[i].onset!=None else 0
            noteduration = list_of_notes[i].s_duration if list_of_notes[i].s_duration!= None else 0
            onset = noteonset + noteduration
            s_duration = list_of_notes[i+1].onset - onset
            duration = self.secondsToDuration(s_duration)
            if (duration != None): # duration is too small to consider as a rest
                #r_pitch = Pitch(letter="r")
                rest = Rest(duration=duration, s_duration=s_duration, onset=onset)
                allNotes.append(rest)
            if i == n_notes-2:
                allNotes.append(list_of_notes[n_notes-1])
        return allNotes

    # convert MIDI file to Pattern
    @staticmethod
    def MIDItoPattern(file):
        return midi.read_midifile(file)

    def TunetoString(self):
        clefstring = {Clef.BASS: 'Bass', Clef.TREBLE: 'Treble'}.get(self.clef)
        if (self.getKey() == None):
            keystring = 'None'
        else:
            keystring = self.getKey().KeytoString()
        buf = "Tune: \nTitle - %s, Contributors - %s \n\tTime Sig - %s, %s, Clef - %s\nList of Notes:\n" %(self.title, str(self.contributors), str(self.timeSignature), keystring, clefstring)
        for note in self.getEventsList():
            buf = buf + "%s\n" %(note.NotetoString())
        return buf

    def notesListEquals(self, Notelist1, Notelist2):
        if len(Notelist1) != len(Notelist2):
            return False
        for i in range(len(Notelist1)):
            if Notelist1[i].noteEqual(Notelist2[i]) == False:
                return False
        return True
    
    #aubio output array to event list using pitches
#    def readWav(self, file):
#        ofArray=[]
#        f = open(file, 'r+')
#        for line in f.read().splitlines():
#            ofArray = ofArray+[line.split()]
#        events = []
#        for pair in ofArray:
#            if float(pair[1]) > 0:
#                events = events+[Note(onset=float(pair[0]), frequency=float(pair[1]))]
#            else:
#                events = events+[Rest(onset=float(pair[0]))]
#        self.setEventsList(events)



    #aubio output array to event list using aubionotes
    def readWav(self, filename):
            ofArray=[]
            f= subprocess.check_output(["aubionotes", "-i", filename])
            raw = f.splitlines()
            raw.pop(0)
            for line in raw:
                ofArray = ofArray+[line.split()]
            events = []
            print raw
            for tuple in ofArray:
                sdur = float(tuple[2]) - float(tuple[1])
                p = Pitch()
                p = p.MIDInotetoPitch(math.floor(float(tuple[0])))
                events = events+[Note(pitch=p, onset=float(tuple[1]), s_duration=sdur, duration = self.secondsToDuration(sdur))]
            self.setEventsList(events)



#    def mp3ToWav(self,fileprefix):
#        sound = AudioSegment.from_mp3(file)
#        prefix = file.split(str='.')
#        sound.export(prefix[0], format="wav")

                                   
# main function used for testing of Tune.py separate from web integration
if __name__ == "__main__":
    # default parameters
    INPUT_FILE = '../tests/MIDITestFiles/c-major-scale-treble.mid'
    # Sets parameters and files
    for i in xrange(1,len(sys.argv)):
        if (sys.argv[i] == '-f'): # input flag: sets input file name
            INPUT_FILE = sys.argv[i+1]
    dummyInstance = Tune()
#    print dummyInstance.MIDItoPattern(INPUT_FILE)
    tune = Tune.TuneWrapper(INPUT_FILE)
#    print tune.TunetoString()

    file1 = '../tests/MIDITestFiles/tune-with-chord-rest-note.mid'
    tune = Tune.TuneWrapper(file1)
#    runConvert('../tests/WAVTestFiles/Test1/')
    tuneWav = Tune(wav = 'test1.wav')
    print tuneWav.TunetoString()

                                   
