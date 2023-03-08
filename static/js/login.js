'use strict';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries


window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function () {
    firebase.auth().signOut();
  };

  // FirebaseUI config.
  const scoutid_provider = new firebase.auth.SAMLAuthProvider('saml.scoutid');
  var uiConfig = {
    signInSuccessUrl: '/sign_in_success/',
    signInOptions: [
      'saml.scoutid'
    ],
    // Terms of service url.
    tosUrl: '<your-tos-url>'
  };

  function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
       var c = ca[i];
       while (c.charAt(0)==' ') c = c.substring(1);
       if(c.indexOf(name) == 0)
          return c.substring(name.length,c.length);
    }
    return "";
  }

  function onsuccess() {
    console.log("Successfully sent login to server");
  }

  function onfailure() {
    console.log("Failed to send login to server");
    alert("Failed to send login to server");
  }

  function postIdTokenToSessionLogin(idToken) {
    var XHR = new XMLHttpRequest();
    var formdata = 'idToken=' + idToken;

    XHR.addEventListener('load', function(event) 
    {
      if (onsuccess) onsuccess();
    });

    XHR.addEventListener('error', function(event) 
    {
      if (onfailure) onfailure();
    });

    XHR.open('POST', '/session_login/', true);
    XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    XHR.onload = function () {
      console.log(this.responseText);
      var after_login_url = getCookie('after_login_url');
      if (after_login_url && after_login_url.length() > 0) {
        document.cookie = "after_login_url= ; expires = Thu, 01 Jan 1970 00:00:00 GMT";
        console.log('after_login_url=' + after_login_url);
        window.location.href = after_login_url;
      }
    };
    XHR.send(formdata);
  }

  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      // User is signed in, so display the "sign out" button and login info.
      document.getElementById('sign-out').hidden = false;
      document.getElementById('login-info').hidden = false;
      console.log(`Signed in as (${user.uid})`);
      user.getIdToken().then(function (idToken) {
        // Add the token to the browser's cookies. The server will then be
        // able to verify the token against the API.
        // SECURITY NOTE: As cookies can easily be modified, only put the
        // token (which is verified server-side) in a cookie; do not add other
        // user information.
        console.log("setting the document.cookie: token=" + idToken);
        document.cookie = "token=" + idToken
        return postIdTokenToSessionLogin(idToken);
      });
    } else {
      // User is signed out.
      // Initialize the FirebaseUI Widget using Firebase.
      var ui = new firebaseui.auth.AuthUI(firebase.auth());
      // Show the Firebase login button.
      ui.start('#firebaseui-auth-container', uiConfig);
      // Update the login state indicators.
      document.getElementById('sign-out').hidden = true;
      document.getElementById('login-info').hidden = true;
      // Clear the token cookie.
      console.log("clearing the document.cookie");
      document.cookie = "token= ; expires = Thu, 01 Jan 1970 00:00:00 GMT";
    }
  }, function (error) {
    console.log(error);
    alert('Unable to log in: ' + error)
  });
});
