# Testing the hl7_batchzip endpoint via Java
This section provides a Java example of using the hl7_batchzip POST API. For manual testing with OpenApi or curl, see the above section "OpenApi/Swagger URL" (OpenApi Execute action will show the curl command).

**Notes:**
* This is just one example that shows the basics. Other utilities/frameworks may provide an easier way to invoke the API.
* A jax-rs implementation of imports is needed. Example: org.apache.cxf

```java
import java.io.ByteArrayInputStream;
import java.io.BufferedInputStream;
import java.io.FileInputStream;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.Entity;
import javax.ws.rs.client.Invocation;
import javax.ws.rs.core.GenericEntity;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.MultivaluedHashMap;
import javax.ws.rs.core.Response;

import org.apache.cxf.jaxrs.ext.multipart.MultipartBody;
import org.apache.cxf.jaxrs.ext.multipart.Attachment;
...
public void testHl7Batchzip2() throws Exception {
	// Precondition: the following services started at the URL below.
    String url = "http://localhost:5000/hl7_batchzip";
         
    // Build and run the POST API:
        
    Client client = ClientBuilder.newClient();
    Invocation.Builder reqBuilder = client.target(url).request()
     	// Add headers:
       	.accept(MediaType.APPLICATION_JSON)
       	.header("Content-Type", "multipart/form-data")
       	.header("tenant-id", "tenant-lp-eclipse-01"); // TODO: Update to your tenant-id value.
        
    // Build form data headers.
    MultivaluedHashMap<String, String> formDataHeaders = new MultivaluedHashMap<>();
    // TODO: update the "filename" to desired value. This is just a name and not the path to the file.
    formDataHeaders.add("Content-Disposition", "form-data; name=\"file\"; filename=\"testFile1-3.zip\"");
    formDataHeaders.add("Content-Type",  "application/x-zip-compressed"); 
        
    // TODO: Update FileInputStream input path the desired zip file.
	BufferedInputStream bis = new BufferedInputStream(new FileInputStream("testFile1-3.zip"));
	Attachment att = new Attachment(bis, formDataHeaders);
        
	// Build the data entity for the POST request.
    GenericEntity<MultipartBody> entity = new GenericEntity<>(new MultipartBody(att), MultipartBody.class);       
    Response response = reqBuilder.post(Entity.entity(entity, MediaType.MULTIPART_FORM_DATA_TYPE)); 
        
    int responseCode = response.getStatus();
       
    String content = response.readEntity(String.class);
    System.out.println("POST " + url + " results:" +
       	"\n- http response code = " + responseCode +
       	"\n- response data = " + content);
        
    response.close();      
}    
```