document.addEventListener('DOMContentLoaded', function() {
    const openFilterModal = document.getElementById('openFilterModal');
    const filterModal = document.getElementById('filterModal');
    const closeFilterModal = document.getElementById('closeFilterModal');
    const closeFilterModalBtn = document.getElementById('closeFilterModalBtn');

    // Открытие модального окна
    openFilterModal.addEventListener('click', function() {
        filterModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    });

    // Закрытие модального окна при клике на оверлей
    closeFilterModal.addEventListener('click', function() {
        filterModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    });

    // Закрытие модального окна при клике на кнопку закрытия
    closeFilterModalBtn.addEventListener('click', function() {
        filterModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    });

    // Закрытие модального окна при клике на Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && filterModal.style.display === 'block') {
            filterModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
});

