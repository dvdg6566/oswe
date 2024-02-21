import java.io.*;  
import javax.servlet.*;  
import javax.servlet.http.*;  
public class httpserv extends HttpServlet  
{  
   public void doGet(HttpServletRequest req ,HttpServletResponse res)throws IOException ,ServletException  
   {  
      PrintWriter out = res.getWriter();  
      res.setContentType("text/html");  
      out.println("<html><body>");  
      out.println("<h1> First servlet</h1>");  
      out.println("</body></html>");  
   }  
}  