import csv
import os
import sys
import time
from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    os.system('clear')
    print("Data loaded.")
    while True:
        source = person_id_for_name(input("1) Name: "))
        if source is None:
            print("Person not found.")
            continue
        target = person_id_for_name(input("2) Name: "))
        if target is None or target is source:
            print("Person not found.")
            continue
        path = shortest_path(source, target)
        if path is None:
            print("Not connected.")
        else:
            degrees = len(path)
            print(f"{degrees} degrees of separation.")
            path = [(None, source)] + path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")
            print("")


def main_timed():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "small"

    # Load data from files into memory
    start_l = time.time()
    print("Loading data...")
    load_data(directory)
    os.system('clear')
    print("Data loaded.")
    end_l = time.time()
    print(f"Loading Time: {end_l-start_l}")
    while True:
        source = person_id_for_name(input("1) Name: "))
        if source is None:
            print("Person not found.")
            continue
        target = person_id_for_name(input("2) Name: "))
        if target is None or target is source:
            print("Person not found.")
            continue
        start_s = time.time()
        path = shortest_path(source, target)
        end_s = time.time()
        print(f"Searching Time: {end_s - start_s}")
        if path is None:
            print("Not connected.")
        else:
            degrees = len(path)
            print(f"{degrees} degrees of separation.")
            path = [(None, source)] + path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")
            print("")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    frontier = QueueFrontier()
    num_steps = 0
    start = Node(state=source, parent=None, action=None)
    frontier.add(start)
    explored = set()
    solution = []
    while True:
        if frontier.empty():
            return None
        node = frontier.remove()
        explored.add(node.state)
        num_steps += 1
        for movie, actor in neighbors_for_person(node.state):
            if not frontier.contains_state(actor) and actor not in explored:
                child = Node(state=actor, parent=node, action=movie)
                if child.state == target:
                    movie_ids = []
                    actor_ids = []
                    while child.parent is not None:
                        movie_ids.append(child.action)
                        actor_ids.append(child.state)
                        child = child.parent
                    movie_ids.reverse()
                    actor_ids.reverse()
                    for i in range(len(movie_ids)):
                        solution.append((movie_ids[i], actor_ids[i]))
                    return solution
                frontier.add(child)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main_timed()
