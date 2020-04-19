# Google Hashcode 2020 - LEBLED PRADIER LAURENT RABOUAN
# StackOverflowCoders
# 02.20.20
from operator import attrgetter
from tqdm import tqdm
import os


class Book:
    def __init__(self, isScanned, score, id):
        self.score = score
        self.isScanned = isScanned
        self.id = id


class Problem:
    def __init__(
        self,
        nbBooks,
        nbLibraries,
        nbDays,
        listeInfos=[],
        books=[],
        libraries=[],
        assigned_libraries=set(),
        assigned_books=set(),
        currentDay=0,
    ):
        self.nbDays = nbDays
        self.nbBooks = nbBooks
        self.currentDay = currentDay
        self.nbLibraries = nbLibraries
        self.listeInfos = listeInfos
        self.books = books
        self.libraries = libraries
        self.assigned_libraries = assigned_libraries
        self.assigned_books = assigned_books

    def fill(self):
        """ Remplis les bibliothèques de livres selon l'input """
        self.libraries = list()  # Reset de la liste des libraries, par sécurité
        for line in range(1, len(self.listeInfos) // 2):
            nbBooks, signUpTime, booksPerDay = list(map(int, self.listeInfos[line * 2]))
            bookids = list(map(int, self.listeInfos[line * 2 + 1]))
            books = [
                Book(
                    isScanned=False,
                    score=int(self.listeInfos[1][bookId - 1]),
                    id=bookId,
                )
                for bookId in list(map(int, self.listeInfos[line * 2 + 1]))
            ]
            self.libraries.append(
                Library(nbBooks, books, signUpTime, booksPerDay, line - 1)
            )

    def reset_assigned(self):
        """Reset par sécurité"""
        self.assigned_books, self.assigned_libraries = set(), set()


class Library:
    def __init__(
        self,
        nbBooks=0,
        books=[],
        signUpTime=0,
        booksPerDay=0,
        id=0,
        totalPts=0,
        ratio=1,
        scanningTime=0,
    ):
        self.nbBooks = nbBooks
        self.books = books
        self.signUpTime = signUpTime
        self.booksPerDay = booksPerDay
        self.id = id
        self.totalPts = totalPts
        self.ratio = ratio
        self.scanningTime = scanningTime

    def calculate_pts_per_day(self, assigned_books=set(), assigned_libraries=set()):
        """ Calcule le ratio points/jour de la bibliothèque en fonction des livres déjà assignés."""
        if self in assigned_libraries:
            self.ratio = float(
                "-inf"
            )  # Si la bibliothèque est déjà assignée, on lui donne un score de -inf pour l'ignorer par la suite.
        else:
            self.totalPts = sum([book.score for book in self.books])
            self.ratio = self.totalPts / self.signUpTime

    def sort_books(self, maxTime, assigned_books=set(), currentTime=0):
        """ Redéfinis la liste de livres de la library, dans l'ordre décroissant de score, en limitant par rapport au temps max le nombre de livres.
        Redéfinis aussi le temps de scan total de la library"""
        timeleft = maxTime - self.signUpTime - currentTime
        available_books = [book for book in self.books if book.id not in assigned_books]
        available_books.sort(key=attrgetter("score"), reverse=True)
        self.books = available_books[: timeleft * self.booksPerDay]
        self.scanningTime = len(available_books) * self.booksPerDay


liste_problemes = []
file_index = 0

for FILE in os.listdir("."):
    total_score = 0
    if not FILE.endswith(".txt"):
        continue
    with open(FILE, "r") as file:
        lines = file.readlines()
        nbBooks, nbLibraries, nbDays = list(map(int, lines[0].strip().split()))
        liste_problemes.append(Problem(nbBooks, nbLibraries, nbDays))
        problem = liste_problemes[file_index]
        problem.listeInfos = [line.strip().split() for line in lines]
        problem.reset_assigned()
        problem.fill()

    for library in problem.libraries:
        library.calculate_pts_per_day()

    currentTime = 0

    # Structure de données pour le resultat :
    libs_scanned = []
    books_scanned = []

    for _ in tqdm(range(len(problem.libraries))):
        available_libraries = list(
            set(problem.libraries) - set(problem.assigned_libraries)
        )
        for library in available_libraries:
            library.sort_books(problem.nbDays, problem.assigned_books, currentTime)
        for library in available_libraries:
            library.calculate_pts_per_day(problem.assigned_books)

        currentLibrary = max(available_libraries, key=attrgetter("ratio"))

        if (currentTime + currentLibrary.signUpTime) > problem.nbDays:
            # Si on dépasse le temps imparti, on sort de la boucle
            break
        else:
            # Assignation
            libs_scanned.append(currentLibrary)
            books_scanned.append([])
            problem.assigned_libraries.add(currentLibrary)
            currentTime += currentLibrary.signUpTime

            for book in currentLibrary.books:
                if book.id not in problem.assigned_books:
                    problem.assigned_books.add(book.id)
                    books_scanned[-1].append(
                        str(book.id)
                    )  # Conversion en String pour utilisation plus facile pendant l'ecriture

    # Calcul du score
    for booklist in books_scanned:
        for book in booklist:
            total_score += int(problem.listeInfos[1][int(book)])

    # Ecriture du fichier d'output
    with open("{}.out".format(FILE), "w+") as file:
        file.write("{} \n".format(len(libs_scanned)))
        for index, element in enumerate(libs_scanned):
            chain_lib = "{} {}".format(element.id, len(element.books))
            file.write(chain_lib + "\n")
            chain_books = " ".join(books_scanned[index])
            file.write(chain_books + "\n")

    file_index += 1
    print("Ran {} successfully, score = {}".format(FILE, total_score))
