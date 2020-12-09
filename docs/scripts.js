function load_dataframe_into(resource, id) {
    fetch(resource, {
        cache: "no-store",
        mode: 'no-cors',
    })
      .then(response => { return response.text() })
      .then(data => {
        node = document.querySelector("#"+id)
        node.innerHTML = data;
        node.querySelectorAll('.dataframe thead').forEach(e => e.classList.add('thead-dark'));
      });
}
