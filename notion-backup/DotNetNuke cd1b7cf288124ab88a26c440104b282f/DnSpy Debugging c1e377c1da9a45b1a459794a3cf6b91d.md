# DnSpy Debugging

DnSpy debugging allows us to see exactly how our payloads are being processed.

### Enabling debugging

- In .NET web applications, optimizations are applied to executables at runtimes, which makes our debugger unable to bind breakpoints to specific lines of code. We can thus modify the **assembly attributes** of the executable and recompile it with dnSpy.
- Right click module name (Module in this case being DotNetNuke) —> Edit Assembly Attributes —> Debuggable Attribute

```java
// Change Debuggable attribute to the following: 
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.Default | DebuggableAttribute.DebuggingModes.DisableOptimizations | DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints | DebuggableAttribute.DebuggingModes.EnableEditAndContinue)]
```

- After replacing attribute, click compile and save edited assembly with `File --> Save Module`.
- Once IIS worker process starts, it makes copies of required DNN modules and loads from temporary directory. To load the edited module, we restart the service with `iisreset /noforce`

### Using dnSpy

The `w3wp.exe` is the IIS worker under which our DotNetNuke application is running. 

We’ll then go to `File -> Close All` to ensure that we’re using the correct version of the executables. 

To debug DNN, we attach our debugger `Debug --> Attach`  to the `w3wp.exe` process (which is the IIS worker process running DNN). 

- If cannot see `w3wp.exe`, browse to DNN instance in browser

Pause execution using appropriate `Debug` menu option. Then access `Debug > Windows > Modules` to list the modules loaded by process. 

Right clicking on any of the listed modules (in our case `System.Web.dll`), can access `Open All Modules` context menu, which loads all available modules in `Assembly Explorer` page. Once loaded, we can click to `continue` the application in the top bar. Right click the module listings and `Sort Assemblies`, then click on the one for our vulnerable DNN dll. 

We can then set a breakpoint, in this case on line 24 of the `PersonalizationController` namespace. 

We can then execute our PoC request, using Burp suite to send a request to a non-existent webpage. When doing so, we can set our `DNNPersonalization` cookie to some test value. 

## Tracing Stack

Call stack will give us the list of functions called on the way to the breakpoint. Select `Call Stack` in the bottom window to view

Backing up a couple steps from the top, we see the `UserMode` property of the `PortalSettings` class is invoked. 

Upon setting a breakpoint on line 926, which is executed within the if statement `if (HttpContext.Current != null && HTTPContext.Current.Request.IsAuthenticated)`. This suggests that the HTTPContext is being interpreted as authenticated (which seems incorrect). 

Near the bottom of the callstack, we find that the reason for this is the function named `AdvancedUrlRewriterer.Handle404OrException`. If there is no user in the context, it is set to be thecurrent thread user. 

```java
if (context.User == null){
	context.User = Thread.CurrentPrincipal;
}
```

We set another breakpoint on these lines (line 809 and 813) and find that the user attribute is indeed set to `null`initially, but is re-written to be a `WindowsPricinpal`after that segment. 

The 404 handler being invoked before `HttpContext.User` object is set, leading to the HTTPContext being interpreted as authenticated.