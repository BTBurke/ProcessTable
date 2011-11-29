import re
import argparse
import datetime
import dateutil.relativedelta as rel
import csv
import numpy as np

class ProcessTable():
		
	def __init__(self):
		pfile = self.getargs()
		self.events = self.construct_events('event-dates.csv')
		print self.events['6A']
		self.precedence =['1B', '1A', '2B', '2A', '3B', '3A', '4B', '4A', '5B', '5A', '6B', '6A', '7B', '7A', '8B', '8A']
		self.process_csv(pfile)
		self.read_replace_template()


	def getargs(self):
		parser = argparse.ArgumentParser(description = "Reads from a CSV file and updates fill matrix table.")
		parser.add_argument('process_file')
		c = parser.parse_args()
		return c.process_file

	def read_replace_template(self):
		with open('template.html', 'r') as fid:
			for line in fid.readlines():
				re_grp = re.sub('([0-9]*">[0-9][A-B]:[0-9]*)', self.replace_value, line)
				fid2 = open('ar2.html', 'w')
				fid2.write(re_grp)
				fid2.close()
		with open('ar2.html', 'r') as fid:
			for line in fid.readlines():
				re_grp = re.sub("(DATE1)", self.replace_date, line)
				fid2 = open('fill_matrix.html', 'w')
				fid2.write(re_grp)
				fid2.close()

			#for grp in re_grp:
				#print grp

	def replace_value(self, m):
		#CSS Color definitions
		WHITE = str(7)
		GREEN = str(8)
		YELLOW = str(9)
		GRAY = str(10)

		event, day = m.group(0).split(':')
		event = event.split('>')[1]
		a_or_b = event[-1]
		day_ind = int(day) - 1
		work_arr = self.events[event]['personnel']
		

		if day_ind >= len(work_arr):
			COLOR = GRAY
			return COLOR + '">' 
		else:
			num = work_arr[day_ind]
			if (num >= 9 and a_or_b == 'A') or (num >= 6 and a_or_b == 'B'):
				COLOR = GREEN
			else:
				COLOR = WHITE
			return COLOR + '">' + str(num)

	def replace_date(self, m):
		d = datetime.date.today()
		return str(d.month) + '/' + str(d.day) + '/' + str(d.year)

	def split_date(self, date_str):
		mo, day, yr = date_str.split('/')
		return datetime.date(int(yr),int(mo),int(day))

	def construct_events(self, event_csv):
		events = csv.DictReader(open(event_csv,'r'))
		event_dict = {}
		for row in events:
			start_date = self.split_date(row['Start Date'])
			end_date = self.split_date(row['End Date'])
			event_days = rel.relativedelta(end_date, start_date).days + 1
			event_dict[row['Event']] = {'personnel': np.zeros(event_days, dtype=np.int), 'start': start_date, 'end': end_date}
		return event_dict

	def process_csv(self, fname):
		with open(fname, 'r') as fid:
			rows = csv.DictReader(fid)
			for row in rows:
				self.name = row['Last Name'] + ', ' + row['First Name']
				self.start = self.split_date(row['Desired AT Start Date (MM-DD-YY)'])
				self.end = self.split_date(row['Desired AT End Date (MM-DD-YY)'])
				self.support = row['Event Supported']
				self.populate_days()
	
	def _is_in_event(self, day, event):
		#print "Start: %s, End: %s" % (self.events[event]['start'], self.events[event]['end'])
		print "%s: %i, %i" % (event,self._diff_days(day, self.events[event]['start']),self._diff_days(day, self.events[event]['end']))

		if self._diff_days(day, self.events[event]['start']) >= 0 and self._diff_days(day, self.events[event]['end'])<=0:
			return True
		else:
			return False

	def _diff_days(self, date1, date2):
		diff_days = date1 - date2
		return diff_days.days

	def _day_array(self, start_date, end_date):
		"""
		Returns array of date objects between date1 and date2
		"""
		day_array = []
		for x in range(self._diff_days(end_date, start_date)+1):
			day_array.append(start_date + rel.relativedelta(days=+x))
		return day_array

	def populate_days(self):
		this_precedence = self.precedence
		this_precedence.insert(0, self.support)

		print this_precedence
		for day in self._day_array(self.start, self.end):
			possible_events = []
			for event in self.events.keys():
				if self._is_in_event(day, event):
					possible_events.append(event)
			print possible_events

			if len(possible_events) == 0:
				raise
			elif len(possible_events) == 1:
				self._increment_personnel(possible_events[0], day)
			else:
				for ev_p in this_precedence:
					if ev_p in possible_events:
						self._increment_personnel(ev_p, day)
						break
			
	
	def _increment_personnel(self, event, day):
		ind = self._diff_days(day, self.events[event]['start'])
		self.events[event]['personnel'][ind] = self.events[event]['personnel'][ind] + 1

if __name__ == '__main__':
	ProcessTable()