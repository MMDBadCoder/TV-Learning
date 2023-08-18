import datetime

from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

from TV_LEARNING.settings import ELASTIC_LIMIT_SEARCH_RESULT, RESPONSE_LIMIT_SEARCH_RESULT
from common_utils.elasticsearch import ElasticConnectionFactory
from english_words_difficulty.difficulty_service import Difficulty
from movies_manager.models import Movie


def search_on_quotes(request, query_text):
    if query_text == '':
        return HttpResponseBadRequest("query text can not be blank")
    es = ElasticConnectionFactory.get_instance()
    search_body = {
        "size": ELASTIC_LIMIT_SEARCH_RESULT,
        "query": {
            "nested": {
                "path": "quote",
                "query": {
                    "match": {
                        "quote.text": {
                            "query": query_text,
                            "fuzziness": "1"
                        }
                    }
                }
            }
        }
    }
    results = es.search(index='quotes', body=search_body)
    hits = [hit for hit in results['hits']['hits']]

    # Enriching by movie data
    sequences = []
    for hit in hits:
        sequence = dict(hit['_source'])
        sequence['search_score'] = hit['_score']
        movie_id = sequence['movie_id']
        movie = Movie.objects.get(id=movie_id)
        sequence['movie'] = movie

        # Determining start time of sequence
        sequence_start_time = max(0, sequence['quote']['start_time'] - 4)
        if sequence.__contains__('last_quote_time'):
            sequence_start_time = max(sequence['last_quote_time'] - 2, sequence_start_time)
        sequence['start_time'] = sequence_start_time
        sequence['display_second'] = str(datetime.timedelta(seconds=int(sequence_start_time)))

        # Determining end time of sequence
        sequence_end_time = sequence['quote']['end_time'] + 4
        if sequence.__contains__('next_quote_time'):
            sequence_end_time = min(sequence_end_time, sequence['next_quote_time'] + 2)
        sequence['end_time'] = sequence_end_time

        sequences.append(sequence)

    # Filtering hidden movies
    sequences = list(filter(lambda s: s['movie'].visible, sequences))

    # Sorting
    sequences = sorted(sequences, key=lambda s: get_difficulty_of_sequence(s))

    data = {
        'query_text': query_text,
        'sequences': sequences[:RESPONSE_LIMIT_SEARCH_RESULT]
    }
    return render(request, 'results.html', data)


def search_box(request):
    if request.POST:
        query_text = request.POST['query_text']
        if query_text is None:
            return HttpResponseBadRequest("missing query text")
        return redirect('user-quote-search-by-url', query_text)
    return render(request=request, template_name='search_page.html')


def get_difficulty_of_sequence(sequence):
    quote = sequence['quote']
    speach_speed = (len(quote['text']) / quote['duration'])
    words_difficulty = Difficulty.get_instance().get_difficulty_of_text(quote['text'])
    return speach_speed + words_difficulty - sequence['search_score'] * 2
