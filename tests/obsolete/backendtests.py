import unittest
import midi
import sys
sys.path.insert(0, '../src')
import os 
from Tune import *

#Please refer to class diagram for reference on parameter values for constructors and methods
class TestImpromptuBackend(unittest.TestCase):
	
	def testpitchequal(self):
		# print "RUNNING: testpitchequal ..."
		#Testing equality of the same note
		pitch = Pitch(letter='b', octave=4, accidental=Accidental.FLAT)
		samePitch = Pitch(letter='b', octave=4, accidental=Accidental.FLAT)
		self.assertTrue(pitch.pitchEqual(samePitch))
		
		#Testing equality of different notes
		differentLetter = Pitch(letter='c', octave=4, accidental=Accidental.FLAT)
		differentOctave = Pitch(letter='b', octave=5, accidental=Accidental.FLAT)
		differentAccidental = Pitch(letter='b', octave=4, accidental=Accidental.NATURAL)
		self.assertFalse(pitch.pitchEqual(differentLetter))
		self.assertFalse(pitch.pitchEqual(differentOctave))
		self.assertFalse(pitch.pitchEqual(differentAccidental))

		# print "PASSED"
	
	def testPitchGetterSetter(self):
		# print "RUNNING: testPitchGetterSetter ..."
		pitch = Pitch(letter='b', octave=4, accidental=Accidental.FLAT)
		note = Note(frequency=493.88, onset=0.0)
		note.setPitch(pitch)
		self.assertTrue(pitch.pitchEqual(note.getPitch()))
		# print "PASSED"

	def testIsRest(self):
		# print "RUNNING: testIsRest ..."
		#Testing rest
		restPitch = Pitch(letter='r')
		rest = Note()
		rest.setPitch(restPitch)
		self.assertTrue(rest.isRest())
		
		#testing note
		notePitch = Pitch(letter='b', octave=4, accidental=Accidental.NATURAL)
		note = Note()
		note.setPitch(notePitch)
		self.assertFalse(note.isRest())

		# print "PASSED"
	
	def testNoteEqual(self):
		# print "RUNNING: testNoteEqual ..."
		#Testing same notes
		notePitch = Pitch(letter='b', octave=4, accidental=Accidental.NATURAL)
		note = Note(frequency=493.88, onset=0.0, duration=Duration.QUARTER, pitch=notePitch)

		samePitch = Pitch (letter='b', octave=4, accidental=Accidental.NATURAL)
		sameNote = Note(frequency=493.88, onset=0.0, duration=Duration.QUARTER, pitch=samePitch)
		self.assertTrue(note.noteEqual(sameNote))

		#Testing different notes
		differentPitch = Pitch (letter='c', octave=5, accidental=Accidental.FLAT)
		diffPitchNote = Note(frequency=493.88, onset=0.0, duration=Duration.QUARTER, pitch=differentPitch)
		self.assertFalse(note.noteEqual(diffPitchNote))

		diffFreqNote = Note(frequency=350.0, onset=0.0, duration=Duration.QUARTER, pitch=samePitch)
		self.assertFalse(note.noteEqual(diffFreqNote))

		diffOnsetNote = Note(frequency=493.88, onset=40.0, duration=Duration.QUARTER, pitch=samePitch)
		sameNote.setPitch(samePitch)
		self.assertTrue(note.noteEqual(diffOnsetNote)) # changed from assertFalse because notes with different onsets should still be the same note

		diffDurationNote = Note(frequency=493.88, onset=0.0, duration=Duration.EIGHTH, pitch=samePitch)
		sameNote.setPitch(samePitch)
		self.assertFalse(note.noteEqual(diffDurationNote))

		rest = Pitch (letter='r')
		restNote = Note(frequency=0, onset=0.0)
		note.setPitch(rest)

		samerest = Pitch (letter='r')
		samerestNote = Note(frequency=0, onset=0.0)
		note.setPitch(samerest)
		self.assertTrue(samerestNote.noteEqual(samerestNote))

		# print "PASSED"

	# This test is unnecessary because we do not need to read Frequencies from MIDI files to compute note pitches.
	# This instead will be needed for iteration 2 with audio files.
	# def testComputeFrequency(self):
	# 	# check frequencies are calculated correctly from computeFrequency
	# 	# import midi file: first 3 notes of C major scale as all quarter notes (refer to TestComputePitches)
	# 	# Use Python MIDI library https://github.com/vishnubob/python-midi
	# 	# MIDI files are an array of integers with a header
	# 	TuneMIDI = midi.read_midifile("../tests/MIDITestFiles/c-major-scale-treble.mid")
	# 	frequencies = [261.63, 293.66, 329.63]
	# 	# check frequencies and onsets calculated correctly from generateTune
	# 	for i in xrange(0, 3):
	# 		self.assertEqual(readFrequency(), frequencies[i])

	def testcomputeOnset(self):
		print "RUNNING: testcomputeOnset ..."
		# check onsets are calculated correctly from computeOnset
		TuneMIDI = midi.read_midifile("../tests/MIDITestFiles/c-major-scale-treble.mid")
		for i in xrange(0, 3):
			self.assertEqual(computeOnset(TuneMIDI[i]), i)

		# print "PASSED"

	def testcreateTune(self):
		# print "RUNNING: testcreateTune ..."
		# --- tests if MIDI files are successfully converted to a Tune object ---
		# import midi file: C major scale with all quarter notes (refer to TestComputePitches)
		# Use Python MIDI library https://github.com/vishnubob/python-midi
		# MIDI files are an array of integers with a header
		TuneMIDI = midi.read_midifile("../tests/MIDITestFiles/c-major-scale-treble.mid")
		# ---- Fail Tune Parameter Constraints ---
		self.assertFalse(Tune("wrongFileType.txt"), Clef.TREBLE, "", [""])
		#  timeSignature has to be (int, int) where int > 0
		self.assertFalse(Tune(TuneMIDI), (-1, 0), Clef.BASS, "Title", ["Contributor"])
		self.assertFalse(Tune(TuneMIDI, (2.5, 3), Clef.BASS, "Title", ["Contributor"]))
		tune = Tune(TuneMIDI, (3,4), Clef.TREBLE, "Title", ["Contributor"])
		# --- test Tune setters and getters ---
		# If bad input, leave field unchanged
		tune.setTimeSignature((4,4))
		self.assertEqual(tune.getTimeSignature(), (4,4))
		tune.setTimeSignature((-1, 0))
		self.assertEqual(tune.getTimeSignature(), (4,4))
		tune.setTitle("new title")
		self.assertEqual(tune.getTitle(), "new title")
		tune.setTitle("this is toooooooooooooooooooooooooooooooooooooooooooo long title")
		self.assertEqual(tune.getTitle(), "new title")
		tune.setContributors(["person1, person2, person3"])
		self.assertEqual(tune.getContributors(), ["person1, person2, person3"])
		tune.setContributors(["this is tooooooooooooooooooooooooooooooooo long contributor name"])
		self.assertEqual(tune.getContributors(), ["person1, person2, person3"])

		frequencies = [261.63, 293.66, 329.63]
		# check frequencies and onsets calculated correctly from generateTune
		for i in xrange(0, 3):
			self.assertEqual(tune[i].getFrequency(), frequencies[i])
			self.assertEqual(tune[i].getOnset(), i)
			self.assertTrue(samerest.noteEqual(samerestNote))

		# print "PASSED"
		
	# This test is unnecessary because we do not need to read Frequencies from MIDI files to compute note pitches.
	# This instead will be needed for iteration 2 with audio files.
	# def testcomputeFrequency(self):
	# 	# check frequencies are calculated correctly from computeFrequency
		
	# 	# import midi file: first 3 notes of C major scale as all quarter notes (refer to TestComputePitches)
	# 	# Use Python MIDI library https://github.com/vishnubob/python-midi
	# 	# MIDI files are an array of integers with a header
	# 	TuneMIDI = midi.read_midifile("../tests/MIDITestFiles/c-major-scale-treble.mid")
		
	# 	frequencies = [261.63, 293.66, 329.63]
	# 	# check frequencies and onsets calculated correctly from generateTune
	# 	for i in xrange(0, 3):
	# 		self.assertEqual(readFrequency(TuneMIDI[i]), frequencies[i])
		
	def testcomputeOnset(self):
		# print "RUNNING: testcomputeOnset ..."
		# check onsets are calculated correctly from computeOnset
		TuneMIDI = Tune.TuneWrapper("../tests/MIDITestFiles/c-major-scale-treble.mid")
		for i in xrange(0, 15):
			self.assertEqual(round(TuneMIDI.getNotesList()[i].onset, 5), round(i*0.50505, 5))

		# print "PASSED"
		
	def testcreateTune(self):
		# print "RUNNING: testcreateTune ..."
		# --- tests if MIDI files are successfully converted to a Tune object ---
		
		# import midi file: C major scale with all quarter notes (refer to TestComputePitches)
		# Use Python MIDI library https://github.com/vishnubob/python-midi
		# MIDI files are an array of integers with a header
		TuneMIDI = Tune.TuneWrapper("../tests/MIDITestFiles/c-major-scale-treble.mid")
		
		# ---- Fail Tune Parameter Constraints ---
		self.assertTrue(Tune(midi = "wrongFileType.txt").midifile == None) 
		#  timeSignature has to be (int, int) where int > 0
		self.assertTrue(Tune(timeSignature = (-1, 0)).timeSignature == (4,4))
		self.assertTrue(Tune(timeSignature = (2.5, 3)).timeSignature == (4,4))
			
		# --- test Tune setters and getters ---
		# If bad input, leave field unchanged
		TuneMIDI.setTimeSignature((4,4))
		self.assertEqual(TuneMIDI.getTimeSignature(), (4,4))
		TuneMIDI.setTimeSignature((-1, 0))
		self.assertEqual(TuneMIDI.getTimeSignature(), (4,4))
		TuneMIDI.setTitle("new title")
		self.assertEqual(TuneMIDI.getTitle(), "new title")
		TuneMIDI.setTitle("this is toooooooooooooooooooooooooooooooooooooooooooo long title")
		self.assertEqual(TuneMIDI.getTitle(), "new title")
		TuneMIDI.setContributors(["person1, person2, person3"])
		self.assertEqual(TuneMIDI.getContributors(), ["person1, person2, person3"])
		TuneMIDI.setContributors(["this is toooooooooooooooooooooooooooooooooooooooooooooooooo long contributor name"])
		self.assertEqual(TuneMIDI.getContributors(), [])

		# print "PASSED"
		
		# frequencies = [261.63, 293.66, 329.63]
		# # check frequencies and onsets calculated correctly from generateTune
		# for i in xrange(0, 3):
		# 	self.assertEqual(TuneMIDI.get[i].getFrequency(), frequencies[i])
		# 	self.assertEqual(tune[i].getOnset(), i)

    #These functions weren't written and are not necessary for execution 
    # because we didn't need the frequency attribute
#	def testnotesListEquals(self):
# 		note1 = Note(frequency = 261.63, onset = 0.0)
# 		note2 = Note( frequency = 293.66, onset = 1.0)
# 		note3 = Note(frequency = 329.63, onset = 2.0)
# 		note4 = Note(frequency = 349.23, onset = 3.0)
		
# 		notes = [note1, note2, note3, note4]
		
# 		samenote1 = Note( frequency = 261.63, onset =  0.0)
# 		samenote2 = Note( frequency = 293.66, onset = 1.0)
# 		samenote3 = Note( frequency = 329.63, onset = 2.0)
# 		samenote4 = Note( frequency = 349.23, onset = 3.0)
		
# 		sameNotes = [samenote1, samenote2, samenote3, samenote4]
		
# 		midifile = "../tests/MIDITestFiles/c-major-scale-treble.mid"
# 		tune = Tune(midi = midifile, timeSignature = (4, 4), clef = Clef.TREBLE, titel = "firstTune", contributor = ["me", "you"])
		
# 		self.assertTrue(tune.notesListEquals(notes,sameNotes))
		
# 		diffNote3 = Note( frequency = 300.0, onset =  2.0)
# 		diff3rdNote = [samenote1, samenote2, diffNote3, samenote4]
# 		self.assertFalse(tune.notesListEquals(notes,diff3rdNote))
		
# 		diffNoteOrder = [samenote1, samenote3, samenote2, samenote4]
# 		self.assertFalse(tune.notesListEquals(notes,diffNoteOrder))
#		note1 = Note( 261.63, 0.0)
#		note2 = Note( 293.66, 1.0)
#		note3 = Note(329.63, 2.0)
#		note4 = Note(349.23, 3.0)
#		
#		notes = [note1, note2, note3, note4]
#		
#		samenote1 = Note( 261.63, 0.0)
#		samenote2 = Note( 293.66, 1.0)
#		samenote3 = Note( 329.63, 2.0)
#		samenote4 = Note( 349.23, 3.0)
#		
#		sameNotes = [samenote1, samenote2, samenote3, samenote4]
#		
#		midifile = midi.read_midifile("miditest.midi")
#		tune = Tune(midifile, (4, 4), treble, "firstTune", ["me", "you"])
#		
#		self.assertTrue(tune.notesListEquals(notes,sameNotes))
#		
#		diffNote3 = Note( 300.0, 2.0)
#		diff3rdNote = [samenote1, samenote2, diffNote3, samenote4]
#		self.assertFalse(tune.notesListEquals(notes,diff3rdNote))
#		
#		diffNoteOrder = [samenote1, samenote3, samenote2, samenote4]
#		self.assertFalse(tune.notesListEquals(notes,diffNoteOrder))
#
#
#	def testNotesListGetterSetter(self):
#		note1 = Note(frequency=261.63,onset= 0.0)
#		note2 = Note(frequency=293.66,onset= 1.0)
#		note3 = Note(frequency=329.63,onset= 2.0)
#		note4 = Note(frequency=349.23,onset= 3.0)
#		
#		notes = [note1, note2, note3, note4]
#		
#		samenote1 = Note(frequency= 261.63,onset= 0.0)
#		samenote2 = Note(frequency= 293.66,onset= 1.0)
#		samenote3 = Note(frequency= 329.63,onset= 2.0)
#		samenote4 = Note(frequency= 349.23,onset= 3.0)
#		
#		sameNotes = [samenote1, samenote2, samenote3, samenote4]
#		
#		tune = Tune()
#		
#		tune.setNotesList(notes)
#		self.assertTrue(tune.notesListEquals(tune.getNotesList(), sameNotes))

	# This test is unnecessary because we do not need to covert frequencies from MIDI files to compute note pitches.
	# This instead will be needed for iteration 2 with audio files.
	# def testComputeNotes(self):
	# 	tune = Tune((4, 4), Clef.TREBLE, "title1", ["a", "b"])
		
	# 	#testing C major scale with all quarter notes
	# 	q_C4 = Note(261.63, 0)
	# 	q_D4 = Note(293.66, 1)
	# 	q_E4 = Note(329.63, 2)
	# 	q_F4 = Note(349.23, 3)
	# 	q_G4 = Note(392.00, 4)
	# 	q_A4 = Note(440.00, 5)
	# 	q_B4 = Note(493.88, 6)
	# 	q_C5 = Note(523.25, 7)
	# 	CMajor1 = [q_C4, q_D4, q_E4, q_F4, q_G4, q_A4, q_B4, q_C5]
	# 	CMajor1_notes = tune.computeNotes(CMajor1)
	# 	self.assertTrue(tune.notesListEquals(CMajor1, CMajor1_notes))
		
	# 	#testing for C major scale of different note lengths
	# 	w_C4 = Note(261.63, 0)
	# 	h_D4 = Note(293.66, 4)
	# 	q_E4 = Note(329.63, 6)
	# 	e_F4 = Note(349.23, 7)
	# 	s_G4 = Note(392.00, 7.5)
	# 	e_A4 = Note(440.00, 7.75)
	# 	q_B4 = Note(493.88, 8.25)
	# 	h_C5 = Note(523.25, 9.25)
	# 	CMajor2 = [w_C4, h_D4, q_E4, e_F4, s_G4, e_A4, q_B4, h_C5]
	# 	CMajor2_notes = tune.computeNotes(CMajor2)
	# 	self.assertTrue(tune.notesListEquals(CMajor2, CMajor2_notes))
	# 	self.assertFalse(tune.notesListEquals(CMajor2, CMajor1))
		
	def testcalculateRests(self):
		# print "RUNNING: testcalculateRests ..."
		tune = Tune()
		PitchC = Pitch (letter='b', octave=4, accidental=Accidental.NATURAL)
					
		q1_C4 = Note(frequency=261.63, onset=0, s_duration=1.0, duration=Duration.QUARTER, pitch=PitchC)
		q_restNote = Note.Rest(frequency=0, onset=0.0, s_duration=1.0, duration=Duration.QUARTER)
		q2_C4 = Note(frequency=261.63, onset=2, s_duration=1.0, duration=Duration.QUARTER, pitch=PitchC)
		
		CRestC = [q1_C4, q_restNote, q2_C4]
		rest = tune.calculateRests([q1_C4, q2_C4])
		self.assertTrue(tune.notesListEquals(rest, CRestC))
		self.assertFalse(tune.notesListEquals(rest, [q1_C4, q2_C4]))

		# print "PASSED"
    #self.assertFalse(tune.notesListEquals(rest, [q1_C4, q2_C4]))

	# We put computeNoteOrder functionality into the calculateRests method so this 
	# test is not relevant 		
#	def testcomputeNoteOrderTest(self):
#		#testing notes with no rests
#		t1note1 = Note(frequency = 261.63, onset = 0.0)
#		t1note2 = Note( frequency = 293.66,onset =  1.0)
#		t1note3 = Note( frequency = 329.63, onset = 2.0)
#		t1note4 = Note( frequency = 349.23,onset =  3.0)
#		t1notes = [t1note2,t1note3,t1note1,t1note4]
#		t1notesOrdered = computeNoteOrder(t1notes, [])
#		t1expectedNotesOrdered = [t1note1,t1note2,t1note3,t1note4]
#		
#		midifile = midi.read_midifile("miditest.midi")
#		tune = Tune(midi = midifile, timeSignature = (4,4), clef = Clef.TREBLE, title = "firstTune", contributor = ["me", "you"])
#		
#		self.assertTrue(tune.notesListEquals(t1notesOrdered, t1expectedNotesOrdered))
#		
#		#testing notes with equal length rests
#		t21note1 = Note(frequency = 261.63,onset =  0.0)
#		t2note2 = Note(frequency = 293.66, onset = 1.0)
#		t2rest1 = Note(frequency = 0,onset =  2.0)
#		t2note3 = Note(frequency = 329.63,onset =  3.0)
#		t2note4 = Note(frequency = 349.23, onset = 4.0)
#		t2rest2 = Note(frequency = 0, onset = 5.0)
#		t2note5 = Note(frequency = 392.00,onset =  6.0)
#		t2notes = [t2note5, t2note2,t2note3,t2note1,t2note4]
#		t2rests = [t2rest2, t2rest1]
#		
#		t2notesOrdered = computeNoteOrder(t2notes, t2rests)
#		t2expectedNotesOrdered = [t2note1,t2note2,t2rest1, t2note3,t2note4, t2rest2, t2note5]
#		
#		self.assertTrue(tune.notesListEquals(t2notesOrdered, t2expectedNotesOrdered))
#		
#		#testing notes with different length rests and notes
#		t3note1 = Note(261.63, 0.0)
#		t3rest1 = Note(0, 1.0)
#		t3note2 = Note(293.66, 3.0)
#		t3rest2 = Note(0, 3.5)
#		t3note3 = Note(329.63, 4.0)
#		t3note4 = Note(349.23, 8.0)
#		t3rest3 = Note(0, 10.0)
#		t3note5 = Note(392.00, 14.0)
#		
#		t3notes = [t3note5, t3note3, t3note2,t3note1,t3note4]
#		t3rests = [t3rest2, t3rest3m, t3rest1]
#		
#		t3notesOrdered = computeNoteOrder(t3notes, t3rests)
#		t3expectedNotesOrdered = [t3note1,t3rest1, t3note2, t3rest2, t3note3, t3note4, t3rest3, t3note5]
#		
#		self.assertTrue(tune.notesListEquals(t3notesOrdered, t3expectedNotesOrdered))

	def testKeyEqual(self):
		# print "RUNNING: testKeyEqual ..."

		pitch = Pitch(letter = 'b',accidental=Accidental.FLAT)
		key = Key(isMajor=True, pitch=Pitch(letter='b', accidental=Accidental.FLAT))
		sameKey = Key(isMajor=True, pitch=Pitch(letter='b', accidental=Accidental.FLAT))
		
		self.assertTrue(key.keyEqual(sameKey))
		
		diffLetter = Key(isMajor=True, pitch=Pitch(letter='e', accidental=Accidental.FLAT))
		diffAccidental = Key(isMajor=True, pitch=Pitch(letter='b', accidental=Accidental.NATURAL))
		diffIsMajor = Key(isMajor=False, pitch=Pitch(letter='b', accidental=Accidental.FLAT))
		
		self.assertFalse(key.keyEqual(diffLetter))
		self.assertFalse(key.keyEqual(diffAccidental))
		self.assertFalse(key.keyEqual(diffIsMajor))

		# print "PASSED"
	
	# we did not implement a tuneEquals method in the Tune class	
	# def testtuneEquals(self):
	# 	midifile = midi.read_midifile("miditest.midi")
	# 	tune = Tune(midifile, (4,4), treble, "firstTune", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	note1 = Note( 261.63, 0.0)
	# 	note2 = Note( 293.66, 1.0)
	# 	note3 = Note( 329.63, 2.0)
	# 	note4 = Note( 349.23, 3.0)
	# 	notes = [t1note2,t1note3,t1note1,t1note4]
	# 	tune.setNotesList(notes)
		
	# 	sameMidifile = midi.read_midifile("miditest.midi")
	# 	sametune = Tune(sameMidifile, (4,4), treble, "firstTune", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	sametune.setNotesList(notes)
	# 	self.assertTrue(tune.tuneEquals(sametune))
		
	# 	diffTimeSig = Tune(sameMidifile, (3,4), treble, "firstTune", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	diffTimeSig.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffTimeSig))
		
	# 	diffClef = Tune(sameMidifile, (4,4), bass, "firstTune", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	diffClef.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffClef))
		
	# 	diffName = Tune(sameMidifile, (4,4), treble, "name", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	diffName.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffName))
		
	# 	diffCollab = Tune(sameMidifile, (4,4), treble, "firstTune", ["us", "you"], Key (true, Pitch('e', None, flat)))
	# 	diffCollab.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffCollab))
		
	# 	diffMidiFile = midi.read_midifile("diffmiditest.test")
	# 	tune = Tune(diffMidiFile, (4,4), treble, "firstTune", ["me", "you"], Key (true, Pitch('e', None, flat)))
	# 	diffMidiFile.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffMidiFile))
		
	# 	diffKey = Tune(sameMidifile, (4,4), treble, "firstTune", ["me", "you"], Key (true, Pitch('b', None, flat)))
	# 	diffKey.setNotesList(notes)
	# 	self.assertFalse(tune.tuneEquals(diffKey))
		
	# 	t2note1 = Note( 261.63, 0.0)
	# 	t2note2 = Note( 293.66, 1.0)
	# 	t2rest1 = Note( 0, 2.0)
	# 	t2note3 = Note( 329.63, 3.0)
	# 	t2note4 = Note( 349.23, 4.0)
	# 	t2rest2 = Note( 0, 5.0)
	# 	t2note5 = Note( 392.00, 6.0)
	# 	t2notes = [t2note5, t2note2,t2note3,t2note1,t2note4]
	# 	diffNotesList = Tune(sameMidifile, (4,4), treble, "firstTune", ["me", "you"])
	# 	diffNotesList.setNotes(t2note1)
	# 	self.assertFalse(tune.tuneEquals(diffNotesList))

	def testNotesListGetterSetter(self):
		# print "RUNNING: testNotesListGetterSetter ..."
		note1 = Note(frequency=261.63,onset= 0.0)
		note2 = Note(frequency=293.66,onset= 1.0)
		note3 = Note(frequency=329.63,onset= 2.0)
		note4 = Note(frequency=349.23,onset= 3.0)
		
		notes = [note1, note2, note3, note4]
		
		samenote1 = Note(frequency= 261.63,onset= 0.0)
		samenote2 = Note(frequency= 293.66,onset= 1.0)
		samenote3 = Note(frequency= 329.63,onset= 2.0)
		samenote4 = Note(frequency= 349.23,onset= 3.0)
		
		sameNotes = [samenote1, samenote2, samenote3, samenote4]
		
		tune = Tune()
		
		tune.setNotesList(notes)
		self.assertTrue(tune.notesListEquals(tune.getNotesList(), sameNotes))

		# print "PASSED"

	def testTuneGetterSetter(self):
		# print "RUNNING: testTuneGetterSetter ..."
		pitch = Pitch(letter='b', accidental=Accidental.FLAT)
		key = Key(isMajor=True, pitch=pitch)
		tune = Tune()
		tune.setKey(key)
		
		expectedKey = Key(isMajor=True, pitch=Pitch(letter='b', accidental=Accidental.FLAT))
		
		self.assertTrue(tune.getKey().keyEqual(expectedKey))

		# print "PASSED"


if __name__ == '__main__':
	unittest.main()
	suite = unittest.TestLoader().loadTestsFromTestCase(TestImpromptuBackend)
	unittest.TextTestRunner(verbosity=3).run(suite)
