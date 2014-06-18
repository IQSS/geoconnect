import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Date;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;
import java.util.zip.ZipException;
import java.util.HashMap;
import java.util.*;

import java.nio.file.Files;
import static java.nio.file.StandardCopyOption.REPLACE_EXISTING;
import java.nio.file.Path;

public class ZipFileMetadataExtractor{

    // Reference for these extensions: http://en.wikipedia.org/wiki/Shapefile
    //
    public final static List<String> SHAPEFILE_MANDATORY_EXTENSIONS = Arrays.asList("shp", "shx", "dbf", "prj");
    public final static String SHP_XML_EXTENSION = "shp.xml";
    public final static List<String> SHAPEFILE_ALL_EXTENSIONS = Arrays.asList("shp", "shx", "dbf", "prj", "sbn", "sbx", "fbn", "fbx", "ain", "aih", "ixs", "mxs", "atx", ".cpg", SHP_XML_EXTENSION);  //  Note, this treats the ".shp.xml" as a separate file

    public String zipFilename = new String();
    public boolean zipFileProcessed = false;
    public String errorMessage = new String();
    
    private List<String> filesListInDir = new ArrayList<String>();

    /* Hash of file names and byte sizes {  "file name" : bytes }
       e.g. { "water.shp" : 541234 }
    */
    private HashMap<String, Long> filesizeHash = new HashMap<String, Long>();   
    
    /* Make a hash with basename and a list of extensions. Ignore files without extensions.
        
       e.g.  { "Tracts" : [ ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shx"] 
               , "my_word_doc" : [".docx"]
              }
    */
    //private HashMap<String, List> fileGroups = new HashMap<String, Arraylist>(); 
    private Map<String, List<String>> fileGroups = new HashMap<String, List<String>>();
    
    private String outputFolder = "unzipped";
    private String rezippedFolder = "rezipped";

    public void msg(String s){
        System.out.println(s);
    }
    public void msgt(String s){
        msg("-------------------------------");
        msg(s);
        msg("-------------------------------");
    }

    /*
        Constructor
    */
    public ZipFileMetadataExtractor(String filename){
        zipFilename = filename;
        processZipfile();
    }
    
    public static void main(String[] args){

           if (args.length == 0){
               System.out.println( "No file name, so add one!");
               // Water_single_shp.zip
             //  ZipFileMetadataExtractor zpt = new ZipFileMetadataExtractor("unzipped.zip");    
               ZipFileMetadataExtractor zpt = new ZipFileMetadataExtractor("../test_data/Waterbody_shp.zip");    
              // ZipFileMetadataExtractor zpt = new ZipFileMetadataExtractor("social_disorder_in_boston.zip");
              // zpt.processZipfile("notazip.zip");                           
               if (!zpt.zipFileProcessed){
                   System.out.println("--------- FAIL -------------");
                   System.out.println(zpt.errorMessage);
               }
               if (zpt.containsShapefile()){
                   System.out.println("--------- SHAPE FOUND! -------------");
                   System.out.println("Shape count: " + zpt.getShapefileCount());
               }

           }else if(args.length > 1){
               System.out.println( "Please only give one file name!");  
           }else{   
               String zip_name =  args[0];      
               System.out.println( "Process File: " + zip_name);

               System.out.println( "Process File: " + zip_name);                
               ZipFileMetadataExtractor zpt = new ZipFileMetadataExtractor(zip_name);
               if (!zpt.zipFileProcessed){
                   System.out.println("--------- FAIL -------------");
                   
                   System.out.println(zpt.errorMessage);
               }
               if (zpt.containsShapefile()){
                   System.out.println("--------- SHAPE FOUND! -------------");
                   System.out.println("Shape count: " + zpt.getShapefileCount());
                   
               }
               
           }
       } // end main
 
    /*
        Create a directory, if one doesn"t exist
    */
    private boolean createDirectory(String fname){
        if (fname == null){
            return false;
        }
      	File folder_obj = new File(fname);
      	return createDirectory(folder_obj);
      	
    } // createDirectory
    
    private boolean createDirectory(File folder){
        if (folder == null){
            return false;
        }
        try{
          	if(!folder.exists()){
          	    msg("Creating folder: " + folder.getName());
          		folder.mkdirs();	    
          	}else{
          	    msg("Folder exists: " + folder.getName());
          	}
         }catch(SecurityException ex){
           ex.printStackTrace(); 
           return false;
        }catch(NullPointerException ex){
            ex.printStackTrace(); 
            return false;
        }
        return true;
    } // createDirectory    

    
    /*
        Print out the key/value pairs of the Hash of filenames and sizes
    */
    private void showFileNamesSizes(){
        msgt("Hash: file names + sizes");
        Iterator<String> keySetIterator = filesizeHash.keySet().iterator();

        while(keySetIterator.hasNext()){
          String key = keySetIterator.next();
          msg("key: [" + key + "] value: [" + filesizeHash.get(key)+"]");
          
        }
    } // end showFileNamesSizes
    

    /*
        Iterate through Hash of file base names and extensions
    */
    private void showFileGroups(){

        msgt("Hash: file base names + extensions");
        
        Iterator<String> fileGroupsIterator = fileGroups.keySet().iterator();
        while(fileGroupsIterator.hasNext()){
            String key = fileGroupsIterator.next();
            msg("\n" + key);
            List<String> ext_list = fileGroups.get(key);
            msg(Arrays.toString(ext_list.toArray()));
            if (doesListContainShapefileExtensions(ext_list)){
                msg(" >>>> GOT IT! <<<<<<<<");
            }
            
          // if (SHAPEFILE_MANDATORY_EXTENSIONS.contains("shp")){
            //       msg("YES!!!");
           //}
        } // end while
    } // end showFileGroups
    
    
    
    
    /*    
        Process the .zip file!  
    */
    public void processZipfile(){
        
        // Examine the file
        unzipFile(zipFilename);
        
        if (!zipFileProcessed){
            return;
        }
        msgt("What have we got!");
        for (String element : filesListInDir) {
            msg(element);
        }
        
        rezipShapefileSets();
        
        //showFileNamesSizes();
        //showFileGroups();
        
    }
    
    /*
        Return a count of shapefile sets in this .zip
    */
    public int getShapefileCount(){
        int shp_cnt = 0;
        
        Iterator<String> fileGroupsIterator = fileGroups.keySet().iterator();
        while(fileGroupsIterator.hasNext()){
            String key = fileGroupsIterator.next();
            List<String> ext_list = fileGroups.get(key);
            if (doesListContainShapefileExtensions(ext_list)){
                shp_cnt+=1;
            }
        }
        return shp_cnt;
        
    }
    
    
    private boolean deleteDirectory(String dirname){
        if (dirname==null){
            return false;
        }
        File dir_obj = new File(dirname);
        if (!(dir_obj.exists())){
            return true;
        }
       String[]entries = dir_obj.list();
       for(String s: entries){
          File currentFile = new File(dir_obj.getPath(),s);
          currentFile.delete();
       }
       dir_obj.delete();
       return true;
    }
    
    /*
        Make a folder with the extracted files
        Except: separately rezip shapefile sets
    */
    private boolean rezipShapefileSets(){
        
        msgt("rezipShapefileSets");
        if (!containsShapefile()){
            msgt("There are no shapefiles to re-zip");
            return false;
        }else if(containsOnlySingleShapefile()){
            msgt("Original zip is good! Every file is part of a single shapefile set");
            return false;
        }
        
        deleteDirectory(rezippedFolder);
        if (!createDirectory(rezippedFolder)){
            errorMessage = "Failed to create rezipped directory: " + rezippedFolder;
        }
        
        Iterator<String> fileGroupsIterator = fileGroups.keySet().iterator();
        
        while(fileGroupsIterator.hasNext()){
            String key = fileGroupsIterator.next();
            msg("\n" + key);
            List<String> ext_list = fileGroups.get(key);
            msg(Arrays.toString(ext_list.toArray()));
        
            if (doesListContainShapefileExtensions(ext_list)){
                List<String> namesToZip = new ArrayList<String>();
                
                for (String ext : ext_list) {
                    namesToZip.add(key + '.' + ext);
                }
                String shpZippedName = rezippedFolder + "/" + key + ".zip";
                ZipMaker zip_maker = new ZipMaker(namesToZip, outputFolder, shpZippedName);
                // rezip it
                
                
            }else{
                for (String ext : ext_list) {
                    File source_file = new File(outputFolder + '/' + key + '.' + ext);
                    File target_file = new File(rezippedFolder + '/' + key + '.' + ext);
                   
                    File target_file_dir = target_file.getParentFile();
                    createDirectory(target_file_dir);
    
                   try{
                        Files.copy(source_file.toPath(), target_file.toPath(), REPLACE_EXISTING);    
                        msg("File copied: " + source_file.toPath() + " To: " + target_file.toPath());
                    }catch(java.nio.file.NoSuchFileException ex){
                        ex.printStackTrace(); 
                        
                        msgt("NoSuchFileException");
                        
                    }catch(IOException ex){
                        ex.printStackTrace(); 
                        
                        msgt("failed to copy");
                    }
                }
            }
        }
    
        return true;
    }
    
    
    public boolean containsOnlySingleShapefile(){
        if (containsShapefile()){
            if (fileGroups.size()==filesizeHash.size()){
                return true;
            }
        }
        return false;
    }
    
    /*
        Does this zip file contain a shapefile set?
    */
    public boolean containsShapefile(){
        Iterator<String> fileGroupsIterator = fileGroups.keySet().iterator();
        while(fileGroupsIterator.hasNext()){
            String key = fileGroupsIterator.next();
            //msg("\n" + key);
            List<String> ext_list = fileGroups.get(key);
            //msg(Arrays.toString(ext_list.toArray()));
            if (doesListContainShapefileExtensions(ext_list)){
                return true;
            }
        }
        return false;
    }
    
    
    /*
        Does a list of file extensions match those required for a shapefile set?
    */
    private boolean doesListContainShapefileExtensions(List<String> ext_list){
        if (ext_list == null){
            return false;
        }
        if (ext_list.containsAll(SHAPEFILE_MANDATORY_EXTENSIONS)){
            return true;
        }
        return false;
    }
    
    
    private void addToFileGroupHash(String basename, String ext){
        if ((basename==null)||(ext==null)){
            return;
        }
        List<String> extension_list = fileGroups.get(basename);
        if (extension_list==null) {
            extension_list = new ArrayList<String>();
        }
        extension_list.add(ext);
        fileGroups.put(basename, extension_list);
    }   // end addToFileGroupHash
    
    /**
     * Update the fileGroup hash which contains a { base_filename : [ext1, ext2, etc ]}
     * This is used to determine whether a .zip contains a shapefile set
     #
     * @param fname filename in String format
     */
    private void updateFileGroupHash(String fname){
        if (fname == null){
            return;
        }
             
        // Split filename into basename and extension.  No extension yields only basename
        //
        if (fname.toLowerCase().endsWith(SHP_XML_EXTENSION)){
            int idx = fname.toLowerCase().indexOf("." + SHP_XML_EXTENSION);
            if (idx >= 1){   // if idx==0, then the file name is ".shp.xml""
                String basename = fname.substring(0, idx);
                String ext = fname.substring(idx+1);
                addToFileGroupHash(basename, ext);
                return;
            }
        }
        
        String[] tokens = fname.split("\\.(?=[^\\.]+$)");
        if (tokens.length==2){
            String basename = tokens[0];
            String ext = tokens[1];
            //msg("basename: " + basename + " ext:" + ext);
            addToFileGroupHash(basename, ext);
        }
    } // end updateFileGroupHash
    
    
    
    
    
    /*
    
       @param fname .zip filename in String format
        
    */
    private boolean unzipFile(String filename){
        msgt("unzipFile: " + filename);

        if (filename==null){
            errorMessage = "No file name was given.  Please use a file with the .zip extension";            
            return false;
        }
        if (!filename.toLowerCase().endsWith(".zip")){
            errorMessage = "This file does not end with the .zip extension";
            return false;
        }
        File f = new File(filename);
        if (!f.exists()){            
            errorMessage = "The file does not exist: " + filename;            
            return false;
        }
        

        if (!createDirectory(outputFolder)){
            msg("Failed to create directory! " + outputFolder);
            return false;
        }
        
    try{
        ZipInputStream zip_stream = new ZipInputStream(new FileInputStream(filename));
        
        
         ZipEntry entry;
         byte[] buffer = new byte[2048];
    
          while((entry = zip_stream.getNextEntry())!=null){
              
              String zentry_file_name = entry.getName();
              
              // Skip files or folders starting with __
              if (zentry_file_name.startsWith("__")){
                  continue;
              }
              
                if (entry.isDirectory()) {
                    String dirpath = outputFolder + "/" + zentry_file_name;
                    createDirectory(dirpath);
                    
                    // Continue to next Entry
                    continue;       
                }
                String s = String.format("Entry: %s len %d added %TD",
                                entry.getName(), entry.getSize(),
                                new Date(entry.getTime()));
                filesListInDir.add(s);
                                                
                updateFileGroupHash(zentry_file_name);
                
                //msg(s);
                
                // Once we get the entry from the stream, the stream is
                // positioned read to read the raw data, and we keep
                // reading until read returns 0 or less.
                String outpath = outputFolder + "/" + entry.getName();
                FileOutputStream output = null;
                try{           
                    long fsize = 0;
                    output = new FileOutputStream(outpath);
                    int len = 0;
                    while ((len = zip_stream.read(buffer)) > 0){
                        output.write(buffer, 0, len);
                        fsize+=len;
                    } // end while
                    //msg("File size: " + fsize + " from zip:" + entry.getSize());
                    if (!(entry.getSize()== fsize)){
                        msg("different: " + fsize);
                        filesizeHash.put(zentry_file_name, fsize);  // Pull file size from actual unzipped file
                    }else{
                        filesizeHash.put(zentry_file_name, entry.getSize());    // Pull file size from .zip metadata
                    }
                }finally{
                    // we must always close the output file
                    if(output!=null) output.close();
                } // end try
            }
            if(zip_stream!=null) zip_stream.close();
            
            if (filesListInDir.size()==0){
                errorMessage = "No files in .zip: " + filename;
                return false;
            }
            
            zipFileProcessed = true;
            return true;
            
        }catch(FileNotFoundException ex){
            ex.printStackTrace(); 
            errorMessage = "The file was not found!  File name: " + filename;
            return false;
            
        }catch(ZipException ex){
                errorMessage = "ZipException File name: " + filename;
                msgt("ZipException");
                return false;
                
        }catch(IOException ex){
            //ex.printStackTrace(); 
            errorMessage = "IOException File name: " + filename;
            msgt("IOException");
            return false;
        }finally{
            // we must always close the zip file.
        }
        
    } // end unzipFile
    
} // end ZipFileMetadataExtractor