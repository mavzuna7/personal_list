document.addEventListener('DOMContentLoaded', function() {
    const openFilterModal = document.getElementById('openFilterModal');
    const filterModal = document.getElementById('filterModal');
    const closeFilterModal = document.getElementById('closeFilterModal');
    const closeFilterModalBtn = document.getElementById('closeFilterModalBtn');
    const searchButton = document.getElementById('search-content');
    const searchInput = document.getElementById('content-search');
    const contentTypeInputs = document.querySelectorAll('input[name="content_type"]');
    const genreSelect = document.getElementById('id_genre');

    // Фильтры (только если есть на странице)
    if (openFilterModal && filterModal && closeFilterModal && closeFilterModalBtn) {
        openFilterModal.addEventListener('click', function() {
            filterModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
        closeFilterModal.addEventListener('click', function() {
            filterModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        closeFilterModalBtn.addEventListener('click', function() {
            filterModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && filterModal.style.display === 'block') {
                filterModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }

    // Поиск по TMDB (работает всегда, если есть кнопка)
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const title = searchInput.value.trim();
            if (!title) {
                alert('Пожалуйста, введите название фильма или сериала');
                return;
            }
            let contentType = 'movie';
            contentTypeInputs.forEach(input => {
                if (input.checked) {
                    contentType = input.value;
                }
            });
            searchButton.disabled = true;
            searchButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Поиск...';
            fetch(`/api/search-content/?title=${encodeURIComponent(title)}&type=${contentType}`)
                .then(response => response.json())
                .then(data => {
                    searchButton.disabled = false;
                    searchButton.innerHTML = 'Поиск';
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    document.getElementById('id_title').value = data.title || '';
                    document.getElementById('id_description').value = data.description || '';
                    document.getElementById('id_release_year').value = data.release_year || '';
                    document.getElementById('id_country').value = data.country || '';
                    document.getElementById('id_director').value = data.director || '';
                    document.getElementById('id_actor').value = data.actors || '';
                    if (data.rating) {
                        document.getElementById('id_rating').value = parseFloat(data.rating);
                    }
                    if (data.poster_path) {
                        const posterPreview = document.getElementById('poster-preview');
                        let posterUrl = data.poster_path;
                        // Если путь не начинается с '/', значит это относительный путь в media
                        if (posterUrl && !posterUrl.startsWith('/')) {
                            posterUrl = '/media/' + posterUrl;
                        }
                        posterPreview.innerHTML = `
                            <img src="${posterUrl}" class="img-thumbnail" style="max-height: 200px;">
                            <input type="hidden" name="poster_path" value="${data.poster_path}">
                        `;
                    }
                    if (data.genre && genreSelect) {
                        genreSelect.value = data.genre;
                    }
                })
                .catch(() => {
                    searchButton.disabled = false;
                    searchButton.innerHTML = 'Поиск';
                    alert('Ошибка при поиске.');
                });
        });
    }
});

