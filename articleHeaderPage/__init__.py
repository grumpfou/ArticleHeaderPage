# -*- coding: utf8 -*-
from PyQt5 import QtGui, QtCore,QtWidgets
import fpdf
# from PyPDF2 import PdfFileWriter, PdfFileReader
import argparse
import bibtexparser
import os
import re
import subprocess
import sys
import traceback

fpdf.SYSTEM_TTFONTS = "/usr/share/fonts/truetype/dejavu/"

color_dict={
	'blue':(0,0,255),
	'green':(0,200,0),
	'red':(255,0,0),
	'black':(0,0,0),
	}


class HeaderPage:
	def __init__(self,filepath,title=None,short=None,author=None,replace=False,
				color = 'blue',notes=None):
		# self.filepath 	= filepath
		self.title 		= title # latin_1(title )
		self.short 		= short # latin_1(short )
		self.author 	= author# latin_1(author)
		self.notes		= notes # latin_1(notes )
		self.color 		= color_dict[color]

		f,e = os.path.splitext(filepath)
		to_remove = []
		filepath_replace = filepath
		if replace:
			for i in range(replace):

				filepath_replace_new = f+'_replace'+str(i)+e
				self.remove_first_page_pdf(filepath_replace_new,filepath_replace)
				to_remove.append(filepath_replace)
				filepath_replace = filepath_replace_new
				# QtGui.QMessageBox.information(self,'HeaderPage','One page suppressed')


		filepath_tmp = f+'_tmp'+e
		self.create_pdf(filepath_tmp)
		to_remove.append(filepath_tmp)

		filepath_combined= f+'_combined'+e
		self.join_pdf(filepath_combined,filepath_tmp,filepath_replace)

		for f in to_remove:
			os.remove(f)

		os.rename(filepath_combined,filepath)


	def create_pdf(self,filepath_tmp):
		"""Creates a pdf containg only the headerPage"""
		pdf=fpdf.FPDF('P','pt','A4')
		pdf.add_page()

		dd = {
			"":"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
			"B":"/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
			"I":"/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
		}
		for k,v in dd.items():
			pdf.add_font('DejaVu', k, v, uni=True)
		# pdf.set_font('Times','',25)
		pdf.set_font('DejaVu','',25)
		pdf.set_text_color(*self.color) # self.color =(red,green,blue)

		if self.short!=None:
			pdf.set_font('','B')
			pdf.write(50, self.short+'\n')


		if self.title!=None:
			pdf.set_font('','')
			pdf.write(30, self.title+'\n')

		if self.author!=None:
			pdf.set_font('DejaVu','',15)
			pdf.set_font('','I')
			pdf.write(30, self.author+'\n')

		if self.notes!=None:

			pdf.set_font('DejaVu','',15)
			pdf.set_text_color(*color_dict['black'])
			pdf.write(20, '\n'+self.notes.strip()+'\n')

		pdf.output(filepath_tmp,'F')

	def join_pdf(self,name,filepath_1,filepath_2):
		"""Join 2 pdf files"""
		subprocess.call(['pdftk',filepath_1,filepath_2,'cat','output',name])

	def remove_first_page_pdf(self,filepath_replace,filepath_to_replace):
		subprocess.call(['pdftk',filepath_to_replace,'cat','2-end','output',filepath_replace])


class Dialog (QtWidgets.QDialog):
	def __init__(self,*args,**kargs):
		QtWidgets.QDialog.__init__(self,*args,**kargs)
		self.bibtex_prase_button = QtWidgets.QPushButton("Prase")
		self.short_edit = QtWidgets.QLineEdit()
		self.authors_edit = QtWidgets.QLineEdit()
		self.title_edit = QtWidgets.QLineEdit()
		self.file_edit = QtWidgets.QLineEdit()
		self.notes_edit = QtWidgets.QTextEdit()

		self.replace = QtWidgets.QSpinBox()
		self.color = QtWidgets.QComboBox()
		k = list(color_dict.keys())
		k.sort()
		self.color.addItems(k)
		i = k.index('blue')
		self.color.setCurrentIndex ( i )
		self.button = QtWidgets.QPushButton("Generate")

		main_layout=QtWidgets.QFormLayout()
		main_layout.addRow("Bibtex Ref",self.bibtex_prase_button)
		main_layout.addRow("Short",self.short_edit)
		main_layout.addRow("Authors",self.authors_edit)
		main_layout.addRow("Title",self.title_edit)
		main_layout.addRow("File",self.file_edit)
		main_layout.addRow("Notes",self.notes_edit)

		main_layout.addRow("Replace first page" ,self.replace)
		main_layout.addRow("Color" ,self.color)
		main_layout.addRow("Prase" ,self.button)
		self.bibtex_prase_button.clicked.connect(self.prase)
		self.button.clicked.connect(self.generate)
		# self.connect(self.bibtex_prase_button, QtCore.SIGNAL("clicked()"), self.prase)
		# self.connect(self.button, QtCore.SIGNAL("clicked()"), self.generate)

		self. setLayout ( main_layout )

	def prase(self):

		textedit = QtWidgets.QTextEdit(parent=self)
		def prase_wid():
			a = bibtexparser.loads(unicode(textedit.toPlainText()))
			if len(a.entries)==0:
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing","Wrong Bibtex reference.")
				return False
			d = a.entries[0]
			if not d.has_key('file'):
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing","Bibtex do not contain the file.")
				return False
			if not (d.has_key('year') or d.has_key('date') ):
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing","Bibtex do not contain the year or the date.")
				return False
			if not d.has_key('author'):
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing","Bibtex do not contain the author.")
				return False
			if not d.has_key('title'):
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing","Bibtex do not contain the title.")
				return False

			if d.has_key('year'): y = d['year']
			else:
				tmp = re.findall('[0-9][0-9][0-9][0-9]',d['date'])
				if len(tmp)==0:
					QtWidgets.QMessageBox.critical(self,"Wrong Prasing",
						"Bibtex do not understand the year format of "
						"the date")
				else: y  = tmp[0]
			authors = d["author"].split(" and ")
			authors = [a.split(',') for a in authors]
			authors = [[aa.strip() for aa in a] for a in authors]
			short = authors[0][0]+y

			authors_str = []
			for a in authors:
				new_a = a[0]
				if len(a)>=2:
					for aa in a[1:]:
						new_a += ' '+ ' '.join([firstname[0].upper()+'.' for firstname in aa.split(" ")])
				authors_str.append(new_a)

			if len(authors_str)>=5:
				authors_str = authors_str[:4]+['...']+[authors_str[-1]]
			authors_str = ", ".join(authors_str)
			print("authors_str",authors_str)
			title = d['title']
			title = title.replace('{','')
			title = title.replace('}','')

			files = d['file'].split(';')
			motif = ':application/pdf'
			for i,f in enumerate(files):
				if f.endswith(motif):
					files[i] = f[:-len(motif)]

			files = filter(lambda f: f.endswith('.pdf') or f.endswith('.PDF'), files)

			print("files",files)
			if len(files)==0:
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing",
										"No pdf file detected in bibtex file.")
				return False
			elif len(files)==1:
				file = files[0]

			else:
				item = QtWidgets.QInputDialog.getItem(textedit,
					'Choose pdf file','File: ', files, 0, False)
				if not item[1]:
					return False
				file = unicode(item[0])

			m = file.find(':')
			if m <-1 :
				QtWidgets.QMessageBox.critical(self,"Wrong Prasing",
										"No pdf file detected in bibtex file.")
				return False
			file = file[m+1:]

			notes = ""
			if d.has_key('annote'):
				notes = d['annote']

			wid.close()
			self.short_edit.setText(short)
			self.authors_edit.setText(authors_str)
			self.title_edit .setText(title)
			self.file_edit .setText(file)
			self.notes_edit .setText(notes)
		wid =  QtWidgets.QDialog(self,QtCore.Qt.Tool)
		but = QtWidgets.QPushButton("Prase")
		lay = QtWidgets.QVBoxLayout()
		lay.addWidget(textedit)
		lay.addWidget(but)
		wid.setLayout(lay)
		but.clicked.connect(prase_wid)
		# self.connect(but, QtCore.SIGNAL("clicked()"), prase_wid)
		# TODO:
		# self.connect(QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Return"), self), QtCore.SIGNAL('activated()'), prase_wid)
		wid.show()


	def generate(self):
		short = unicode(self.short_edit.text())
		authors = unicode(self.authors_edit.text())
		title = unicode(self.title_edit.text())
		file  = unicode(self.file_edit.text())
		notes = unicode(self.notes_edit.toPlainText())

		if int(self.replace.value()) >0 :
			replace = int(self.replace.value ())
		else:
			replace = False

		color = unicode(self.color.currentText())
		cs = "<center><strong>"
		sc = "</center></strong><br/>"
		m = "We are going to put the header page to the file:<br/>"+\
			cs+file+","+sc+\
			"with the title:<br/>"+\
			cs+title+","+sc+\
			"with the short description:<br/>"+\
			cs+short+","+sc+\
			"in color:<br/>"+\
			cs+color+sc
		if replace:
			m += "<strong>by replacing its "+str(replace)+"st page(s).</strong>"
		else:
			m += "<strong>by inserting a first page.</strong>"
		r = QtWidgets.QMessageBox.question(self,"Confimation",m,
									QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		if r == QtWidgets.QMessageBox.Yes:
			# title =None
			author = authors
			try:
				HeaderPage(filepath = file,
					title = title,
					short = short,
					author = author,
					replace=replace,
					color=color,
					notes=notes,
					)
			except StandardError as e:
				mess = "Traceback (most recent call last):\n"
				for frame in traceback.extract_tb(sys.exc_info()[2]):
					fname,lineno,fn,text = frame
					mess += 'File "'+fname+'", line '+str(lineno)+', in '+fn+\
						'\n\t'+text+'\n'
				mess+= e.__class__.__name__ +':'+str(e)
				QtWidgets.QMessageBox.critical(self,'HeaderPage','Error when creating '+\
					'the file: \n'+str(mess))
				raise e
			else:
				QtWidgets.QMessageBox.information(self,'HeaderPage','Header page '+\
					'creation successeded')
				subprocess.call(["xdg-open", file])


		self.replace.setValue (0)


def  main():
	parser = argparse.ArgumentParser()

	parser.add_argument("file",
		help="File to execute",
		nargs='?')

	parser.add_argument("--title",
		# help="Import a file, for its the options, read the documentation",
		# type='unicode',
		nargs='+')

	parser.add_argument("--short",
		# help="Export a file",
		nargs='+')

	parser.add_argument("--author",
		# help="Recheck the typography when opening the file.",
		nargs='+')

	parser.add_argument("--replace",
		# help="Recheck the typography when opening the file.",
		action='store_true')

	parser.add_argument("--gui",
		# help="Recheck the typography when opening the file.",
		action='store_true')


	args = parser.parse_args()

	def adapt (a) :
		if a==None: return a
		return ' '.join(a).decode('utf8')
	filepath  = args.file
	title  	  = adapt(args.title)
	short  	  = adapt(args.short)
	author    = adapt(args.author)
	replace   = args.replace
	gui   = args.gui

	if not gui:
		if len(sys.argv)==1:
			raise IOError('Please specify the file where to add the file')
		HeaderPage(filepath = filepath,
				title = title,
				short = short,
				author = author,
				replace=replace,
				)
	else:
		app = QtWidgets.QApplication(sys.argv)
		dir,tmp = os.path.split(__file__)
		iconpath = os.path.join(dir,'neuron.png')
		# iconpath = '/home/dessalles/Programmation/Python/Project_AthenaWriter/AthenaWriterWorkingVersion/Images/LogoTmp.png'
		app.setWindowIcon(QtGui.QIcon(iconpath))
		d = Dialog()
		d.show()
		sys.exit(app.exec_())


if __name__=='__main__':
	main()
