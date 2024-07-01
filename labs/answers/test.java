import java.util.Random;
import java.util.Base64;

public class test{
	public static void main(String args[]){
		long x = Long.parseLong("1742427166705");
		int length = 40;
		int userId = 5;
		String token = createToken(userId, x);
		System.out.println(token);
	}

	public static String createToken(int userId, long seed){
		String CHARSET = "abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".toUpperCase() + "1234567890" + "!@#$%^&*()";
	    Random random = new Random(seed);
		StringBuilder sb = new StringBuilder();
		byte[] encbytes = new byte[42];

		System.out.println(seed);

		for (int i=0;i<42;++i){
			sb.append(CHARSET.charAt(random.nextInt(CHARSET.length())));
		}

		System.out.println(sb);

		byte[] bytes = sb.toString().getBytes();
		
		for (int i=0;i<bytes.length;i++){
			encbytes[i] = (byte)(bytes[i] ^ (byte)userId);
		}		

		return Base64.getUrlEncoder().withoutPadding().encodeToString(encbytes);
	}
}
