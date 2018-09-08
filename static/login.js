function signOut() {
  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function () {
    console.log('User signed out.');
    
  });
}

function backendSignOut() {

}

function onSignIn(googleUser) {
  var id_token = googleUser.getAuthResponse().id_token;

  $('.g-signin2').attr('style', 'display: none');

  $.ajax({
    type: 'POST',
    url: '/gconnect',
    processData: false,
    data: id_token,
    contentType: 'application/octet-stream; charset=utf-8',
    success: function(result) {
      $('.signout').attr('style', 'display: relative');
      $('.login_form').attr('style', 'display: none');
      // console.log(result);
      // $(".result").html(JSON.stringify(result));
      // console.log(result);
      // window.location.replace(result)
    }
  });
}
