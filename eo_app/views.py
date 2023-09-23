        
from django.shortcuts import render, redirect
from django.http import request, JsonResponse
import requests
from .models import Creator, Tag, Show, Comment, StaffFavorite, CreatorOfTheMonth, InfluentialShow
from django.shortcuts import get_object_or_404

# For show recommendation function
import urllib.parse
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from django.db.models import Count

# For search
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Count, Q, F, Max, ExpressionWrapper, Value
from django.db.models.functions import Cast, Power
import random
from django.shortcuts import reverse
from datetime import datetime


# Other search imports for cacheing
from django.views.decorators.cache import cache_page


# For Email functionality 
from .forms import CommentForm
from django.core.mail import send_mail
from django.conf import settings
# from episode_one.secrets import EMAIL_HOST_USER
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "default_email@example.com")

import os
api_key = os.environ.get('API_KEY')
# api_key = os.environ.get('API_KEY')
base_url = 'https://api.themoviedb.org/3/search/tv'


def main(request):
    pk = Show.objects.all()
    return render(request, 'main.html', {'pk':pk})

def get_staff_favorites(request):
    return StaffFavorite.objects.all()

def all_staff_favorites(request):
    staff_favorites = StaffFavorite.objects.all()
    return render(request, 'all_staff_favorites.html', {'staff_favorites': staff_favorites})


# Function to get creators of the current month
def get_creators_of_the_month(request):
    # Gets the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Gets the list of existing creator IDs for the current month and year
    existing_creator_ids = CreatorOfTheMonth.objects.filter(month=current_month, year=current_year).values_list('creator_id', flat=True)
    creators_not_selected = Creator.objects.exclude(id__in=existing_creator_ids)

    # Checks if there are less than 10 creators not selected for this month
    if len(creators_not_selected) < 10:
        # Gets 10 random creators of the month
        creators_of_the_month = CreatorOfTheMonth.objects.filter(month=current_month, year=current_year).order_by('?')[:10]
    else:
        # Selects 10 random creators who have not been selected before
        random_creators = random.sample(list(creators_not_selected), 10)
        creators_of_the_month = []

        # Creates CreatorOfTheMonth objects for the selected creators
        for creator in random_creators:
            creator_of_the_month = CreatorOfTheMonth(creator=creator, month=current_month, year=current_year)
            creator_of_the_month.save()
            creators_of_the_month.append(creator_of_the_month)

    # Updates creator details and images for CreatorOfTheMonth objects
    for creator_of_the_month in creators_of_the_month:
        creator_obj = creator_of_the_month.creator
        creator_image_url = ""

        # Checks if the creator has an image associated with it
        if creator_obj.image:
            creator_image_url = creator_obj.image.url
        else:
            # Retrieves the creator image from the API
            api_search_url = requests.get(f'https://api.themoviedb.org/3/search/person?api_key={api_key}&language=en-US&page=1&include_adult=false&query={creator_obj.name}')
            creator_search_results = api_search_url.json()

            creator_data = creator_search_results.get('results', [{}])[0]
            creator_image = creator_data.get('profile_path')

            # Gets the formatted image URL or use default image URL if no image available
            if creator_image:
                creator_image_url = f"https://image.tmdb.org/t/p/w500/{creator_image}"
            else:
                creator_image_url = "/static/images/default_creator_image.jpg"

        # Updates CreatorOfTheMonth object with creator details and image URL
        creator_of_the_month.creator_image = creator_image_url
        creator_of_the_month.creator_id = creator_obj.id
        
        # Adds additional fields to CreatorOfTheMonth object
        creator_of_the_month.creator_name = creator_obj.name
        creator_of_the_month.current_scripts = creator_obj.shows.all()

    # Returns the list of CreatorOfTheMonth objects
    return creators_of_the_month


def index(request):
    # Gets the search query from the request parameters
    search_query = request.GET.get('search')

    # Gets all shows, ordered by creation date
    shows = Show.objects.all().order_by('-created')

    # Gets staff favorites using a separate function (not shown here)
    staff_favorites = get_staff_favorites(request)

    # Gets creators of the month using a separate function (not shown here)
    creators_of_the_month = get_creators_of_the_month(request)

    # Gets influential shows along with their associated creators using select_related and prefetch_related
    influential_shows = InfluentialShow.objects.select_related('show').prefetch_related('show__creators').all()

    # Filters shows based on the search query if it exists
    if search_query:
        shows = shows.filter(
            Q(creators__name__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(tags__genre__icontains=search_query)
        ).distinct()

    # Checks if the request is an AJAX request (XMLHttpRequest)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # Prepares results for AJAX response, containing title and poster URL of each show
        results = [{'title': show.title, 'poster': show.poster.url} for show in shows]
        return JsonResponse({'results': results})

    # Renders the index.html template with the required context data
    return render(request, 'index.html', {
        'shows': shows,
        'staff_favorites': staff_favorites,
        'creators_of_the_month': creators_of_the_month,
        'influential_shows': influential_shows
    })


@cache_page(60 * 15)  # Caches the view for 15 minutes
def search(request):
    # Gets the search query from the request parameters
    search_query = request.GET.get('search')
    
    # Gets all shows
    shows = Show.objects.all()

    # Filters shows based on the search query if it exists
    if search_query:
        shows = shows.filter(
            Q(title__icontains=search_query) |
            Q(creators__name__icontains=search_query) |
            Q(tags__genre__icontains=search_query)
        ).distinct()

    # Uses prefetch_related to fetch related creators and tags to avoid additional queries
    shows = shows.prefetch_related('creators', 'tags')

    # Checks if the request is an AJAX request (XMLHttpRequest)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Prepares results for AJAX response, containing title and poster URL of each show
        results = []
        for show in shows:
            results.append({
                'title': show.title,
                'poster': show.poster.url if show.poster else None
            })
        return JsonResponse({'results': results})

    # Paginates the shows with a custom paginate_shows function (not shown here)
    paginate_by = 15
    shows_page = paginate_shows(request, shows, paginate_by)

    # Prepares the context data for rendering the search_results.html template
    context = {
        'search_term': search_query,
        'results': shows_page
    }

    # Renders the search_results.html template with the context data
    return render(request, 'search_results.html', context)


def paginate_shows(request, shows, paginate_by):
    # Creates a Paginator object with the provided shows and the number of shows per page
    paginator = Paginator(shows, paginate_by)
    
    # Gets the page number from the request's GET parameters
    page_number = request.GET.get('page')
    
    # Gets the Page object for the requested page number
    # If the page number is invalid or not provided, it defaults to the first page
    page_obj = paginator.get_page(page_number)

    # Returns the Page object containing the shows for the requested page
    return page_obj


def rest_of_influential_shows(request):
    # Gets all influential shows with related show objects and their creators prefetched
    influential_shows = InfluentialShow.objects.select_related('show').prefetch_related('show__creators').all()

    # Prepares the context data for rendering the influential_shows.html template
    context = {
        'influential_shows': influential_shows,
    }

    # Renders the influential_shows.html template with the context data
    return render(request, 'influential_shows.html', context)



def creator_page(request, id):
    # Gets the Creator object based on the provided ID
    creator_obj = Creator.objects.get(id=id)

    # API calls to search for the creator and obtain their TMDB ID
    api_search_url = requests.get(f'https://api.themoviedb.org/3/search/person?api_key={api_key}&language=en-US&page=1&include_adult=false&query={creator_obj}')
    creator_search_results = api_search_url.json()

    # Retrieves the TMDB ID of the creator
    creator_tmdb_id = creator_search_results.get('results', [{}])[0].get('id')

    # API calls to retrieve detailed creator information using the TMDB ID
    api_person_url = requests.get(f"https://api.themoviedb.org/3/person/{creator_tmdb_id}?api_key={api_key}&language=en-US")
    creator_info = api_person_url.json()

    # Retrieves the creator's image URL from the API or uses a default if not available
    creator_image = creator_info.get('profile_path')
    creator_image_url = ""
    if creator_image:
        creator_image_url = f"https://image.tmdb.org/t/p/w500/{creator_image}"
    elif creator_obj.image:
        creator_image_url = creator_obj.image.url
    else:
        creator_image_url = "/static/images/default_creator_image.jpg"

    # Retrieves similar creators based on show tag/genres and gender
    similar_creators = Creator.objects.annotate(
        tag_count=Count('shows__tags'),
        matching_tags=Count('shows__tags', filter=Q(shows__tags__in=creator_obj.shows.values('tags')))
    ).exclude(id=creator_obj.id).order_by('-matching_tags', '-tag_count')

    # Calculates the weight based on the number of shows for each creator
    max_show_count = Creator.objects.aggregate(Max('shows__count'))['shows__count__max'] or 1
    similar_creators = similar_creators.annotate(
        weight=ExpressionWrapper(
            (F('matching_tags') / F('tag_count')) * Power(1 / (F('shows__count') + 1), 0.2),
            output_field=models.FloatField()
        )
    ).order_by('-weight')

    # Shuffles the queryset to introduce randomness
    similar_creators = list(similar_creators)
    random.shuffle(similar_creators)

    # If the current creator is female, prioritizes female creators in the recommendation
    if creator_obj.gender == 'F':
        similar_creators = [c for c in similar_creators if c.gender == 'F' or c.gender == 'O']

    random.shuffle(similar_creators)
    similar_creators = similar_creators[:9]

    # Initializes an empty dictionary to store recommended creators data
    recom_creators = {}
    for similar_creator in similar_creators:
        # API calls to search for the similar creator and obtain their TMDB ID
        api_search_url = requests.get(f'https://api.themoviedb.org/3/search/person?api_key={api_key}&language=en-US&page=1&include_adult=false&query={similar_creator.name}')
        similar_creator_search_results = api_search_url.json()

        # Retrieves the similar creator's name and profile path
        similar_creator_data = similar_creator_search_results.get('results', [{}])[0]
        similar_creator_name = similar_creator_data.get('name')
        similar_creator_profile_path = similar_creator_search_results.get('results', [{}])[0].get('profile_path')
       
        similar_creator_data['profile_path'] = f"https://image.tmdb.org/t/p/w500/{similar_creator_profile_path}" if similar_creator_profile_path else ""

        # Adds the similar creator's data to the recommended creators dictionary
        recom_creators[similar_creator.id] = {
            'name': similar_creator_name,
            'profile_path': similar_creator_profile_path,
            'creator_obj': similar_creator  # Adds the creator object to the data
        }
    
    # Initializes an empty list to store show data
    show_data_list = []

    # Iterates over each show in the creator's shows
    for show in creator_obj.shows.all():
        # Performs API call to retrieve show data
        show_url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&language=en-US&page=1&include_adult=false&query={show.title}"
        api_response = requests.get(show_url).json()
        results = api_response.get('results', [])

        # Checks if there are any results
        if results:
            # Retrieves the first result
            show_data = results[0]
            # Extracts the poster URL from the show data
            poster_url = f"https://image.tmdb.org/t/p/w500/{show_data.get('poster_path')}"
        else:
            # Uses a default poster image if no results found
            poster_url = "/static/images/default_creator_image.jpg"

        # Creates a dictionary containing show ID and poster URL
        show_info = {
            'id': show.id,
            'show': show.title,
            'poster_url': poster_url,
        }

        # Appends the show information to the list
        show_data_list.append(show_info)

    # Prepares the context data for rendering the template
    context = {
        "creator": creator_obj,
        "creator_info": creator_info,
        "creator_image": creator_image_url,
        "recom_creators": recom_creators,
        "show_data_list": show_data_list,
    }

    # Renders the template with the context data
    return render(request, "creator_page.html", context)



def show_page(request, id):
    # Gets the Show object based on the provided ID
    show_obj = Show.objects.get(id=id)

    # API calls to search for the show and obtain its TMDB ID
    show_url = requests.get(F"https://api.themoviedb.org/3/search/tv?api_key={api_key}&language=en-US&page=1&include_adult=false&query={show_obj}")

    show_info = show_url.json()

    # Grabs the id of 'show' from the TMDB API
    show_tmdb_id = show_info['results'][0]['id']

    try:
        # Grabs json object for the specific 'show' page.
        api_show_url = requests.get(F"https://api.themoviedb.org/3/tv/{show_tmdb_id}?api_key={api_key}&language=en-US")
        show_info = api_show_url.json()

        # Fetchs the necessary details from the API response
        # ...

        # Adds the show info from the API to the 'show_info' dictionary
        show_info['poster_path'] = show_info['poster_path']
        show_info['id'] = show_tmdb_id

    except Exception as e:
        # Handles the exception when the API call fails
        # Logs the error or perform any other necessary actions

        # Uses the information from your database instead
        show_info = {
            'title': show_obj.title,
            'description': show_obj.description,
            'poster_path': show_obj.poster_path,
            'id': show_tmdb_id,
            # Adds other relevant fields from your Show model
        }

    # Fetching API data with recommendation results
    recom_show_data = []

    # Prefetch_related to improve performance for related fields
    fetch = Show.objects.all().prefetch_related('creators')

    for show_title in fetch:
        genre_data = show_title.tags.all()
        show_title_id = show_title.id
        recom_show_data.append((show_title, genre_data, show_title_id))

    # Creates a DataFrame from the fetched data for processing
    df = pd.DataFrame(recom_show_data, columns=['Title', 'Genre', 'Show_id'])
    check = df.isnull().values.any()

    # Combines the title and genre data into a single feature for similarity calculation
    df['important_features'] = df['Title'].astype(str) + df['Genre'].astype(str)

    # Converts the important features into a matrix using CountVectorizer
    cm = CountVectorizer().fit_transform(df['important_features'])
    cs = cosine_similarity(cm)

    # Finds the index of the current show in the DataFrame
    matched_show_id = df[df.Title == show_obj]['Show_id'].index[0]

    # Calculates the similarity scores for all shows
    scores = list(enumerate(cs[matched_show_id]))

    # Sorts the scores in descending order to get recommended shows
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    sorted_scores = sorted_scores[1:]

    # Initializes an empty list to store recommended show titles
    show_title_list = []

    # Gets the top 7 similar shows (excluding the current show)
    j = 0
    for item in sorted_scores:
        show_title = df[df.index == item[0]]['Title'].values[0]
        j = j + 1
        if j > 7:
            break
        show_title_list.append(show_title)

    # Initializes an empty dictionary to store API data for recommended shows
    recom_api_data_dict = {}
    for i in show_title_list:
        # API calls to search for the recommended show and obtain its details
        recom_api_data = requests.get(F"https://api.themoviedb.org/3/search/tv?api_key={api_key}&language=en-US&page=1&include_adult=false&query={i}").json()
        api_title = recom_api_data['results'][0]['name']
        api_poster = recom_api_data['results'][0]['poster_path']
        api_id = recom_api_data['results'][0]['id']
        try:
            # Tries to get the recommended show from your database
            recommended_show = Show.objects.get(title=api_title)
            recommended_show_id = recommended_show.id
            # Appends all search results to the recom_api_data_dict dictionary
            recom_api_data_dict[api_title] = {'poster_path': api_poster, 'id': recommended_show_id}

        except Show.DoesNotExist:
            # Handles the case when the recommended show is not found in your database
            # Logs the error or perform any other necessary actions
            pass

    # Prepares the context data for rendering the template
    context = {
        'show': show_obj,
        'show_info': show_info,
        'recom_data': recom_api_data_dict
    }

    # Renders the template with the context data
    return render(request, 'show_page.html', context)


def about(request):
    return render(request, 'about.html')


def comment(request):
    return render(request, 'comment.html')


def comment_submit(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save()
            
            # Retrieves name, email, and message from the comment object or form.cleaned_data
            name = comment.name
            email = comment.email
            message = comment.message
            
            # Sends email notification
            subject = 'New User Message'
            email_message = f'You have received a new message from {name} ({email}).\n\nMessage: {message}'
            recipient_list = [EMAIL_HOST_USER] 
            from_email = settings.DEFAULT_FROM_EMAIL
            
            send_mail(subject, email_message, from_email, recipient_list, fail_silently=False)
            
            return redirect('/')
    return redirect('/')


def news(request):
    return render(request, 'news.html')

def reviews(request):
    return render(request, 'reviews.html')
