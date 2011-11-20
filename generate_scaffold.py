#!C:\Python26\python.exe -u

#  pow model generator.
#
# options are: 
#	no option or -create 		means create
#	-remove 			removes 

import email
import string
import os
from optparse import OptionParser
import sqlite3
import sys
import datetime
from sqlalchemy.orm import mapper
from sqlalchemy import *


sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./lib" )))
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./models/powmodels" )))
import powlib


# setting the right defaults
MODE_CREATE = 1
MODE_REMOVE = 0

def main():
	parser = OptionParser()
	mode= MODE_CREATE
	#parser.add_option("-n", "--name",  action="store", type="string", dest="name", help="creates migration with name = <name>", default ="None")
	parser.add_option("-m", "--model",  action="store", type="string", dest="model", help="defines the model for this migration.", default ="None")
	parser.add_option("-f", "--force",  action="store_false",  dest="noforce", help="forces overrides of existing files",default="True")

	(options, args) = parser.parse_args()
	print options
	if options.model == "None":
		parser.error("You must at least specify a model by giving -m <modelname>.")
		return
	else:
		scaffold(options.model, options.noforce)
			
	
def scaffold(modelname, noforce):
	# 
	print "generating scaffold for model: " + str(modelname)
	actions = ["list", "show","new","create", "edit", "update","delete"]
	
	for act in actions:
		# add the auto generated warning to the outputfile
		infile = open (os.path.normpath("./stubs/autogenerated_warning_tmpl.txt"), "r")
		ostr = infile.read()
		infile.close()
		
		# add a creation date
		ostr += "## date created: \t" + str(datetime.date.today())
		
		# Add the _stub part0 content to the newly generated file. 
		infile = open (os.path.normpath("./stubs/scaffold_stub_part0.tmpl"), "r")
		ostr = ostr + infile.read()
		infile.close()
		
		#pluralname = powlib.plural(model)
		#template = powlib.readconfig("pow.cfg", "global", "SCAFFOLD_TEMPLATE")
		#ostr += u"<%inherit file=\"/" + template + "\"/>"
		
		ostr += powlib.linesep
		
		# Add the _stub part1 content to the newly generated file. 
		infile = open (os.path.normpath("./stubs/scaffold_" + act +"_stub_part1.tmpl"), "r")
		ostr = ostr + infile.read()
		infile.close()
		filename = string.capitalize(modelname)  + "_" + act +".tmpl"
		filename = os.path.normpath( "./views/" + filename)
		
		if os.path.isfile( os.path.normpath(filename) ) and noforce:
			print filename + " already exists..."
		else:
			ofile = open(  filename , "w+") 
			print  "created scaffold " + filename
			ofile.write( ostr )
			ofile.close()
	
	
	
def render_method( self, name, vars=[] ):
	#
	# call with
	#     name: method name
	#     vars = [ ("var1","None"), ("var2","1"), ... ]
	#
	ostr = ""
	ostr = ostr + self.pow_tab + "#" + self.pow_newline
	ostr = ostr + self.pow_tab + "# Method: " + name  + self.pow_newline
	ostr = ostr + self.pow_tab + "#" + self.pow_newline
	if len(vars) == 0:
		ostr = ostr + self.pow_tab + "def " + name + "(self):" + self.pow_newline
	else:
		ostr = ostr + self.pow_tab + "def " + name + "(self"
		for var,val  in vars:
			if val == None:
				str = ostr + "," + var
			else:
				str = ostr + "," + var + "=" + val
		ostr = ostr + "):" + self.pow_newline
		ostr = ostr + self.pow_tab + self.pow_tab + "pass" + os.linesep
	return ostr



if __name__ == '__main__':
	main()
