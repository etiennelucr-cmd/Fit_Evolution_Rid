"""Run once with configured Streamlit secrets, before launching the app."""
import moteur as m
import coach, journal, musique, planning_plus, seance_libre, gotham_radio, dashboard
m.init()
for module in (coach,journal,musique,planning_plus,seance_libre,gotham_radio,dashboard):
    if hasattr(module,'init'): module.init()
print('Tables initialisées.')
