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

  this.refreshContent = function() {
    let result = this.getItems(function(result) {
      mainViewModel.content([]);
      for (var i = 0; i < result.length; i++) {
        mainViewModel.content.push(result[i])
      }
      // console.log(mainViewModel.content());
    });
  };

  this.edit = function(item) {
    $.ajax({
      type: 'POST',
      url: '/edit',
      data: JSON.stringify(item),
      contentType: 'application/json',
      success: function(xhr, msg) {
        mainViewModel.refreshContent();
        flash.print("Edit done.\n" + item.name + ", of catagory: " + item.catagory + '.');
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          console.log(xhr.responseText);
          console.log(msg);
          console.log(error);
          // location.reload();
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

  this.remove = function(item) {
    $.ajax({
      type: 'POST',
      url: '/delete',
      data: JSON.stringify(item),
      contentType: 'application/json',
      success: function(xhr, msg) {
        mainViewModel.refreshContent();
        flash.print("Removed item: " + item.name + ", of catagory: " + item.catagory + '.');
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          console.log(xhr.responseText);
          console.log(msg);
          console.log(error);
          // location.reload();
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

function addModel() {
  var self = this;
  this.itemName = ko.observable();
  this.itemCatagory = ko.observable();
  this.itemFile = ko.observable();

  this.active = ko.observable(false);

  this.submit = function (formData) {
    file = formData.elements.item_file;
    name = self.itemName();
    catagory = self.itemCatagory();

    data = new FormData();
    if (file.files[0]) {
      data.append('file', file.files[0]);
    }
    data.append('name', name);
    data.append('catagory', catagory);

    $.ajax({
      type: "POST",
      url: '/add',
      data: data,
      contentType: false,
      processData: false,
      cache: false,
      success: function(data) {
        mainViewModel.refreshContent();
        self.itemName('');
        self.itemCatagory('');
        self.itemFile('');
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          console.log(xhr.responseText);
          console.log(msg);
          console.log(error);
          // location.reload();
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
  this.auth = new auth();
  this.flash = new flash();
  this.addModel = new addModel();
})();


$(function() {
  ko.applyBindings(masterViewModel);
  mainViewModel.loggedIn(current_user_authed);
});
