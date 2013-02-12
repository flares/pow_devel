#!python
#  pow app generator
#  Generates the PoW Application.
#  options are:
#   see: python generate_app.py --help


from optparse import OptionParser
import sqlite3, sys, os, datetime
import string
import shutil

sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./stubs/lib" )))  # lint:ok
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "./stubs/models/powmodels" )))  # lint:ok
#for p in sys.path:
#    print p


import powlib
import generate_model


def main():
    """ Executes the render methods to generate a conroller and basic
        tests according to the given options """
    parser = OptionParser()
    #mode = MODE_CREATE
    parser.add_option("-n", "--name",
                      action="store",
                      type="string",
                      dest="name",
                      help="set the app name",
                      default="None")
    parser.add_option("-d", "--directory",
                      action="store",
                      type="string",
                      dest="directory",
                      help="app base dir",
                      default="./")
    parser.add_option("-f", "--force",
                      action="store_true",
                      dest="force",
                      help="forces overrides of existing app",
                      default="False")
    parser.add_option("-sql", "--sqlalchemy",
                      action="store_true",
                      dest="sql",
                      help="create an sqlalchemy ORM based app",
                      default="False")

    (options, args) = parser.parse_args()
    #print options, args
    if options.name == "None":
        if len(args) > 0:
            # if no option flag (like -n) is given, it is assumed that
            # the first argument is the appname. (representing -n arg1)
            options.name = args[0]
        else:
            parser.error(
                "You must at least specify an appname by giving -n <name>."
                )

    appdir = options.directory
    appname = options.name
    force = options.force
    start = None
    end = None
    start = datetime.datetime.now()

    gen_app(appname, appdir, force, options.sql)

    end = datetime.datetime.now()
    duration = None
    duration = end - start
    print " -- generated_app in(" + str(duration) + ")"


def render_db_config(appname, appbase, sql_db=false):
    """ Creates the db.cfg file for this application
        and puts it in appname/config/db.cfg"""

    infile = open("./stubs/config/db.py")
    instr = infile.read()
    infile.close()
    instr = instr.replace("#DEVEL_DB", appname + "_devel") 
    instr = instr.replace("#TEST_DB", appname + "_test")
    instr = instr.replace("#PROD_DB", appname + "_prod")

    if sql_db:
        instr = instr.replace("#DBTYPE", "sqlite")
        instr = instr.replace("#PORT", "")
    else:
        instr = instr.replace("#DBTYPE", "mongodb")
        instr = instr.replace("#PORT", "27017")

    ofile = open(os.path.normpath(appbase + "/config/db.py"), "w")
    ofile.write(instr)
    ofile.close()


def gen_app(appname, appdir, force=False, sql=False):
    """ Generates the complete App Filesystem Structure for Non-GAE Apps.
        Filesystem action like file and dir creation, copy fiels etc.
        NO DB action in this function """

    appname = str(appname)
    appname = str.strip(appname)
    appname = str.lower(appname)
    print " -- generating app:", appname

    powlib.check_create_dir(appdir + appname)
    appbase = os.path.abspath(os.path.normpath(appdir + "/" + appname + "/"))
    #print appbase
    # defines the subdirts to be created. Form { dir : subdirs }
    subdirs = [
                {"config": []},
                {"db": []},
                {"lib": []},
                {"migrations": []},
                {"models": ["basemodels"]},
                {"controllers": []},
                {"public": ["img",
                            "img/bs",
                            "ico",
                            "css",
                            "css/bs",
                            "js",
                            "js/bs",
                            "doc"]},
                {"stubs": ["partials"]},
                {"views": ["layouts"]},
                {"tests": ["models",
                           "controllers",
                           "integration",
                           "fixtures"]},
                {"ext": ["auth", "validate"]}
              ]
    for elem in subdirs:
        for key in elem:
            subdir = os.path.join(appbase, str(key))
            powlib.check_create_dir(subdir)
            for subs in elem[key]:
                powlib.check_create_dir(os.path.join(subdir, str(subs)))

    #
    # copy the files in subdirs. Form ( from, to: appdir + x)
    #
    deep_copy_list = [ ("stubs/config", "config"),
                       ("stubs/lib", "lib"),
                       ("stubs", "stubs"),
                       ("stubs/migrations", "migrations"),
                       ("stubs/partials", "stubs/partials"),
                       ("stubs/public/doc", "/public/doc"),
                       ("stubs/public/ico", "/public/ico"),
                       ("stubs/public/img", "/public/img"),
                       ("stubs/public/img/bs", "/public/img/bs"),
                       ("stubs/public/css", "/public/css"),
                       ("stubs/public/css/bs", "/public/css/bs"),
                       ("stubs/public/js", "public/js"),
                       ("stubs/public/js/bs", "public/js/bs"),
                       ("stubs/lib", "lib"),
                       ("stubs/controllers", "controllers"),
                       ("stubs/views", "views"),
                       ("stubs/views/layouts", "views/layouts"),
                       ("stubs/ext/auth", "ext/auth"),
                       ("stubs/ext/validate", "ext/validate"),
                       ]

    print " -- copying files ..."
    exclude_patterns = [".pyc", ".pyo", ".DS_STORE"]
    exclude_files = ["db.cfg"]
    for source_dir, dest_dir in deep_copy_list:
        for source_file in os.listdir(source_dir):
            fname, fext = os.path.splitext(source_file)
            if not fext in exclude_patterns and not source_file in exclude_files:  # lint:ok
                powlib.check_copy_file(
                    os.path.join(source_dir, source_file),
                    os.path.join(appbase + "/" + dest_dir,source_file)
                )
            else:
                print " excluded:.EXCL", source_file
                continue

    #
    # copy the generator files
    #
    if sql:
      SCRIPTDIR = "scripts/sql/"
    else:
      SCRIPTDIR = "scripts/mongodb/"

    powlib.check_copy_file("SCRIPTDIR" + "generate_model.py", appbase)
    powlib.check_copy_file("SCRIPTDIR" + "do_migrate.py", appbase)
    powlib.check_copy_file("SCRIPTDIR" + "generate_controller.py", appbase)
    powlib.check_copy_file("SCRIPTDIR" + "generate_migration.py", appbase)
    powlib.check_copy_file("SCRIPTDIR" + "generate_scaffold.py", appbase)
    powlib.check_copy_file("SCRIPTDIR" + "generate_mvc.py", appbase)

    powlib.check_copy_file("scripts/pow_console.py", appbase)
    powlib.check_copy_file("scripts/runtests.py", appbase)
    powlib.check_copy_file("scripts/pow_router.wsgi", appbase)
    powlib.check_copy_file("scripts/simple_server.py", appbase)

    powlib.replace_string_in_file(
        os.path.join(appbase + "/" + "simple_server.py"),
        "#POWAPPNAME",
        appname
    )

    powlib.replace_string_in_file(
        os.path.join(appbase + "/" + "pow_router.wsgi"),
        "#POWAPPNAME",
        appname
    )

    #
    # copy the initial db's. Only for SQL-DBs
    #
    if sql:
        appdb = "stubs/db/app_db_including_app_versions_small.db"
        app_db_path = appbase + "/db/" + appname
        powlib.check_copy_file(appdb, os.path.normpath(app_db_path + "_prod.db"))
        powlib.check_copy_file(appdb, os.path.normpath(app_db_path + "_test.db"))
        powlib.check_copy_file(appdb, os.path.normpath(app_db_path + "_devel.db"))
        #powlib.check_copy_file("stubs/db/empty_app.db", os.path.normpath(appbase + "/db/app.db") )  # lint:ok

    #
    # initiate the db.cfg file
    #
    render_db_config(appname, appbase)

    # initialize the base PoW DB management environment.
    if sql:
        #initiate SQLAlchemy / relational based DB environment
        generate_model.render_model(
            "App",
            False,
            "System class containing the App Base Informations",
            appname)
        generate_model.render_model(
            "Version",
            False,
            "System class containing the Versions",
            appname)
    else:
        #initial mongoDB config and environment
        infile = os.path.abspath("./stubs/partials/init_pow_mongodb.py")
        powlib.replace_string_in_file( infile, "#APPNAME", appname):
        
    return


if __name__ == "__main__":
    main()
