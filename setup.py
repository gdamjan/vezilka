from setuptools import setup
setup(...
    entry_points="""
    [paste.paster_command]
    mycommand = mypackage.mycommand:MyCommand

    [paste.global_paster_command]
    myglobal = mypackage.myglobal:MyGlobalCommand
    """)
