# Application Discovery

Discovery phase is critical to build a proper sitemap to obtain a view of exposed endpoints and application libraries. 

1. Opening [`http://openitcockpit`](http://openitcockpit) in Firefox while proxying in Burp will create a basic sitemap by capturing all requests and resources that are loaded. We can access this through `target-->sitemap`. 
    1. The application runs on HTTPS
    2. Without a valid session, application root was directed to `/login/login`
    3. Application-specific Javascript found in `js` directory
    4. Vendor dependencies are found in `lib` and `vendor` directories. 
    5. Application uses Bootstrap, JQuery, particles and Font Awesome
2. The 404 page (just opening a random page in browser) expands the sitemap significantly
    1. Specifically, the `/js/vendor/UUID.js-4.0.3/` directory contains a `dist` subdirectory. 
    2. When a JS library is successfully built, the output files are typically written to a `dist` or `public` subdirectory. During the build process, unnecessary files are removed, and the resulting library is distributed and imported into an application. 
    3. The existence of a `dist` directory suggests the developer included the entire directory instead of just the `.js` library file, and unnecessary files could expand our attack surface. We reference their documentation [uuidjs - npm (npmjs.com)](https://www.npmjs.com/package/uuidjs/v/4.0.3) for more details. Following to the github, we find the contents of the `dist` directory: [UUID.js/dist at master · LiosK/UUID.js (github.com)](https://github.com/LiosK/UUID.js/tree/master/dist)
    4. We can check for the [`README.md`](http://README.md) file, showing we can access any files from the repo. 
3. Server-side executables like PHP are rarely included in vendor libraries, however, they may contain HTML files that could introduce **reflected cross-site scripting (XSS)** vulnerabilities. 
    1. These files are likely less scrutinized than other deliberately exposed files and endpoints. 

## Library Discovery

We already have found the following libraries:

```bash
UUID.js-4.0.3
fineuploader
gauge
gridstack
lodash
```

We can use a specific library wordlist to fuzz the`/js/vendor` path. 

- The nice-registry repo contains a [list of all NPM packages](https://raw.githubusercontent.com/nice-registry/all-the-package-names/master/names.json) ordered by popularity.
- Alternatively, [npm rank (github.com)](https://gist.github.com/anvaka/8e8fa57c7ee1350e3491)

```bash
cat names.json| grep "," | grep -v '@' | cut -d '"' -f 2 > list.json
(grep -v to remove any libraries that start with @ since they aren't going to be in a filepath)
gobuster dir -w list.json -u https://openitcockpit/js/vendor/ -k
```

Among the package names sprayed, we find the following:

```bash
autocomplete
lodash
gauge
bootstrap-daterangepicker
image-picker
```

Once we’ve gotten the list of libraries, we compile them into a nice `packages.txt` list and search them up against the `quickhits.txt` wordlist in the web-content directory of SecLists. From this, we can check their readme’s for their version number and get them as follows:

```bash
while read l; do echo "===$l==="; gobuster dir -w ~/SecLists/Discovery/Web-Content/quickhits.txt -k -q -u $l; done < packages.txt

UUID.js v4.0.3
Lodash v3.9.3
Gridstack v0.2.3
```

![Untitled](Application%20Discovery%20d16be10559d14582abe953b8684973fa/Untitled.png)

We can now download these packages and search for any HTML files. To download the pavakges, we can go to `/archive` and look for the source zip by their version number (either `archive/v(xx).zip` or `archive/(xx).zip`.

```bash
find . -iname *.html 
(iname means case insensitivity)

./gridstack.js-0.2.3/demo/two.html
./gridstack.js-0.2.3/demo/serialization.html
./gridstack.js-0.2.3/demo/knockout2.html
./gridstack.js-0.2.3/demo/float.html
./gridstack.js-0.2.3/demo/nested.html
./gridstack.js-0.2.3/demo/knockout.html
./lodash-3.9.3/test/backbone.html
./lodash-3.9.3/test/underscore.html
./lodash-3.9.3/test/index.html
./lodash-3.9.3/perf/index.html
./lodash-3.9.3/vendor/firebug-lite/skin/xp/firebug.html
./UUID.js-4.0.3/docs/uuid.js.html
./UUID.js-4.0.3/docs/UUID.html
./UUID.js-4.0.3/docs/index.html
./UUID.js-4.0.3/test/browser-core.html
./UUID.js-4.0.3/test/browser.html                                 
```