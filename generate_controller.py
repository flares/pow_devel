#!C:\Python26\python.exe -u

#  pow model generator.
#
# options are: 
#   see: python generate_controller.py --help

import os
from optparse import OptionParser
import sqlite3
import sys, string
import datetime
from sqlalchemy.orm import mapper
from sqlalchemy import *


sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./lib" )))
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./models" )))
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./models/powmodels" )))
import powlib
import PowObject

# setting the right defaults
MODE_CREATE = 1
MODE_REMOVE = 0
PARTS_DIR = powlib.PARTS_DIR
CONTROLLER_TEST_DIR = "/tests/controllers/"


def main():
    parser = OptionParser()
    mode= MODE_CREATE
    #parser.add_option("-n", "--name",  action="store", type="string", dest="name", help="creates migration with name = <name>", default ="None")
    parser.add_option("-m", "--model",  action="store", type="string", dest="model", help="defines the model for this migration.", default ="None")
    parser.add_option("-f", "--force",  action="store_false",  dest="noforce", help="forces overrides of existing files",default="True")
    
    controller_name = "None"
    controller_model = "None"
    start = None
    end = None
    start = datetime.datetime.now()
    
    (options, args) = parser.parse_args()
    #print options        
    if options.model == "None":
        if len(args) > 0:
            # if no option flag (like -m) is given, it is assumed that the first argument is the model. (representing -m arg1)
            options.model = args[0]
        else:
            parser.error("You must at least specify an appname by giving -n <name>.")
            
    controller_name = options.model
    render_controller(controller_name, options.noforce)

    end = datetime.datetime.now()
    duration = None
    duration = end - start 
    print "generated_controller in("+ str(duration) +")"
    return
    
def render_controller(name, noforce):
    # 
    print " creating controller: " 
    print " -- ", name 
    
    # add the auto generated warning to the outputfile
    infile = open (os.path.normpath(PARTS_DIR + "autogenerated_warning.txt"), "r")
    ostr = infile.read()
    infile.close()
    
    # add a creation date
    ostr = ostr + os.linesep
    ostr = ostr + "# date created: \t" + str(datetime.date.today())
    ostr = ostr + os.linesep
    
    # Add the model_stub part1 content to the newly generated file. 
    infile = open (os.path.normpath( PARTS_DIR + "controller_stub_part0.py"), "r")
    ostr = ostr + infile.read()
    infile.close()
    
    #pluralname = powlib.plural(model)
    #ostr += powlib.tab +  powlib.tab + "table_name=\"" + pluralname + "\""
    ostr += powlib.linesep
    ostr += "import " + string.capitalize( name ) 
    ostr += powlib.linesep
    ostr += powlib.linesep
    
    classname = string.capitalize( name ) + "Controller"
    ostr += "class " + classname + "(BaseController.BaseController):"
    
    # Add the controller_stub part 1 content to the newly generated file. 
    infile = open (os.path.normpath(PARTS_DIR + "controller_stub_part1.py"), "r")
    ostr = ostr + infile.read()
    ostr+= powlib.tab + powlib.tab + "self.modelname = \"" + string.capitalize( name ) + "\"" + powlib.linesep
    
    # Add the controller_stub part2 content to the newly generated file. 
    infile = open (os.path.normpath(PARTS_DIR + "controller_stub_part2.py"), "r")
    ostr = ostr + infile.read()
    infile.close()
    
    filename = os.path.normpath ( "./controllers/" + classname +".py" )
    
    if os.path.isfile( os.path.normpath(filename) ) and noforce:
        print " --", filename + " already exists... (Not overwrtitten. Use -f to force ovewride)"
    else:
        ofile = open(  filename , "w+") 
        print  " -- created controller " + filename
        ofile.write( ostr )
        ofile.close()
    #
    # check if BaseModel exist and repair if necessary
    if os.path.isfile(os.path.normpath( "./controllers/BaseController.py")):
        #BaseModel exists, ok.
        pass
    else:
        # copy the BaseClass
        powlib.check_copy_file(os.path.normpath( "./stubs/controllers/BaseController.py"), os.path.normpath( "./controllers/"))
    
    render_test_stub( name, classname )
    return
    
    
def render_test_stub (controllername, classname, prefix_path ="" ):
    #print "rendering Testcase for:", classname, " ", " ", modelname
    print " -- generating TestCase...",
    infile = open( os.path.normpath( PARTS_DIR +  "test_controller_stub.py"), "r")
    test_name = "Test" + classname + ".py"
    ofile = open( os.path.normpath(prefix_path + CONTROLLER_TEST_DIR + test_name ), "w")
    instr = infile.read()
    instr = instr.replace("#CLASSNAME", "Test" + classname  )
    ofile.write(instr)
    infile.close()
    ofile.close()
    print  " %s...(created)" % (prefix_path + CONTROLLER_TEST_DIR + test_name)
    return


if __name__ == '__main__':
    main()
