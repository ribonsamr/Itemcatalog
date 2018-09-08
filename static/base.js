function mainViewModel() {
  this.loggedIn = ko.observable(false);
  this.content = ko.observableArray([]);
  this.navItems = [
    { title: ko.observable('Home'),
      url: ko.observable('/'),
      visib: true
    },

    { title: ko.observable('Items'),
      url: ko.observable('/items'),
      visib: true
    },

    { title: ko.observable('API'),
      url: ko.observable('/api'),
      visib: true
    },

    { title: ko.observable('Users'),
      url: ko.observable('/users'),
      visib: ko.pureComputed(function() { return this.loggedIn(); }, this)
    },

    { title: ko.observable('Login'),
      url: ko.observable('/login'),
      visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)
    },

    { title: ko.observable('Signup'),
      url: ko.observable('/signup'),
      visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)
    }];

  this.logoutButton = {
    title: ko.observable('Logout'),
    visib: ko.pureComputed(function() { return this.loggedIn(); }, this),
    logOut: function() {
      $.ajax({
        type: 'POST',
        url: '/logout',
        processData: false,
        contentType: 'application/json',
        success: function(xhr, msg) {
          if (gapi.auth2) {
            if (gapi.auth2.getAuthInstance().isSignedIn.get()) {
              var auth2 = gapi.auth2.getAuthInstance();
              auth2.signOut().then(function () {
                console.log('User signed out.');
              });
            }
          }
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

  this.getItems = function(func) {
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
  };

}

function formModel() {
  this.username = ko.observable("");
  this.email = ko.observable("");
  this.password = ko.observable("");
  this.submitData = function() {
    $.ajax({
      type: 'POST',
      url: '/signup',
      processData: false,
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(xhr, msg) {
        mainViewModel.loggedIn(true);
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
  };

  this.logIn = function() {
    $.ajax({
      type: 'POST',
      url: '/login',
      processData: false,
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
}

var masterViewModel = (function() {
  this.mainViewModel = new mainViewModel();
  this.formViewModel = new formModel();
})();

$(function() {
  ko.applyBindings(masterViewModel);
  mainViewModel.loggedIn(current_user_authed);
});
