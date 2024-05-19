# Serialization

Serialization is the process of converting the state of an object into a form that can be persisted or transported (a bit like jsonifying our current state to store as hard disk files). As long as format of saved file is understood by consumer, object can be **recreated** in process space as desired. 

## Limitations

- The XML Serializer class is able to serialize **public properties and fields** of an object.
- When we perform an XML serialization, it will save the object into a text file in XML format. We can then perform deserialization to recover our object from the XML text file.
- It supports a narrow set of objects as it cannot serialize abstract classes. (An abstract class cannot be initialized by itself, needs to be subclassed by another class to use properties)
- The **type** of object must be known to the XmlSerializer instance at runtime.
    - Developers could build custom **flexible** deserializing wrapper (for instance, taking on additional arguments that specify the object class and perform serialization functionality accordingly)
    - We can use `GetType` function on object to dynamically specify object class
- It is possible to change the contents of a serialized object file (can change the object to an instance of an object from a different class)

## Usage of XmlSerializer

```java
// Serialization
var ser = new XmlSerializer(typeof(<variable>));
TextWriter writer = new StreamWriter("C:\\Users\\Public\\basicXML.txt");
ser.Serialize(writer, txt);
writer.Close();

// Deserialization
var fileStream = new FileStream(args[0], FileMode.Open, FileAccess.Read);
var streamReader = new StreamReader(fileStream);
XmlSerializer serializer = new XmlSerializer(typeof(<variable>));
serializer.Deserialize(streamReader);
```

## Attacking

To attack, we can modify the contents of a serialized XML file to modify object properties, leading to unexpected results. 

- For instance, we may be able to change the process spawned if the deserializer application implements a function that starts a process

To generate the XML payload, we can modify the original code to generate a similar XML file but with malicious behavior.