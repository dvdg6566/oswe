import java.util.Random;

// Invoke program as java generate_tokens.java <low> <high>

public class OpenCRXToken{
	public static void main(String args[]){
		int length = 40;
		long low = Long.parseLong(args[0]);
		long high = Long.parseLong(args[1]);
		String token = "";

		for (long l = low; l < high; l++){
			token = getRandomBase62(length, l);
			System.out.println(token);
		}
	}

	public static String getRandomBase62(int length, long seed){
		String alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
	    Random random = new Random(seed);
	    String s = "";
	    for (int i = 0; i < length; i++)
	      s = s + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".charAt(random.nextInt(62)); 
	    return s;
	}
}