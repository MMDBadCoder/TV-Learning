# We use this logic to insert movie from csv file to our server light database
# insert() should be called in wsgi.py file at TV_LEARNING directory to be executed at startup time

from movies_manager.models import Movie

movies_index_range = range(1, 11)


def insert():
    with open('all_movies.csv', 'r') as movies_file:

        def try_to_create_model_object(line):
            parts = line.split('\t')
            index = int(parts[0])
            genre = parts[1]
            title1 = parts[2]
            title2 = parts[3]
            votes_count = int(parts[4])
            rating = float(parts[5])

            if Movie.objects.filter(id=index).exists():
                print("Id of this movie is occupied by another movie: {}".format(line))
                return
            Movie.objects.create(id=index, title1=title1, title2=title2, genre=genre,
                                 votes_count=votes_count, imdb_rating=rating)

        def get_index_of_line(line):
            return int(line.split('\t')[0])

        movies_file.readline()
        while True:
            line = movies_file.readline()
            index = get_index_of_line(line)
            if index not in movies_index_range:
                continue
            try_to_create_model_object(line)
            while True:
                line = movies_file.readline()
                index = get_index_of_line(line)
                if index not in movies_index_range:
                    return
                try_to_create_model_object(line)
