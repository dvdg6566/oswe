# JS Injection

Since Bassmaster is designed as a server-side plugin, we want to parse the code for any low-hanging fruit by searching for the `eval` function. The eval function takes in a string and **evaluates the source string a script body**. This means that both statements and expressions are allowed, and then returns the completion value of the code. As such, it is often susceptible to **injection attacks** if the input is user-controlled and not properly sanitized. 

```bash
grep -rnw "eval(" . --color
./lib/batch.js:152:                    eval('value = ref.' + parts[i].value + ';');
```

Here is the function. In the function, we notice that one of the specific parts array entries needs to fulfill the following conditions:

- The value of the `parts[i].type` attribute is `ref`
- The value of `resultsData.resultsMap[parts[i].index]` is evaluated as true
- The value of the`parts[i].value`attribute is inserted into the eval expression

If no error is found, Bassmaster will simply move on with the next request. After which, the following lines of code are run: `resultsData.results[pos] = result; resultsData.resultsMap[pos] = result;`, which updates the `resultsData` object based on the `data.result` attribute. 

```jsx
internals.batch = function (batchRequest, resultsData, pos, parts, callback) {

	var path = '';
	var error = null;

	for (var i = 0, il = parts.length; i < il; ++i) {
		path += '/';

		if (parts[i].type === 'ref') {
			var ref = resultsData.resultsMap[parts[i].index];

			if (ref) {
				var value = null;

				try {
					eval('value = ref.' + parts[i].value + ';');
				}
				catch (e) {
					error = new Error(e.message);
				}

				if (value) {
					if (value.match && value.match(/^[\w:]+$/)) {
						path += value;
					}
					else {
						error = new Error('Reference value includes illegal characters');
						break;
					}
				}
				else {
					error = error || new Error('Reference not found');
					break;
				}
			}
			else {
				error = new Error('Missing reference response');
				break;
			}
		}
		else {
			path += parts[i].value;
		}
	}

	if (error === null) {

		// Make request
		batchRequest.payload.requests[pos].path = path;
		internals.dispatch(batchRequest, batchRequest.payload.requests[pos], function (data) {

			// If redirection
			if (('' + data.statusCode).indexOf('3')  === 0) {
				batchRequest.payload.requests[pos].path = data.headers.location;
				internals.dispatch(batchRequest, batchRequest.payload.requests[pos], function (data) {
					var result = data.result;

					resultsData.results[pos] = result;
					resultsData.resultsMap[pos] = result;
					callback(null, result);
				});
				return;
			}

			var result = data.result;
			resultsData.results[pos] = result;
			resultsData.resultsMap[pos] = result;
			callback(null, result);
		});
	}
	else {
		resultsData.results[pos] = error;
		return callback(error);
	}
};
```

Tracing back our `internals.batch` function, we find that it is invoked in the `internals.process` function as follows. The `callBatch` function is used to perform a callback to the `internals.batch` ****function, which is invoked with a variable called `parts` that is populated from the `requests` array. 

```jsx
internals.process = function (request, requests, resultsData, reply) {

	var fnsParallel = [];
	var fnsSerial = [];
	var callBatch = function (pos, parts) {

		return function (callback) {
			//console.log("calling the batch function!");
			internals.batch(request, resultsData, pos, parts, callback);
		};
	};
	
	for (var i = 0, il = requests.length; i < il; ++i) {
		var parts = requests[i];

		if (internals.hasRefPart(parts)) {
			fnsSerial.push(callBatch(i, parts));
		}
		else {
			fnsParallel.push(callBatch(i, parts));
		}
	}
```

The `internals.process` function is invoked inside the main exports function.

 For each item in `request.payload.requests.length`, its `path` is processed with the regex expression [xx], and the matches are then put into the function `parseRequest`. This `parseRequest` function is the one responsible for setting the `type` to ref, and hence we need to ensure that it evaluates in such a way that does so. This implies that if we can contorl the URL paths passed to `lib/batch.js` for processing, we should be able to reach our eval function with user-controlled data. 

```jsx
module.exports.config = function (settings) {

	return {
		handler: function (request, reply) {

			var resultsData = {
				results: [],
				resultsMap: []
			};

			var requests = [];
			var requestRegex = /(?:\/)(?:\$(\d)+\.)?([^\/\$]*)/g;       // /project/$1.project/tasks, does not allow using array responses

			// Validate requests

			var errorMessage = null;
			var parseRequest = function ($0, $1, $2) {

				if ($1) {
					if ($1 < i) {
						parts.push({ type: 'ref', index: $1, value: $2 });
						return '';
					}
					else {
						errorMessage = 'Request reference is beyond array size: ' + i;
						return $0;
					}
				}
				else {
					parts.push({ type: 'text', value: $2 });
					return '';
				}
			};

			if (!request.payload.requests) {
				return reply(Boom.badRequest('Request missing requests array'));
			}

			for (var i = 0, il = request.payload.requests.length; i < il; ++i) {

				// Break into parts

				var parts = [];
				var result = request.payload.requests[i].path.replace(requestRegex, parseRequest);

				// Make sure entire string was processed (empty)

				if (result === '') {
					requests.push(parts);
				}
				else {
					errorMessage = errorMessage || 'Invalid request format in item: ' + i;
					break;
				}
			}

			if (errorMessage === null) {
				internals.process(request, requests, resultsData, reply);
			}
			else {
				reply(Boom.badRequest(errorMessage));
			}
		},
		description: settings.description,
		tags: settings.tags
	};
};
```

Let’s now look into where our `batch.js` exports function is called from, which is coming from the `index.js` file. Based on the contents, here the `/batch` endpoint is responsible for sending our requests to that eval statement. 

```jsx
var Batch = require('./batch');

// Declare internals

var internals = {
    defaults: {
        batchEndpoint: '/batch',
        description: 'A batch endpoint that makes it easy to combine multiple requests to other endpoints in a single call.',
        tags: ['bassmaster']
    }
};

exports.register = function (pack, options, next) {

    var settings = Hoek.applyToDefaults(internals.defaults, options);

    pack.route({
        method: 'POST',
        path: settings.batchEndpoint,
        config: Batch.config(settings)
    });

    next();
};

exports.register.attributes = {
    pkg: require('../package.json')
};

```