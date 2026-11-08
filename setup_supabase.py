"""Initialisation volontaire des tables Fit Evolution dans le schéma isolé."""
import os
import sys

def main():
    if os.environ.get('FIT_INIT_CONFIRM') != 'fit_evolution':
        print('Sécurité : définir FIT_INIT_CONFIRM=fit_evolution pour initialiser.')
        return 2
    from cloud_db import connect
    with connect() as c:
        schema = c.execute('SELECT current_schema() AS name').fetchone()['name']
        if schema != 'fit_evolution':
            raise RuntimeError('Schéma inattendu : arrêt sans création de tables.')
    import moteur, coach, journal, musique, planning_plus, seance_libre, gotham_radio, dashboard
    for module in (moteur, coach, journal, musique, planning_plus, seance_libre, gotham_radio, dashboard):
        if hasattr(module, 'init'):
            print('Initialisation :', module.__name__)
            module.init()
    with connect() as c:
        rows = c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='fit_evolution' ORDER BY table_name").fetchall()
    print('Tables fit_evolution :', ', '.join(r['table_name'] for r in rows))
    return 0

if __name__ == '__main__':
    sys.exit(main())
