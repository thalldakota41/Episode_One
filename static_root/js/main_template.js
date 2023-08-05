

(function() {

  // Gets the search input element
  const searchInput = $('#search');

  // Gets the search results container element
  const searchResultsContainer = $('#search-results');

  // Attachs an autocomplete behavior to the search input
  searchInput.autocomplete({

    // The source function to fetch autocomplete suggestions
    source: function(request, response) {

      // Trims the search query and store it in a variable
      const searchQuery = request.term.trim();

      // If the search query is empty, clears the search results container and return
      if (searchQuery === '') {
        searchResultsContainer.empty();
        return;
      }

      // Performs an AJAX request to get search results from the server
      $.ajax({
        url: '/search/',
        method: 'GET',
        data: { search: searchQuery },
        success: function(data) {
          // If the server returns results, formats and displays them in the autocomplete
          if (data.results.length > 0) {
            const formattedResults = data.results.slice(0, 5).map(function(show) {
              return {
                label: show.title,
                value: show.title,
                poster: show.poster
              };
            });
            response(formattedResults);
          } else {
            // If no results are returned, displays an emptys result list
            response([]);
          }
        },
        error: function(error) {
          // Handles errors and display an empty result list
          console.error('Error:', error);
          response([]);
        }
      });
    },

    // The create function to customize the autocomplete result item rendering
    create: function() {
      $(this).data('ui-autocomplete')._renderItem = function(ul, item) {
        // Creates HTML for each result item with title and poster
        const showHtml = `
          <div class="show-result">
            <img src="${item.poster}" alt="${item.label} Poster">
            <h3>${item.label}</h3>
          </div>
        `;
        return $('<li>').append(showHtml).appendTo(ul);
      };
    },

    // Sets the minimum length required to trigger autocomplete suggestions
    minLength: 0
  });

  // Attachs a keydown event handler to the search input
  $('#search').keydown(function(event) {
    // If the 'Enter' key is pressed, it prevents the default form submission and submit the search form
    if (event.key === 'Enter') {
      event.preventDefault();
      $('#search-form').submit();
    }
  });
})();
