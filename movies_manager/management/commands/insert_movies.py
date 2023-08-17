from django.core.management import BaseCommand

from movies_manager.models import Movie


class Command(BaseCommand):
    help = 'Insertion of movies from tsv file to our light db'

    def add_arguments(self, parser):
        parser.add_argument('movie_index', help='Index of movie argument')

    def handle(self, *args, **options):
        movie_index = options['movie_index']
        if movie_index.__contains__(':'):
            parts = list(map(int, movie_index.split(':')))
            movie_indices = list(range(parts[0], parts[1] + 1))
        else:
            movie_indices = [int(movie_index)]
        insert(movie_indices)


def insert(movies_indices):
    with open('all_movies.tsv', 'r') as movies_file:

        def try_to_create_model_object(line):
            parts = line.split('\t')
            index = int(parts[0])
            genre = parts[1]
            title1 = parts[2]
            title2 = parts[3]
            votes_count = int(parts[4])
            rating = float(parts[5])

            if Movie.objects.filter(id=index).exists():
                print("Id of this movie {} by id of {} occupied by another".format(title1, index))
                return
            Movie.objects.create(id=index, title1=title1, title2=title2, genre=genre,
                                 votes_count=votes_count, imdb_rating=rating)
            print('{} was inserted to db'.format(title1))

        def get_index_of_line(line):
            return int(line.split('\t')[0])

        movies_file.readline()
        line_by_index = {}
        while True:
            line = movies_file.readline()
            if not line:
                break
            index = get_index_of_line(line)
            line_by_index[index] = line

        for index in movies_indices:
            try_to_create_model_object(line_by_index[index])
