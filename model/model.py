from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO
from model.tour import Tour
from model.attrazione import Attrazione

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()
        print(self.tour_map)

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        # Prendo le relazioni tour e attrazione
        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
            id_tour = relazione["id_tour"]
            id_attrazione = relazione["id_attrazione"]
            tour_istanza = self.tour_map.get(id_tour)
            attrazione_istanza = self.attrazioni_map.get(id_attrazione)
            # Riempo gli insiemi nelle rispettive classi, attrizione e tour
            tour_istanza.attrazioni.add(attrazione_istanza)
            attrazione_istanza.tour.add(tour_istanza)

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        global tour
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        attrazioni_usate = set()
        for tour in self.tour_map.values():
            if tour.id_regione == id_regione:
                if tour.durata_giorni <= max_giorni:
                    if tour.costo <= max_budget:
                            self._costo += tour.costo
                            for attr in tour.attrazioni:
                                self._pacchetto_ottimo.append(attr)
                                attrazioni_usate.add(attr)

        self._valore_ottimo = self._ricorsione(1,[], max_giorni, max_budget, 0, attrazioni_usate)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if start_index >= len(pacchetto_parziale):
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente
            self._valore_ottimo = valore_corrente
            return pacchetto_parziale
        tour_list = list(self.tour_map.values())
        tour = tour_list[start_index]
        if tour.durata_giorni <= durata_corrente and tour.budget <= costo_corrente:
            if not tour.attrazioni.intersection(attrazioni_usate):
                pacchetto_parziale.append(tour)
                attrazioni_usate.update(tour.attrazioni)
                self._ricorsione(start_index + 1,
                                 pacchetto_parziale,
                                 durata_corrente + tour.durata_giorni,
                                 costo_corrente + tour.costo,
                                 valore_corrente + sum(a.valore_cultura for a in tour.attrazioni),
                                 attrazioni_usate)
                pacchetto_parziale.pop()
                attrazioni_usate.difference(tour.attrazioni)
            else:
                return None
        else:
            return None