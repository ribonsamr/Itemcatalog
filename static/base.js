// Main view model
function mainViewModel() {
  this.loggedIn = ko.observable(false);
  this.content = ko.observableArray([]);
  this.searchInput = ko.observable('');
  this.searchResults = ko.observableArray([]);

  // Navigation items that will change due to the login state
  this.navItems = [
  { title: ko.observable('Login'),
    url: ko.observable('/login'),
    visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)},

  { title: ko.observable('Signup'),
    url: ko.observable('/signup'),
    visib: ko.pureComputed(function() { return !this.loggedIn(); }, this)}];

  this.usersNav = {
    title: ko.observable('Users'),
    url: ko.observable('/users'),
    visib: ko.pureComputed(function() {
      return this.loggedIn();
    }, this)};

  this.logoutButton = {
    title: ko.observable('Logout'),
    visib: ko.pureComputed(function() { return this.loggedIn(); }, this),
  }

  // POST a request to get all the users data in the db, and log the results.
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

  // Get all the items from the db, and execute a function with the result.
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

  // Refresh the items content (mainViewModel.content) which is displayed
  // across the main and the items pages.
  this.refreshContent = function() {
    let result = this.getItems(function(result) {
      mainViewModel.content([]);
      for (var i = 0; i < result.length; i++) {
        data = result[i];
        filename = data.image_filename;

        // Check if the item has an image, and load it.
        if (!filename) {
          mainViewModel.content.push(data);
        } else {
          // console.log(data);
          $.ajax({
            type: 'POST',
            url: '/image',
            data: {filename: filename},
            success: function(result) {
              data.image_filename = result;

              // update the content list
              mainViewModel.content.push(data);
              // console.log(data);
            }
          });
        }
      }
    });
  };

  // POST a request to edit a record
  this.edit = function(item) {
    $.ajax({
      type: 'POST',
      url: '/edit',
      data: JSON.stringify(item),
      contentType: 'application/json',
      success: function(xhr, msg) {

        // Refresh the content
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
          flash.print(xhr.responseText)
        }
      }
    });
  }

  // POST a request to delete an item
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
          flash.print(xhr.responseText)
        }
      }
    });
  }

  // Search an item with a keyword.
  this.searchItem = function() {
    $.ajax({
      type: 'GET',
      url: '/search/' + mainViewModel.searchInput(),
      success: function(result) {

        // inform the user with the number of matches found
        flash.print('Found ' + result.length + '.');

        // empty the searchResults object
        mainViewModel.searchResults([]);

        for (var i = 0; i < result.length; i++) {
          data = result[i];

          // Check if the item has an image linked to it, and load it.
          filename = data.image_filename;
          if (!filename) {
            mainViewModel.searchResults.push(data);
          } else {
            console.log(data);
            $.ajax({
              type: 'POST',
              url: '/image',
              data: {filename: filename},
              success: function(result) {
                data.image_filename = result;
                mainViewModel.searchResults.push(data);
                console.log(data);
              }
            });
          }
        }
      },
      error: function(xhr, msg, error) {
        if (xhr.status === 400) {
          location.reload();
        }
        if (xhr.status === 302) {
          window.location.href = xhr.responseText;
        }
        if (xhr.status === 405) {
          flash.print(xhr.responseText);
        }
        if (xhr.status === 404) {
          // If there are no results, the server returns 404.
          flash.print("No results.");
        }
      }
    });
  }
}

// Login form model
function formModel() {
  this.username = ko.observable("");
  this.email = ko.observable("");
  this.password = ko.observable("");
}

// Auth model
function auth() {
  // POST a request with JSON data to login a user
  this.login = function() {
    $.ajax({
      type: 'POST',
      url: '/login',
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(xhr, msg) {
        // If the response is OK, log him in.
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
          flash.print(xhr.responseText)
        }
      }
    });
  }

  // A POST request to sign up a user
  this.submitData = function() {
    $.ajax({
      type: 'POST',
      url: '/signup',
      data: JSON.stringify(ko.toJSON(formViewModel, null, 2)),
      contentType: 'application/json',
      success: function(xhr, msg) {
        // If the respone is OK, log him in.
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
          flash.print(xhr.responseText)
        }
      }
    });
  }

  // A POST request to logout a user.
  this.logout = function() {
    $.ajax({
      type: 'POST',
      url: '/logout',
      processData: false,
      contentType: 'application/json',
      success: function(xhr, msg) {

        // Get the google auth2 instance, and sign the user out.
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
          flash.print(xhr.responseText)
        }
      }
    });
  }
}

// flash model to show temp messages to the user when he executes some tasks.
function flash() {
  var self = this;
  this.msg = ko.observable();
  this.print = function(text) {
    self.msg(text);
  };
}

// A model to add new items
function addModel() {
  var self = this;
  this.itemName = ko.observable();
  this.itemCatagory = ko.observable();
  this.itemFile = ko.observable();

  this.active = ko.observable(false);

  this.submit = function(formData) {
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
        flash.print('Added item: ' + name + ', of catagory: ' + catagory + '.');
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
          flash.print(xhr.responseText)
        }
      }
    });
  }
}

// Combine all the views together
var masterViewModel = (function() {
  this.mainViewModel = new mainViewModel();
  this.formViewModel = new formModel();
  this.auth = new auth();
  this.flash = new flash();
  this.addModel = new addModel();
})();


$(function() {
  ko.applyBindings(masterViewModel);
  
  // Get the current_user login state via main.py:line 86.
  mainViewModel.loggedIn(current_user_authed);
});
