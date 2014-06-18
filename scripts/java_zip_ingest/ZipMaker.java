import java.util.List;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

// source: http://www.avajava.com/tutorials/lessons/how-can-i-create-a-zip-file-from-a-set-of-files.html
//
public class ZipMaker{


    public static void main(String[] args){
        
    }
    public ZipMaker(){
        
    }
    public ZipMaker(List<String> filenames, String inputDirname, String outputZipFilename){

        try {
			FileOutputStream fos = new FileOutputStream(outputZipFilename);
			ZipOutputStream zos = new ZipOutputStream(fos);

            for(String fname: filenames){
            
                String fullpath = new String(inputDirname + '/' + fname);
                addToZipFile(fname, fullpath, zos);
    			
            }


		//	String file5Name = "f1/f2/f3/file5.txt";
		//	addToZipFile(file5Name, zos);

			zos.close();
			fos.close();

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
        
    }


	public static void addToZipFile(String fileName, String fullFilepath, ZipOutputStream zos) throws FileNotFoundException, IOException {

		System.out.println("Writing '" + fileName + "' to zip file");

		File file = new File(fullFilepath);
		FileInputStream fis = new FileInputStream(file);
		ZipEntry zipEntry = new ZipEntry(fileName);
		zos.putNextEntry(zipEntry);

		byte[] bytes = new byte[1024];
		int length;
		while ((length = fis.read(bytes)) >= 0) {
			zos.write(bytes, 0, length);
		}

		zos.closeEntry();
		fis.close();
	}

}
