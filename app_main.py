"""app_main.py - golf app entry point."""
import console
import ui
import dialogs
from views.AppMain import MainView
from golf_db.db_sqlalchemy import Database

DB_URL = 'sqlite:///golf.sqlite'
db = Database(DB_URL)

class GolfApp(object):
  def __init__(self):
    self.view = ui.load_view('views/main')
    self.view.db = db
    self.view.setup()
    self.view.present('full_screen')

GolfApp()

