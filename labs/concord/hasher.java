import java.util.Base64;
import java.security.NoSuchAlgorithmException;

import java.security.MessageDigest;

public class hasher{
  public static String hash(String s) {
      MessageDigest md;
      try {
          md = MessageDigest.getInstance("SHA-256");
      } catch (NoSuchAlgorithmException e) {
          throw new RuntimeException(e);
      }

      byte[] ab = Base64.getDecoder().decode(s);
      System.out.println(ab);
      ab = md.digest(ab);
      System.out.println(ab);

      return Base64.getEncoder().withoutPadding().encodeToString(ab);
  }

  public static void getBoth(byte[] s){
    // Generates both sides to use and to insert into db)
    MessageDigest md;
    try {
        md = MessageDigest.getInstance("SHA-256");
    } catch (NoSuchAlgorithmException e) {
        throw new RuntimeException(e);
    }

    String enc = Base64.getEncoder().encodeToString(s);
    System.out.println(enc);
  }

  public static void main(String args[]){
    String token = hash("abcdefghabcdefgh");
    System.out.println(token);

    // byte[] ab = "[B@35fc6dc4".getBytes();
    // System.out.println(ab);
    // getBoth(ab);
  }
}