import java.util.Random;
import java.util.Base64;

// Invoke program as java generate_tokens.java <low> <high> <userId>

public class TokenUtil{
	public static final String CHARSET = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".toUpperCase() + "1234567890" + "!@#$%^&*()";

	public static void main(String args[]){
		int length = 40;
		long low = Long.parseLong(args[0]);
		long high = Long.parseLong(args[1]);
		int userId = Integer.parseInt(args[2]);
		String token = "";

		for (long l = low; l <= high; l++){
			token = createToken(userId, l);
			System.out.println(token);
		}
	}

	public static String createToken(int userId, long seed){
	    Random random = new Random(seed);
		StringBuilder sb = new StringBuilder();
		byte[] encbytes = new byte[42];

		for (int i=0;i<42;++i){
			sb.append(CHARSET.charAt(random.nextInt(CHARSET.length())));
		}

		byte[] bytes = sb.toString().getBytes();
		
		for (int i=0;i<bytes.length;i++){
			encbytes[i] = (byte)(bytes[i] ^ (byte)userId);
		}		

		return Base64.getUrlEncoder().withoutPadding().encodeToString(encbytes);
	}
}

// Openjdk version 1.8.0_252