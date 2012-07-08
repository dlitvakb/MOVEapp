var j = new Juggernaut();

j.subscribe('persona:saved', function(d) {
    $("#name").text(d.model.name);
    $("#surname").text(d.model.surname);
});
