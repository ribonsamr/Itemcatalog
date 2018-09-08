function getItems(func) {
  $.ajax({
    type: 'GET',
    url: '/api/items',
    processData: false,
    data: true,
    dataType: 'json',
    success: function(result) {
      func(result);
    }
  });
}

var mainViewModel = {
  Home: { title: ko.observable('Home'), url: ko.observable('/') },
  Items: { title: ko.observable('Items') },
  API: { title: ko.observable('API') },
  Users: { title: ko.observable('Users') },
  Login: { title: ko.observable('Login') },
  Logout: { title: ko.observable('Logout') },
  loggedIn: ko.observable(false),
  content: ko.observableArray([])
};

$(function() {
  ko.applyBindings(mainViewModel);
  mainViewModel.loggedIn(current_user_authed);
});
