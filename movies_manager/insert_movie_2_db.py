# We use this logic to insert movie from csv file to our server light database
# insert() should be called in wsgi.py file at TV_LEARNING directory to be executed at startup time

from movies_manager.models import Movie

movies_index_range = range(1, 11)


def insert():
    with open('all_movies.csv', 'r') as movies_file:
        movies_file.readline()
        while True:
            if int(movies_file.readline().split('\t')[0]) in movies_index_range:
                break
        while True:
            line = movies_file.readline().strip()
            parts = line.split('\t')
            index = int(parts[0])
            if index not in movies_index_range:
                break
            genre = parts[1]
            title1 = parts[2]
            title2 = parts[3]
            votes_count = int()
            rating = float(parts[5])

            if not Movie.objects.filter(id=index):
                raise Exception("Id of this movie is occupied by another movie: {}".format(line))
            Movie.objects.create(id=index, title1=title1, title2=title2, votes_count=votes_count, rating=rating)
