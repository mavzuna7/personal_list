import os
import requests
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class MovieService:
    def __init__(self):
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        self.tmdb_base_url = 'https://api.themoviedb.org/3'
        self.tmdb_image_base_url = 'https://image.tmdb.org/t/p'

    def search_content(self, query: str, content_type: str = 'movie') -> Dict:
        """Поиск информации о фильме или сериале с использованием TMDb API (русский, затем английский)"""
        if content_type == 'movie':
            result, error = self._search_tmdb_movie(query, language='ru-RU')
            if not result:
                result, error = self._search_tmdb_movie(query, language='en-US')
            if not result and error:
                return {'error': error}
            return result
        else:
            result, error = self._search_tmdb_tv(query, language='ru-RU')
            if not result:
                result, error = self._search_tmdb_tv(query, language='en-US')
            if not result and error:
                return {'error': error}
            return result

    def _search_tmdb_movie(self, query: str, language: str = 'ru-RU') -> Tuple[Dict, Optional[str]]:
        try:
            response = requests.get(
                f'{self.tmdb_base_url}/search/movie',
                params={
                    'api_key': self.tmdb_api_key,
                    'query': query,
                    'language': language
                }
            )
            if response.status_code != 200:
                print('TMDb error:', response.text)
                return { }, f"TMDb error: {response.text}"
            results = response.json().get('results', [])
            if results:
                movie_id = results[0]['id']
                details = self._get_tmdb_movie_details(movie_id, language)
                if details:
                    return ({
                        'title': details.get('title', ''),
                        'original_title': details.get('original_title', ''),
                        'description': details.get('overview', ''),
                        'release_year': details.get('release_date', '')[:4],
                        'country': ', '.join([c.get('name', '') for c in details.get('production_countries', [])]),
                        'director': ', '.join([c.get('name', '') for c in details.get('credits', {}).get('crew', []) if c.get('job') == 'Director']),
                        'actors': ', '.join([c.get('name', '') for c in details.get('credits', {}).get('cast', [])[:5]]),
                        'poster_url': f"{self.tmdb_image_base_url}/original{details.get('poster_path', '')}" if details.get('poster_path') else '',
                        'rating': details.get('vote_average', ''),
                        'genres': [g.get('name', '') for g in details.get('genres', [])],
                        'tmdb_id': movie_id,
                        'tmdb_type': 'movie',
                    }, None)
            return { }, None
        except Exception as e:
            print(f"Ошибка при поиске на TMDb: {e}")
            return { }, str(e)

    def _search_tmdb_tv(self, query: str, language: str = 'ru-RU') -> Tuple[Dict, Optional[str]]:
        try:
            response = requests.get(
                f'{self.tmdb_base_url}/search/tv',
                params={
                    'api_key': self.tmdb_api_key,
                    'query': query,
                    'language': language
                }
            )
            if response.status_code != 200:
                print('TMDb error:', response.text)
                return { }, f"TMDb error: {response.text}"
            results = response.json().get('results', [])
            if results:
                tv_id = results[0]['id']
                details = self._get_tmdb_tv_details(tv_id, language)
                if details:
                    return ({
                        'title': details.get('name', ''),
                        'original_title': details.get('original_name', ''),
                        'description': details.get('overview', ''),
                        'release_year': details.get('first_air_date', '')[:4],
                        'country': ', '.join([c.get('name', '') for c in details.get('production_countries', [])]),
                        'director': ', '.join([c.get('name', '') for c in details.get('credits', {}).get('crew', []) if c.get('job') == 'Director']),
                        'actors': ', '.join([c.get('name', '') for c in details.get('credits', {}).get('cast', [])[:5]]),
                        'poster_url': f"{self.tmdb_image_base_url}/original{details.get('poster_path', '')}" if details.get('poster_path') else '',
                        'rating': details.get('vote_average', ''),
                        'genres': [g.get('name', '') for g in details.get('genres', [])],
                        'tmdb_id': tv_id,
                        'tmdb_type': 'tv',
                    }, None)
            return { }, None
        except Exception as e:
            print(f"Ошибка при поиске на TMDb: {e}")
            return { }, str(e)

    def _get_tmdb_movie_details(self, movie_id: int, language: str = 'ru-RU') -> Optional[Dict]:
        try:
            response = requests.get(
                f'{self.tmdb_base_url}/movie/{movie_id}',
                params={
                    'api_key': self.tmdb_api_key,
                    'language': language,
                    'append_to_response': 'credits'
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при получении деталей фильма с TMDb: {e}")
        return None

    def _get_tmdb_tv_details(self, tv_id: int, language: str = 'ru-RU') -> Optional[Dict]:
        try:
            response = requests.get(
                f'{self.tmdb_base_url}/tv/{tv_id}',
                params={
                    'api_key': self.tmdb_api_key,
                    'language': language,
                    'append_to_response': 'credits'
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при получении деталей сериала с TMDb: {e}")
        return None 