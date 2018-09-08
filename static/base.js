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

function mainViewModel() {
  this.loggedIn = ko.observable(false);
  this.content = ko.observableArray([]);
  this.navItems = [
    { title: ko.observable('Home'), url: ko.observable('/'), visib: true },
    { title: ko.observable('Items'), visib: true },
    { title: ko.observable('API') , visib: true},
    { title: ko.observable('Users'), visib: ko.pureComputed(function() {
        return this.loggedIn();
    }, this) },
    { title: ko.observable('Login'), visib: ko.pureComputed(function() {
        return !this.loggedIn();
    }, this) },
    { title: ko.observable('Logout'), visib: ko.pureComputed(function() {
        return this.loggedIn();
    }, this) },
  ];
}

function formModel() {
  this.userName = ko.observable("");
  this.userEmail = ko.observable("");
  this.userPassword = ko.observable("");
  this.submitData = function() {
    $.ajax({
      type: 'POST',
      url: '/signup',
      processData: false,
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(result) {
        alert(result);
        // do some stuff here
      }
    });
  };
}

var masterViewModel = (function() {
  this.mainViewModel = new mainViewModel();
  this.formViewModel = new formModel();
})();

$(function() {
  ko.applyBindings(masterViewModel);
  mainViewModel.loggedIn(current_user_authed);
});
