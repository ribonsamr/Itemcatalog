function mainViewModel() {
  this.loggedIn = ko.observable(false);
  this.content = ko.observableArray([]);
  this.navItems = [
  { title: ko.observable('Login'),
  url: ko.observable('/login'),
  visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)},

  { title: ko.observable('Signup'),
  url: ko.observable('/signup'),
  visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)}];

  this.usersNav = {title: ko.observable('Users'),
  url: ko.observable('/users'),
  visib: ko.pureComputed(function() {
    return this.loggedIn();
  }, this)};

  this.logoutButton = {
    title: ko.observable('Logout'),
    visib: ko.pureComputed(function() { return this.loggedIn(); }, this),
  }

  this.getUsers = function(func) {
    $.ajax({
      type: 'GET',
      url: '/api/users',
      dataType: 'json',
      success: function(result) {
        console.log((result));
        flash.print("check your console.");
      }
    });
  };

  this.getItems = function(func) {
    $.ajax({
      type: 'GET',
      url: '/api/items',
      dataType: 'json',
      success: function(result) {
        func(result);
      }
    });
  };

}

function formModel() {
  this.username = ko.observable("");
  this.email = ko.observable("");
  this.password = ko.observable("");
}


function auth() {
  this.login = function() {
    $.ajax({
      type: 'POST',
      url: '/login',
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(xhr, msg) {
        mainViewModel.loggedIn(true);
        window.location.href = '/';
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          location.reload();
        }
        if (xhr.status === 302) {
          window.location.href = xhr.responseText;
        }
        if (xhr.status === 405) {
          alert(xhr.responseText)
        }
      }
    });
  }

  this.submitData = function() {
    $.ajax({
      type: 'POST',
      url: '/signup',
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(xhr, msg) {
        mainViewModel.loggedIn(true);
        window.location.href = '/';
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          location.reload();
        }
        if (xhr.status === 302) {
          window.location.href = xhr.responseText;
        }
        if (xhr.status === 405) {
          alert(xhr.responseText)
        }
      }
    });
  }

  this.logout = function() {
    $.ajax({
      type: 'POST',
      url: '/logout',
      processData: false,
      contentType: 'application/json',
      success: function(xhr, msg) {
        var auth2 = gapi.auth2.getAuthInstance();
        auth2.signOut().then(function () {
          console.log('User signed out.');
        });
        mainViewModel.loggedIn(false);
        window.location.href = '/';
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          location.reload();
        }
        if (xhr.status === 302) {
          window.location.href = xhr.responseText;
        }
        if (xhr.status === 405) {
          alert(xhr.responseText)
        }
      }
    });
  }
}

function flash() {
  var self = this;
  this.msg = ko.observable();
  this.print = function(text) {
    self.msg(text);
  };
}


var masterViewModel = (function() {
  this.mainViewModel = new mainViewModel();
  this.formViewModel = new formModel();
  this.auth = new auth();
  this.flash = new flash();
})();


$(function() {
  ko.applyBindings(masterViewModel);
  mainViewModel.loggedIn(current_user_authed);
});
