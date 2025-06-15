document.addEventListener('DOMContentLoaded', function() {
    const filterButton = document.getElementById('filterButton');
    const filterDropdown = document.getElementById('filterDropdown');
    const recommendationsButton = document.getElementById('recommendationsButton');
    const recommendationsDropdown = document.getElementById('recommendationsDropdown');
    let isFilterDropdownVisible = false;
    let isRecommendationsDropdownVisible = false;

    // Функция для закрытия всех выпадающих окон
    function closeAllDropdowns() {
        filterDropdown.classList.remove('show');
        recommendationsDropdown.classList.remove('show');
        isFilterDropdownVisible = false;
        isRecommendationsDropdownVisible = false;
    }

    // Функция для закрытия выпадающего окна при клике вне его
    function closeDropdown(event) {
        if (!filterDropdown.contains(event.target) && 
            !filterButton.contains(event.target) &&
            !recommendationsDropdown.contains(event.target) &&
            !recommendationsButton.contains(event.target)) {
            closeAllDropdowns();
        }
    }

    // Обработчик клика по кнопке фильтров
    filterButton.addEventListener('click', function(event) {
        event.stopPropagation();
        if (isRecommendationsDropdownVisible) {
            recommendationsDropdown.classList.remove('show');
            isRecommendationsDropdownVisible = false;
        }
        isFilterDropdownVisible = !isFilterDropdownVisible;
        filterDropdown.classList.toggle('show');
    });

    // Обработчик клика по кнопке рекомендаций
    recommendationsButton.addEventListener('click', function(event) {
        event.stopPropagation();
        if (isFilterDropdownVisible) {
            filterDropdown.classList.remove('show');
            isFilterDropdownVisible = false;
        }
        isRecommendationsDropdownVisible = !isRecommendationsDropdownVisible;
        recommendationsDropdown.classList.toggle('show');
    });

    // Обработчик клика по документу для закрытия выпадающих окон
    document.addEventListener('click', closeDropdown);

    // Предотвращаем закрытие при клике внутри выпадающих окон
    filterDropdown.addEventListener('click', function(event) {
        event.stopPropagation();
    });

    recommendationsDropdown.addEventListener('click', function(event) {
        event.stopPropagation();
    });
}); 